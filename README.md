# LLM_Earnings_Call

## Name
Earnings Call Dashboard (Mixtral)

## Data
Publically available earnings call transcript data.

## LLM Model Used

Databricks Pay-per-token Mixtral API : https://docs.databricks.com/en/machine-learning/foundation-models/index.html

![Mixtral](/imgs/mixtral.PNG)

## Description
Generate Informative dashboards based on the most recent transcript of an earnings call in the calendar quarter and are typically made public 3 hours after the call. 
The Dashboard consists of 5 sections :
1. Report Overview Section(Report Generation using llm context refinement) -  A brief overview of the company's financial performance during the quarter, highlighting key metrics such as revenue, net income, earnings per share, and capital allocation.
2. Chatbot - Chatbot to ask questions about the company's earnings call.
3. Question and Answer Section(Topic Modeling and Q&A Extraction using LLM) -  Question and Answer's asked in the call along with important highlights segmented by topic.  
4. Management Discussion Section(Sentiement Analysis and Reasoning using LLM) - Sentiement Analysis with reasoning, based on the management discussion section of the call.   
5. Transcript Highlight - Sentiment based highlighting on the earnings call transcript pdf files.   


## Visuals
* Report Overview Section (**LLM GENERATED CONTEXT REFINEMENT**)

![Report Overview Section](./imgs/ir_report.PNG)

* Chatbot (**RAG CHATBOT**)

![Chatbot](./imgs/ir_chat.PNG) 

* Question and Answer Section (**LLM GENERATED TOPIC MODELING AND Q&A EXTRACTION**)

![Question and Answer Section](/imgs/ir_qa.PNG) 

* Management Discussion Section (**LLM GENERATED SENTIMENT ANALYSIS**)

![Management Discussion Section](./imgs/ir_md.PNG)

* Transcript Highlight

![Transcript Highlight](/imgs/ir_highlight.PNG)

## Project Plan

1. Report Overview (**LLM GENERATED CONTEXT REFINEMENT**)

  * Split PDF into chunks.

  * Create prompt to output report in a JSON format based on following categories : (Summary, Revenue growth drivers and challenges, Margin performance and expense management, Earnings quality and non-GAAP metrics, Capital allocation and cash flow, Guidance and forward-looking statements, Conclusion)

  ![Prompt](/imgs/p_overview.PNG)

  ![Prompt_Response](/imgs/ir_1.PNG)

  * Loop through the JSON outputs and combine responses across all the individual categories (example shown only for the first two chunks of the summary category)
  
  ![Comb_Responses](/imgs/ir_report_2.PNG)

  * Create a summary Prompt to summarize the combined response across each category.

  ![Final_Summary](/imgs/ir_report_3.PNG)
  
  * Save as csv.

2. Chatbot (**RAG CHATBOT**)
  * Format PDF to remove disclaimers.
  * Remove Q&A section due to information overlap.
  * Pass entire PDF as context leveraging mixtral's large token length.

3. Question and Answer Section (**LLM GENERATED TOPIC MODELING AND Q&A EXTRACTION**)

  * Extract Question and Answer section from the PDF.

  * Generate LLM Prompt (JSON Response) to extract question & answer pairs and assign categories along with importance scores based on the question asked.
  
  ![QA_Prompt](/imgs/ir_qa_1.PNG)

  * Loop through the JSON response and filter out q&a pairs with low scores.   

  ![QA_Response](/imgs/ir_qa_2.PNG)

  * Save as csv.

  ![QA_CSV](/imgs/ir_qa_3.PNG)

4. Management Discussion Section (**LLM GENERATED SENTIMENT ANALYSIS**)

  * Extract Management Discussion section from PDF.  

  * Calcualted Sentiment Score using sentiment analysis models : finbert, distilbert and roberta 

  ![MD_Sentiment](/imgs/ir_md_1.PNG)

  * Ensemble Sentiment Score to get accurate sentiment values.

  ![MD_SentimentEnsemble](/imgs/ir_md_2.PNG)


  * Generate LLM prompt (JSON Response) to use existing sentiment and paragraph to come up with a Category and Reasoning behind the sentiment. 

  ![MD_Prompt](/imgs/ir_md_3.PNG)

  * Save as csv.

  ![MD_CSV](/imgs/ir_md_4.PNG)

5. Transcript Highlight

 * Creating bounding boxes in PDF and extract text using Fitz library.
 * Split text into sentences.
 * Caluclate sentence wise sentiment and highlight text in PDF based on sentence sentiment.    
 * Save as csv.

## Installation
1. Clone repo. (git clone https://gitlab.com/xcel-master/data_science/llm_earnings_call.git)

2. Set variables in config.yml and commit the changes to git.

   ![CNFG_SETUP](/imgs/config_2.PNG)

3. Pip Install requirements.txt (pip install -r requirements.txt)

4. Run report_gen_job.py (python report_gen_job.py)

   Check Job Run on UI and wait for Status : Succeeded

   ![JOB_RUN](/imgs/job_run.PNG)

5. Run app.py using streamlit to load frontend (streamlit run app.py).

   ![UI](/imgs/UI.PNG)


## Authors and acknowledgment

Hari Purnapatre : hari.k.purnapatre@xcelenergy.com

Blake Kleinhans: blake.e.kleinhans@xcelenergy.com


