from langchain.llms import Databricks
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
import re
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from collections import namedtuple
## Text Splitting & Docloader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from langchain.document_loaders import TextLoader
## LLM Init
from langchain.retrievers import ContextualCompressionRetriever
from langchain.llms import Databricks
from langchain.embeddings import HuggingFaceBgeEmbeddings

from typing import Any, List, Mapping, Optional
import json
import hashlib
from pprint import pprint
from langchain.prompts import PromptTemplate
from datetime import datetime

import requests
import os

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM

from dbruntime.databricks_repl_context import get_context
import yaml 

with open('../../config.yml', 'r') as file:
    config_params = yaml.safe_load(file)
# this uses the current databricks environment to deploy as the user that ran the notebook
# NOTE: in a job the user is the one who created the job unless otherwise specified

os.environ['DATABRICKS_HOST'] = 'https://' + config_params['databricks_config']['databricks_host']
os.environ['DATABRICKS_TOKEN'] = config_params['databricks_config']['databricks_token']


class DatabricksLlama70b(LLM):
    endpoint_name: str = 'databricks-llama-2-70b-chat'
    max_tokens: int = 128
    temperature: float = 0.6

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        
        response = requests.post(
            url=f"{os.environ['DATABRICKS_HOST']}/serving-endpoints/{self.endpoint_name}/invocations",
            headers={'Authorization': f"Bearer {os.environ['DATABRICKS_TOKEN']}"}, 
            json={
                "messages": [
                    {
                    "role": "user",
                    "content": prompt
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
        )

        print({
            'reponse': str(response),
            'response.content': str(response.content)
        })

        return response.json()['choices'][0]['message']['content']

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "endpoint_name": self.endpoint_name,
            "max_tokens": self.max_tokens,
        }


class DatabricksMPT(LLM):
    endpoint_name: str = 'databricks-mpt-30b-instruct'
    max_tokens: int = 128
    temperature: float = 0.6
    verbose: bool = False

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        
        response = requests.post(
            url=f"{os.environ['DATABRICKS_HOST']}/serving-endpoints/{self.endpoint_name}/invocations",
            headers={'Authorization': f"Bearer {os.environ['DATABRICKS_TOKEN']}"}, 
            json={
                "prompt": prompt,
                "max_tokens": self.max_tokens
            }
        )
        if self.verbose:
            print(response)
            print(response.content)

        return response.json()['choices'][0]['text']

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "endpoint_name": self.endpoint_name,
            "max_tokens": self.max_tokens,
        }


class DatabricksMixtral(LLM):
    endpoint_name: str = 'databricks-mixtral-8x7b-instruct'
    max_tokens: int 
    temperature: float 
    verbose: bool = False

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        
        response = requests.post(
            url=f"{os.environ['DATABRICKS_HOST']}/serving-endpoints/{self.endpoint_name}/invocations",
            headers={'Authorization': f"Bearer {os.environ['DATABRICKS_TOKEN']}"}, 
            json={
                "messages": [
                    {
                    "role": "user",
                    "content": prompt
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
        )

        if self.verbose:
            print({
                'reponse': str(response),
                'response.content': str(response.content)
            })

        return response.json()['choices'][0]['message']['content']

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "endpoint_name": self.endpoint_name,
            "max_tokens": self.max_tokens,
        }









    

