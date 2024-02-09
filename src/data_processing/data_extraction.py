import ast
from tqdm import tqdm
import re
from transformers import pipeline
import pandas as pd
import requests
import os 
import fitz
from typing import List
from typing import Dict

def remove_disclaimer(ans_comb: List[str]) -> List[str]:
    """
    This function cleans up the ans_comb argument by removing disclaimer texts, or texts
    that conveys the model's inability to output a proper answer to the given text body.

    Parameters:
    ans_comb (List[str]): A list containing response texts generated by the language model.
    
    Returns:
    cleaned_chunks (List[str]): A list containing response chunks that are devoid of any disclaimer texts.
    """
    cleaned_chunks = []
    for i in ans_comb:
        # Check if the text contains specific phrases indicating a disclaimer
        if (i.lower().find('sorry') != -1) or (i.lower().find("give a brief overview of the company's financial performance during the quarter") != -1) or (i.lower().find("give a brief overview of the company's financial performance during the quarter") != -1) or (i.lower().find("identify the company's revenue growth drivers and challenges")!= -1) or ((i.lower().find("outline")!= -1)) or ((i.lower().find("cannot analyze")!= -1)):
            continue
        else:
            cleaned_chunks.append(i)
    return cleaned_chunks        

def get_prompt_elements(prompt_t: str) -> dict:
    """
    This function reads a given prompt and extracts the key elements. 
    The function searches for { and } symbols in the text and uses ast.literal_eval to 
    convert the text into return an eval'd object. If the brackets are not found, it searches
    for the word "Conclusion" (assuming that is where the key elements are provided) to extract 
    the key elements in between statements starting with "Summary:" and ending with Statement:.
    
    Args:
    - prompt_t: A string representing the prompt.

    Returns:
    - A dictionary representing the extracted key elements from the prompt.
    """
    # Check if curly brackets are present in the prompt_t
    if prompt_t.find('}') <= 0:
        # If curly brackets are not found, search for the word "Conclusion"
        start_index = prompt_t.find('Conclusion')
        end_index = prompt_t.find('\n', start_index)
        # Extract the key elements between "Summary:" and "Statement:"
        start_index = prompt_t.find('{')
        prompt = ast.literal_eval(prompt_t[start_index:end_index] + '"' +'}')
        return prompt
    else:
        # If curly brackets are found, extract the key elements between them
        start_index = prompt_t.find('{')
        end_index = prompt_t.find('}')+1
        prompt = ast.literal_eval(prompt_t[start_index:end_index])
        
        return prompt

def get_prompt_elements_format(i: str) -> dict:
    """
    Returns a dictionary of prompt elements obtained from a given string parameter.

    Args:
    i (str): A string representing the prompt elements.

    Returns:
    dict: A dictionary of prompt elements.
    """
    # Check if the string contains '}'
    if i.find('}') != -1:
        # Extract the substring starting from 'Summary'
        i = i[ i.find('Summary'):]

        # Create a comma-separated string of the elements in the substring
        ans = ", ".join([f"{j}" for j in i.split('\n')])

        # Create a new string with '{' and a newline followed by the comma-separated elements
        i = '{' + '\n' + ans 

        # Convert the new string into a dictionary using ast.literal_eval()
        i = ast.literal_eval(i)

        # Return the dictionary of prompt elements
        return i
    else:
        # Extract the substring starting from 'Summary'
        i = i[ i.find('Summary'):]

        # Create a comma and newline-separated string of the elements in the substring
        ans = ", \n".join([f"{j}" for j in i.split('\n')])

        # Create a new string with '{', a newline, double quotes, and the comma-separated elements
        i = f"{{\n\"{ans}\n}}"

        # Convert the new string into a dictionary using ast.literal_eval()
        i = ast.literal_eval(i)

        # Return the dictionary of prompt elements
        return i

def extract_data(cleaned_chunks) -> List[str]:
    """
    This function extracts summary context from cleaned chunks.
    It loops through the cleaned chunks and attempts to get the prompt elements from each chunk.
    When calling the 'get_prompt_elements' function on the current chunk is unsuccessful, it calls
    the 'get_prompt_elements_format' function instead. Finally, summary context is stored in the
    'summary_cntxt' list and returned.
    
    Args:
        cleaned_chunks (List[str]): A list of cleaned chunks.

    Returns:
        List[str]: A list of summary context extracted from cleaned chunks.
    """
    summary_cntxt = []
    for j,i in enumerate(cleaned_chunks):
        print(i,j)
        try:
            summary_cntxt.append(get_prompt_elements(i))
        except:
            try:
                summary_cntxt.append(get_prompt_elements_format(i))
            except:
                continue
    return summary_cntxt


