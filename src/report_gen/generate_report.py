# Databricks notebook source
pip install PyPDF2 databricks-genai-inference langchain-core transformers pymupdf

# COMMAND ----------

from src.report_gen.report_gen_func import *
import yaml

# COMMAND ----------

with open('../../config.yml', 'r') as file:
    config_params = yaml.safe_load(file)

# COMMAND ----------

pdf_dir = config_params['pull_report']['dbfs_pdfs_dir'].replace('dbfs:', '/dbfs')
pdf_files = [pdf_dir + f for f in os.listdir(pdf_dir) if '.pdf' in f]
company_name = extract_company_names(pdf_files, pdf_dir)

# COMMAND ----------

model_names = [
    "ProsusAI/finbert",
    "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    "yiyanghkust/finbert-tone",
    "soleimanian/financial-roberta-large-sentiment"
    ]

# COMMAND ----------

ir_overview_report(pdf_files, company_name, p_overview, p_summary)

# COMMAND ----------

preqa_report(pdf_files, company_name, model_names, p_preqa)

# COMMAND ----------

qa_report(pdf_files, company_name, p_qa)

# COMMAND ----------

highlight_pdf(pdf_files, company_name, model_names)
