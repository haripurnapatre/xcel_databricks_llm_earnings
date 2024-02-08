# Databricks notebook source
pip install PyPDF2 databricks-genai-inference langchain-core transformers pymupdf

# COMMAND ----------

import os
pdf_dir = 'dbfs:/investor_relations/q3_earnings_call_pdfs/'
current_dir = os.getcwd()
dbutils.fs.cp(pdf_dir, current_dir, recurse = True)

# COMMAND ----------

pdf_dir = '/dbfs/investor_relations/q3_earnings_call_pdfs/'
pdf_files = [pdf_dir + f for f in os.listdir(pdf_dir) if '.pdf' in f]
pdf_files