def combine_extract(summary_cntxt: List[Dict[str, str]]) -> Dict[str, List[str]]:
    """
    Combines extracted summary context into a final report dictionary, where each key represents 
    a feature and the corresponding value is a list of values for that feature from the given list of
    summary_cntxt.
    
    Args:
    summary_cntxt (list of dictionaries): List of extracted summary context where each dictionary 
    represents a 'summary' object
    
    Returns:
    final_report (dictionary): A dictionary where each key represents a feature and the corresponding 
    value is a list of values for that feature from the given list of summary_cntxt.
    """
    
    summary_comb = ''
    final_report = {}
    
    # Get all keys from first dictionary of summary_cntxt and create a dictionary as a placeholder for final report
    keys = [i for i in summary_cntxt[0].keys()]
    final_report = {keys:[] for keys in summary_cntxt[0]}
    
    # Loop through each dictionary in summary_cntxt and combine values from different features
    for i in tqdm(summary_cntxt):
        for j in i.keys():
            # if (bool(re.search('.*not.*provided.*transcript.*' , i[j].lower())) or bool(re.search('.*not.*mentioned.*transcript.*' , i[j].lower())) or bool(re.search('.*not.*provide.*transcript.*' , i[j].lower())) or bool(re.search('.*not.*discussed.*transcript.*' , i[j].lower())) or bool(re.search('.*not.*provided.*context.*' , i[j].lower())) 
            # or bool(re.search('.*not.*mentioned.*context.*' , i[j].lower())) or bool(re.search('.*not.*provide.*context.*' , i[j].lower())) or bool(re.search('.*not.*discussed.*context.*' , i[j].lower())) or bool(re.search('.*not.*information.*context.*' , i[j].lower())) or bool(re.search('.*not.*information.*transcript.*' , i[j].lower())) or bool(re.search('.*not.*margin.*performance.*' , i[j].lower())) or bool(re.search('.*not.*earnings.*quality.*' , i[j].lower())) or bool(re.search('.*not.*capital.*allocation.*' , i[j].lower())) or bool(re.search('.*not.*guidance.*statements.*' , i[j].lower())) or bool(re.search('.*not.*growth.*drivers.*' , i[j].lower()))) and (not bool(re.search('.*however.*', i[j].lower()))):
            #     i[j] = ''
            summary_comb += i[j] + ''
            final_report[j].append(i[j])
            print(final_report)
            
    return final_report

def extract_text_qa(path):
    """
    This function takes a filepath and uses the fitz module to extract text from each page of a PDF file.
    It then takes only the text blocks and appends them to a list.
    
    Args:
    path (str): The path that contains the PDF file to read.
    
    Returns:
    list: A list of the extracted text blocks.
    """
    # initialize an empty list to store the extracted text
    text = [] 
    # open the PDF document using fitz
    doc = fitz.open(path) 
    # iterate through each page in the document
    for page in doc: 
        # extract the text blocks from the page
        output = page.get_text("blocks") 
        # initialize a variable to mark the block id
        previous_block_id = 0 
         # iterate through each block in the extracted output
        for block in output:
            # check if the block is a text block
            if block[6] == 0: 
                # append the text to the list
                text.append(block[4]) 
    return text


def preqa_split(text) -> List:
    """
    This function takes a list of strings and split it into a list of strings from the page with the presentation to the page with the Question and Answer only
    
    Args:
    text (list): The list of strings to split

    Returns:
    result (list): The list of strings of the pages containing the presentation through to the Question and Answer section only
    
    """
    count = 0
    start_ind = 0
    end_ind = 0
    
    # Find the starting index of the presentation section
    
    for j,i in enumerate(text):
        if re.search(r'Presentation\n', i) and len(i) <= len('Presentation\n'):
            start_ind = j
            break
            
    # Find the ending index of the presentation section
    
    for j,i in enumerate(text):
        if re.search(r'.*Question and Answer\n.*', i) and len(i) <= len('Question and Answer\n'):
            end_ind = j
    
    # Extract the text between the indices start_ind and end_ind
    text = text[start_ind:end_ind]   
    return text



def preqa_remove_disclaimer(text: List) -> List:
    """
    This function processes a list of strings and removes sentences that contain
    any of a pre-determined set of keywords that point to disclaimers, irrelevant
    or redundant documentation from an earnings call transcription 

    Args:
    text (list): A list of strings to process

    Returns:
    sentiment list(str): A refined list of the original list with the "disclaimer" strings removed
    """

    sentiment = []
    for i in text:
        # Use of regex to check for disclaimer keywords to exclude
        # and ensure that length is greater than a threshold
        if (re.search(r'.*all rights.*', str(i).lower().strip()) or
            len(i.strip()) < 50 or
            re.search(r'.*2023 earnings call.*', str(i).lower().strip()) or
            re.search(r'.*s&p.*', str(i).lower().strip()) or
            re.search(r'.*market intelligence.*', str(i).lower().strip()) or
            re.search(r'.*Presentation.*', str(i).lower().strip()) or
            re.search(r'.*Operator.*', str(i).lower().strip()) or
            re.search(r'.*marketintelligence.*', str(i).lower().strip()) or
            re.search(r'.*copyright.*', str(i).lower().strip())):
            # i is discarded if it meets any of the above conditions above
            continue 
        else:
            # Unwanted strings have been eliminated, so add any accepted strings to a new list for further processing
            sentiment.append(i.strip())  
    return sentiment


