import os
import streamlit as st
from annotated_text import annotated_text
import pandas as pd
import plotly.express as px
import textwrap
import base64
import yaml
import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
import vertexai
from src.data_processing.data_extraction import *
from src.utils.utils import *

st.set_page_config(layout="wide")

#Read Config File
with open('config.yml', 'r') as file:
    config_params = yaml.safe_load(file)

if not check_password():
   st.stop()  # Do not continue if check_password is not True.

#pdf directory with transcripts
pdf_loc = config_params['pull_report']['dbfs_pdfs_dir'].replace('dbfs:', '/dbfs')


# Del duplicate directories 
del_dir(os.path.abspath('pdf'))
del_dir(os.path.abspath('files'))

# Create directories to upload and read files
pdf_dir = create_dir('pdf')
llm_response_dir = create_dir('files')


# Databricks Path where Earning call transcripts are saved
dbfs_pdfs_dir = config_params['pull_report']['dbfs_pdfs_dir']
# Databricks Path where llm generated reports are saved
reports_dir = config_params['pull_report']['reports_dir']

#get path of pdf transcripts in dbfs directory
pdf_files = get_pdf_files(dbfs_pdfs_dir)
#extract company name
company_name = extract_company_names(pdf_files, pdf_loc)

#copy pdf transcripts from dbfs to local dir 
dbfs_to_local_dir_sync(reports_dir, pdf_dir)
#copy llm generated reports from dbfs to local dir
dbfs_to_local_dir_sync(dbfs_pdfs_dir, llm_response_dir)

path_copy = os.listdir(pdf_dir)


st.title('IR Report')
st.divider()

st.subheader("IR Overview")
#dropdown to toggle betwwen company name
#company_name = company_name[:5]
cmpny = st.selectbox('Company Name', company_name)
company_name = []
company_name.append(cmpny)

#get path for llm generated report's for report overview section
pdf_results = [f for f in path_copy if 'IR_Report.csv' in f and company_name[0] in f]
print('\n\n\n\n\njksdhbvjhsdbf', pdf_results)
pdf_results = os.path.join(pdf_dir, pdf_results[0])

#read and display reports
df = pd.read_csv(pdf_results)

#select box to toggle between overview categories
ct = ["Summary", "Revenue growth drivers and challenges", "Margin performance and expense management", "Earnings quality and nonGAAP metrics",
"Capital allocation and cash flow", "Guidance and forwardlooking statements", "Conclusion"]
ctype = st.selectbox("Category", ct)
if ctype == "Summary":

   annotated_text(
   ("Summary", "A brief overview of the company's financial performance during the quarter, highlighting key metrics such as revenue, net income, and earnings per share."))
   st.markdown(df['Summary'][0].replace('$', "\$"))

elif ctype == "Revenue growth drivers and challenges":
    
   annotated_text(
   ("Revenue growth drivers and challenges", "The revenue growth drivers and challenges of the company"))
   st.markdown(df['Revenue growth drivers and challenges'][0].replace('$', "\$"))

elif ctype == "Margin performance and expense management":
   annotated_text(
   ("Margin performance and expense management", "The margin performance and expense management of the company."))
   st.markdown(df['Margin performance and expense management'][0].replace('$', "\$"))

elif ctype == "Earnings quality and nonGAAP metrics":
   annotated_text(
   ("Earnings quality and nonGAAP metrics", "The company's earnings quality and non-GAAP metrics."))
   st.markdown(df['Earnings quality and nonGAAP metrics'][0].replace('$', "\$"))

elif ctype == "Capital allocation and cash flow":
   annotated_text(
   ("Capital allocation and cash flow", "The company's capital allocation and cash flow."))
   st.markdown(df['Capital allocation and cash flow'][0].replace('$', "\$"))

elif ctype == "Guidance and forwardlooking statements":
   annotated_text(
   ("Guidance and forwardlooking statements", "Guidance and forward-looking statements for the company."))
   st.markdown(df['Guidance and forwardlooking statements'][0].replace('$', "\$"))

elif ctype == "Conclusion":
   annotated_text(
   ("Conclusion", "A summary of your analysis, including a rating or recommendation on the company's stock based on your assessment of its financial outlook."))
   st.markdown(df['Conclusion'][0].replace('$', "\$"))

#Chatbot Section

#get earnings call transcript path  
path_llm = os.listdir(llm_response_dir)
pdf_results_llm = [f for f in path_llm if company_name[0] in f]
path_llm = os.path.join(llm_response_dir, pdf_results_llm[0])

