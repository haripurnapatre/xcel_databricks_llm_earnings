from tqdm import tqdm
from src.llm_setup.experiment_utils import *
from src.data_processing.data_format import *
from src.data_processing.data_extraction import *
from src.llm_setup.prompt import *
import requests 
import os
from typing import List
from typing import Dict

def generate_report(formatted_txt: List[str], p_overview: str, company: str) -> List[str]:
    """
    Generates a report by iterating through a list formatted text prompts, using a provided llm and p14 format string.

    Args:
        formatted_txt (list): A list of formatted text prompts to be inputed into the llm
        p_overview (string): A string format to be used as a parameter for llm
        company (string): The name of the company

    Returns:
        ans_comb (list): A list of answers generated by the function using the given formatted text prompts
    """

    # Initialize variables
    answer = ''
    j = 0
    ans_comb = []
    
    # Iterate through prompts and generate answers using llm and p_overview
    for i in tqdm(formatted_txt):
        j= j+1
        print(j)
        
        # Reset answer if first prompt in loop, else use previous value
        if j == 1:
            answer = ''
        else:
            answer = answer
        
        # Use p_overview to format prompt text
        temp = p_overview.format(BODY = i, company = company) 
        model_max_tokens = 32768
        token_est = model_max_tokens - int(len(temp)/2)
        llm = DatabricksMixtral(max_tokens=token_est, temperature=0.4, verbose = True)
        
        # LLM Call to generate report
        answer = llm(temp)
        answer = str(answer).strip()
        answer = remove_repeat(answer)
        answer = answer.replace('-', '')
        answer = answer.replace('null', '"No Specific Information provided in context"')
        ans_comb.append(answer)
        print('-----------------------------------------------------')
        print(answer)
    return ans_comb

def summarize_response(final_report: Dict[str, List[str]], p_summary: str) -> Dict[str, str]:
    """
    Summarizes the final report using a given summary template.

    Args:
    - final_report (dict[str, List[str]]): A dictionary containing the final report information.
    - p_summary (str): The summary template to be used.

    Returns:
    - dict[str, str]: A dictionary containing the summarized report.

    """
    xcel_report = {}
    # iterate over keys in final_report dictionary
    for i in final_report.keys():
        # join the list of sentence strings to form a single string
        cntxt = ' '.join(final_report[i])
        model_max_tokens = 32768
        token_est = model_max_tokens - int(len(cntxt)/2)
        llm = DatabricksMixtral(max_tokens=token_est, temperature=0.4)
        # generate concise summary and save in xcel_report
        if i.lower() == 'summary':
            concise_summary_1 = llm(p_summary_overview.format(BODY = cntxt))
        else:
            concise_summary_1 = llm(p_summary.format(BODY = cntxt))
        xcel_report[i] = concise_summary_1
        # print summary of the context data
        print(i,'',concise_summary_1)
    return xcel_report

def llm_preqa(results: pd.DataFrame, llm, p_preqa: str) -> List:
    """
    Apply LLM to preprocess sentences and generate predicted sentiment.

    Args:
        results (DataFrame): The DataFrame containing the sentences and labels.
        llm (Model): The LLM model used for preprocessing.
        p_preqa (str): The template for formatting the sentences.

    Returns:
        List[str]: The list of predicted sentiment for each sentence.
    """
    final_ans = []
    for j, i in enumerate(results['sentence']):
        # Print current sentence number and its Label.
        print(j, results['Label'].iloc[j])
        # Format the current sentence and Label using prompt "p_preqa".
        temp = p_preqa.format(BODY1 = i.replace('\n', ' '), BODY2 = results['Label'].iloc[j]) 
        # Generate predicted sentiment using LLM.
        answer = llm(temp)
        # Append predicted sentiment to final_ans list.
        final_ans.append(answer)
        # Print predicted sentiment.
        print(answer)
    return final_ans

def llm_qa(comb_text: List, p_qa : str) -> List:
    """
    Perform a QA (Question-Answer) operation on a list of text using a given template.

    Args:
        comb_text (List[str]): A list of text to perform the QA operation on.
        p_qa (str): The template to use for the QA operation, with a placeholder for the text.

    Returns:
        List[str]: A list of answers for each input text.

    """

    # Create an empty list to store the final answers
    final_ans = []

    # Iterate over the combined text
    for j, i in enumerate(comb_text):

        # Format the template with the current text
        temp = p_qa.format(BODY1=i) 

        # Estimate the number of tokens in the formatted template
        token_est = int(len(temp)/2)

        # Invoke the QA operation using the formatted template and token estimate
        answer = llm_qa_invoke(temp, token_est)

        # Append the answer to the final answer list
        final_ans.append(answer)

        # Print the answer
        print(answer)

    # Return the final answer list
    return final_ans