def sentiment_analysis(model_names: List[str], sentiment: List[str]) -> pd.DataFrame:
    """
    This function processes a list of strings (sentiment) using various pre-trained models and returns a pandas dataframe with the 
    sentiment score and sentiment label for each string
    
    Args:
        model_names (List[str]): A list of pre-trained BERT/Transformer models to use for the sentiment analysis
        sentiment (List[str]): A list of strings to process
    
    Returns:
        results_2 (pd.DataFrame): A pandas dataframe with the sentiment score and sentiment label for each string
    """
    results = [] 
    for model_name in model_names:
        # Load model
        print(f'Loading {model_name}...')
        sentiment_model = pipeline("text-classification", model=model_name)
    
        for sentence_i , sentence in enumerate(sentiment):
    
            # Predict sentiment score
            result = sentiment_model(sentence)[0]
    
            # Add other related information to the result
            result['sentence_i'] = sentence_i
            result['n_sentences'] = len(sentence)
            result['sentence'] = sentence
            result['model_name'] = model_name
    
            results.append(result)
    
    # Convert results to pandas dataframe
    results = pd.DataFrame(results)
    
    #function to encode the sentiment labels and score 
    def try_encode_score(label: str) -> float:
        """
        This function encodes sentiment labels as numerical scores.
        
        Args:
            label (str): The sentiment label
        
        Returns:
            score (float): The numerical score corresponding to the sentiment label
        """
        encoding_dict = {
            'neutral': 0, 
            'positive': 1, 
            'negative': -1,
            '1 star': -1,
            '2 stars': -0.5,
            '3 stars': 0,
            '4 stars': 0.5,
            '5 stars': 1,
        }
    
        try:
            return encoding_dict[label.lower()]
        except:
            return 0
        
    # Process the sentiment score and assign a sentiment label
    results['Sentiment Score'] = results['label'].apply(try_encode_score)*results['score']
    results_2 = results.groupby(['sentence']).agg({'Sentiment Score' : 'mean', 'score' : 'mean'}).reset_index()
    results_2['Label'] = results_2['Sentiment Score'].apply(lambda x: 'Positive' if x > 0.06 else ('Neutral' if (x >= -0.06 and x <=0.06) else 'Negative'))
    return results_2





def extract_qa(final_ans: List[str]) -> List[Dict]:
    """
    Extracts sentiment data in JSON format from extracted answers.
    
    Args:
    final_ans (List[str]): List containing answers generated by LLM.
    
    Returns:
    sentiment_llama (List[Dict]): List containing sentiment data in JSON format.
    """
    # Initialize empty list
    sentiment_llama = []
    j = 0
    
    # Loop through each answer generated by LLM
    for i in final_ans:
        print(i) # Debugging statement
        j = j+1 # Increment the counter
        print(j) # Debugging statement
        try:
            # Check if i contains a list with multiple elements
            if (str(i).strip().find('[') != -1) and (str(i).strip().find(']') != -1) and len(ast.literal_eval(i[str(i).find('['):str(i).find(']')+1])) > 1:
                start_index = str(i).find('[')
                end_index = str(i).find(']')
                
                # Loop through each element in the list
                for t in ast.literal_eval(i[start_index:end_index+1]):
                    t = str(t)
                    start_index_nested = str(t).find('{')
                    end_index_nested = str(t).find('}')
                    sentiment_llama.append(ast.literal_eval(t[start_index_nested:end_index_nested+1].replace('\n', '')))
                
            # Check if i contains only a single list element
            elif (str(i).strip().find('[') != -1) and (str(i).strip().find('{') != -1) and (str(i).strip().find('}') == -1) and (str(i).strip().find(']') == -1):
                i = str(i)+'"' +'}'+']'
                start_index = str(i).find('[')
                end_index = str(i).find(']')
                
                # Extract the single list element and add to the result list
                for t in ast.literal_eval(i[start_index:end_index+1]):
                    t = str(t)
                    start_index_nested = str(t).find('{')
                    end_index_nested = str(t).find('}')
                    sentiment_llama.append(ast.literal_eval(t[start_index_nested:end_index_nested+1].replace('\n', '')))
            
            # Check if i contains only a single dictionary element
            elif (str(i).strip().find('[') != -1) and (str(i).strip().find('{') != -1) and (str(i).strip().find('}') != -1) and (str(i).strip().find(']') == -1):
                i = str(i) + ']'
                start_index = str(i).find('[')
                end_index = str(i).find(']')
                
                # Extract the single dictionary element and add to the result list
                for t in ast.literal_eval(i[start_index:end_index+1]):
                    t = str(t)
                    start_index_nested = str(t).find('{')
                    end_index_nested = str(t).find('}')
                    sentiment_llama.append(ast.literal_eval(t[start_index_nested:end_index_nested+1].replace('\n', '')))
            
            # Check if i is a simple dictionary element
            else:
                start_index = str(i).find('{')
                end_index = str(i).find('}')
                
                # Extract the simple dictionary element and add to the result list
                sentiment_llama.append(ast.literal_eval(i[start_index:end_index+1].replace('\n', '')))
        
        # If an error occurs during extraction, add the simple dictionary element to the result list
        except:
            start_index = str(i).find('{')
            end_index = str(i).find('}')
            sentiment_llama.append(ast.literal_eval(i[start_index:end_index+1].replace('\n', '')))
    
    # Return the list containing sentiment data in JSON format
    return sentiment_llama