#get earnings call transcript path  
text_llm = extract_text_qa(path_llm)
#format documents  
doc_split_llm = preqa_split(text_llm)
#remove disclaimers 
doc_llm = preqa_remove_disclaimer(doc_split_llm)
st.title("IR Chat")
colored_header(label='', description='', color_name='gray-30')

# Initializing Vertex AI
vertexai.init(project="projectname", location="us-central1")

# Initialize session state variables
if 'something' not in st.session_state:
 st.session_state.something = ''
input_container = st.container()
response_container = st.container()
#Toggle text input on submit 
def submit():
   st.session_state.something = st.session_state.widget
   st.session_state.widget = ''
# Capture user input and display bot responses

user_input = st.text_input('You: ', "", key='widget', on_change=submit)
user_input = st.session_state.something
print('werwer', user_input)
#pass formatted text as context to the llm prompt
with response_container:
   if user_input:
      print('enter')
      temp = p_chat_preqa.format(BODY1 = user_input, BODY2 = doc_llm) 
      model_max_tokens = 32768
      token_est = int(len(temp)/2)
      call_max_tokens = model_max_tokens - token_est
      response = llm(temp, call_max_tokens)
      response = response.replace('$', "\$")
      message(user_input, avatar_style="icons")
      message(response, avatar_style="icons")
      st.session_state.something = ''

   else:
      message('How can I help you?',   avatar_style="icons")

with input_container:
    display_input = user_input


#tabs to toggle between report gen section
tab1, tab2, tab3 = st.tabs(["Question and Answer Section", "Management Discussion Section", "Sentiment Highlight"])
with tab1:
   @st.cache_data
   def load_data(path):
      df_qa = pd.read_csv(path)
      return df_qa
   
#llm output for the question and answer section
   pdf_results = [f for f in path_copy if 'QA_Report.csv' in f and company_name[0] in f]
   pdf_results = os.path.join(pdf_dir, pdf_results[0])

#filter by llm generated importance score for redundant q&a    
   df_qa = load_data(pdf_results)
   df_qa = df_qa[df_qa['Importance Score'] >= 7]
   df_qa = df_qa[df_qa['Label'].str.strip() != 'Introduction']


   df_qa = df_qa[['Sentences Question', 'Summary Answer', 'Importance Highlight', 'Label']]
   selected_category = st.selectbox("Select Category", df_qa['Label'].unique())
   df_qa = df_qa[df_qa['Label'] == selected_category]

#Display responses by topic
   true_html = '<input type="checkbox" checked disabled="true">'
   false_html = '<input type="checkbox" disabled="true">'
   df_qa['D'] = True
   df_qa['D'] = df_qa['D'].apply(lambda b: true_html if b else false_html)
   df_qa = df_qa[['Sentences Question', 'Summary Answer', 'Importance Highlight', 'Label']]
   df_qa = df_qa.rename(columns = {'Sentences Question' : 'Question', 'Summary Answer' : 'Answer Summary', 'Label' : 'Category'})
   st.markdown(df_qa.to_html(escape=False), unsafe_allow_html=True)

with tab2:
#llm output for the management discussion section
   pdf_results = [f for f in path_copy if "PreQA_Sentiment.csv" in f and company_name[0] in f]
   pdf_results = os.path.join(pdf_dir, pdf_results[0]) 

# Use the native Plotly theme.
   df_preqa = pd.read_csv(pdf_results)
   fig = px.bar(df_preqa, x="Category", y="score", color="Label", custom_data=[['<br>'.join(textwrap.wrap(str(x), width=180)) for x in df_preqa['Reasoning']], df_preqa['Label'], ['<br>'.join(textwrap.wrap(str(x), width=180)) for x in df_preqa['Paragraph']]], color_discrete_map = {'Positive': '#008000', 'Negative': '#FF0000', 'Neutral': '#0000FF'})
   fig.update_traces(hovertemplate='Sentiment:%{customdata[1]}<br>Paragraph:%{customdata[2]}<br>Reasoning:%{customdata[0]}', textposition='inside', textfont_size=5, marker_line_color = 'black', hoverlabel = dict(align = 'left'))
   st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab3:
#llm output for the pdf highlight section
   pdf_results = [f for f in path_copy if '.pdf' in f and company_name[0] in f]
   pdf_results = os.path.join(pdf_dir, pdf_results[0]) 
   def ViewPDF(wch_fl):
    with open(wch_fl,"rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="1500" height="1000" type="application/pdf">' 
        st.markdown(pdf_display, unsafe_allow_html=True)
   ViewPDF(pdf_results)