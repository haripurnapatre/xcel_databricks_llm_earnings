import os
import base64
import requests
import re
import yaml
import streamlit as st
import hmac

import fitz
from databricks.sdk import WorkspaceClient

with open('config.yml', 'r') as file:
    config_params = yaml.safe_load(file)

#Setup Environment Variables with config.yaml
os.environ['DASHBOARD_PASSWORD'] = config_params['databricks_config']['password']
os.environ['DATABRICKS_HOST'] = config_params['databricks_config']['databricks_host']
os.environ['DATABRICKS_TOKEN'] = config_params['databricks_config']['databricks_token']
w = WorkspaceClient()

#Prompt for IR Chat
p_chat_preqa = """<s>[INST] <<SYS>>
We have provided text from a report of the quarterly earnings call transcript for [Company Name] and We have the opportunity to give an answer for the question asked based on the provided text.
<</SYS>>
[/INST]
</s>


<s>[INST]  
Answer the question based on the provided text
question: {BODY1}
provided text: {BODY2}
[/INST]"""


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], os.environ['DASHBOARD_PASSWORD']):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

#Get path for transcipt PDF's on databricks
def get_pdf_files(dbfs_pdfs_dir):
   return [f.path for f in w.dbutils.fs.ls(dbfs_pdfs_dir) if '.pdf' in f.path]

#Copy transcript PDF's from databricks to local directory
@st.cache_data
def dbfs_to_local(
    dbfs_file_path, 
    local_dir = '.', 
    MAX_BYTES = 1048576,
):
    """
    Uses the Databricks REST API to download a file from DBFS

    Args:
    dbfs_file_path (str): DBFS file path "dbfs:/FileStore/my/dbfs/file.csv"
    local_dir (str): local directory where we want the file copied to
    MAX_BYTES (int): default to 1048576 (1MB), this is the max chunk size allowed by the api
    """
    file_name = dbfs_file_path.split('/')[-1]
    local_file_path = f'{local_dir}/{file_name}'

    response_length = MAX_BYTES
    chunk_i = 0

    # delete file if exists because we want to overwrite
    if os.path.exists(local_file_path):
        os.remove(local_file_path)

    with open(local_file_path, 'wb') as local_file:

        while response_length == MAX_BYTES:
            response = requests.get(
                url=f"https://{os.environ['DATABRICKS_HOST']}/api/2.0/dbfs/read",
                headers={'Authorization': f"Bearer {os.environ['DATABRICKS_TOKEN']}"}, 
                json={
                    "path": dbfs_file_path, 
                    "offset": chunk_i*MAX_BYTES,
                    "length": MAX_BYTES
                }
            )

            response_obj = response.json()

            response_length = response_obj['bytes_read']
            chunk = response_obj['data']

            local_file.write(base64.b64decode(chunk))
            chunk_i = chunk_i+1

    return local_file_path

@st.cache_data
def dbfs_to_local_dir_sync(dbfs_dir, local_dir):
    """
    Copies the contents of a DBFS folder to a local folder, if the files already exist compare
    modification time and only overwrite local files if the DBFS file was created after our last 
    fetch
    
    Args:
    dbfs_dir (str): folder on dbfs that you want to copy "dbfs:/FileStore/my/dbfs/dir"
    local_dir (str): local folder where you want the files copied to "./my/local/dir"
    """
    print({'dbfs_dir': dbfs_dir, 'local_dir': local_dir})
    dbfs_files = w.dbutils.fs.ls(dbfs_dir)

    for dbfs_file in dbfs_files:
        local_file_path = f'{local_dir}/{dbfs_file.name}'
        print({'local_file_path': local_file_path})
        if not os.path.exists(local_file_path) or os.path.getmtime(local_file_path) < dbfs_file.modificationTime/1000:
            dbfs_to_local(
                dbfs_file.path,
                local_dir
            )

def create_dir(folder_name):
    if not os.path.exists(folder_name):
       os.mkdir(folder_name)

    return os.path.abspath(folder_name)
@st.cache_data
def del_dir(pdf_dir):
    if os.path.isdir(pdf_dir):
        for filename in os.listdir(pdf_dir):
            os.remove(os.path.join(pdf_dir, filename))
        os.rmdir(pdf_dir)

#mixtral endpoint call
def llm(prompt, max_token):
    response = requests.post(
            url=f"https://{os.environ['DATABRICKS_HOST']}/serving-endpoints/databricks-mixtral-8x7b-instruct/invocations",
            headers={'Authorization': f"Bearer {os.environ['DATABRICKS_TOKEN']}"}, 
            json={
                "messages": [
                    {
                    "role": "user",
                    "content": prompt
                    }
                ],
                "max_tokens": max_token,
                "temperature": 0
            }
        )
    return response.json()['choices'][0]['message']['content']