def convert_text(text: List[str]) -> str:
    """
    Combines a list of strings into one string

    Args:
    text (list[str]): List of strings to combine into a single string

    Returns:
    str: A single string containing all the strings in the input list
    """
    return ''.join(text)


def llm_qa_invoke(prompt:str, max_token:int) -> str:
    """
    Invokes Mixtral API to generate a response message.

    Args:
    prompt (str): Prompt given to the Mixtral API to generate a response
    max_token (int): The maximum number of tokens to generate for the response message

    Returns:
    str: The response message generated by the Mixtral API
    """
    response = requests.post(
            url=f"{os.environ['DATABRICKS_HOST']}/serving-endpoints/databricks-mixtral-8x7b-instruct/invocations",
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



def doc_split(comb_text: str) -> List:
    """
    Splits a string into a list of documents.

    Args:
        comb_text (str): A long text containing multiple documents.

    Returns:
        list: A list of documents split from the input text using the last occurrence of "Question and Answer" as the split point.
    """
    # Find all occurrences of "Question and Answer" in the text    
    iter = re.finditer(r'.*Question and Answer\n.*', comb_text)

    # Get the indices of all occurrences
    indices = [m.start(0) for m in iter]

    # Get the index of the last occurrence
    start_ind = indices[len(indices) - 1]

    # Split the text starting from the last occurrence of "Question and Answer"
    doc_split = comb_text[start_ind:].split('Operator\n')

    # Remove the first element since it contains the delimiter
    doc_split = doc_split[1:]

    return doc_split


def split_string_into_sentences(input_string: str) -> List[str]:
    """
    Splits a given input string into sentences based on period followed by space 
    or new line character. 
    
    Args:
    input_string (str): Input string
    
    Returns:
    List[str]: List of sentences obtained through splitting input string
    """
    # Split input string into sentences based on period followed by space or new line character
    sentences = re.split(r'(?<=[a-zA-Z])\.(?=\s|$)', input_string)
    
    # Return List of sentences obtained through splitting input string
    return sentences


def split_sentence(doc: str) -> List[str]:
    """
    Splits a document into individual sentences. 

    Parameters:
    doc (str): A document containing multiple sentences.

    Returns:
    List[str]: List of individual sentences. 
    """

    # Initialize an empty list to store the individual sentences
    sentence_individual = []

    # Iterate through each character in the document
    for i in doc:
        # Split each character into sentences
        for j in split_string_into_sentences(str(i).strip().replace('\n', ' ')):
            # Used to filter senteces containig introductory statements 
            if len(j) > 20:
                sentence_individual.append(j)
            else:
                continue

    # Return the list of individual sentences
    return sentence_individual

def extract_company_names(pdf_files: List[str], path: str) -> List[str]:
    """
    Extracts company names from pdf file path.
    
    Args:
    pdf_files (List[str]): List containing file paths of PDF files
    
    Returns:
    company_names (List[str]): List containing company names extracted from file paths
    """
    company_names = []
    
    # Iterate through each PDF file path in the list
    for string in pdf_files:
        
        # Find the start and end indices of the company name within the file path
        start = string.find(path[(path[:path.rfind('/')].rfind('/'))+1:]) + len(path[(path[:path.rfind('/')].rfind('/'))+1:])

        if string.find('_Earnings Call_') != -1:
            end = string.find('_Earnings Call_')
        else:
            end = string.find('_Earnings_Call_')
        
        # Extract the company name using the start and end indices
        company_name = string[start:end]
        print(company_name)
        
        # Add the extracted company name to the list of company names
        company_names.append(company_name)
    
    # Return the list of extracted company names
    return company_names