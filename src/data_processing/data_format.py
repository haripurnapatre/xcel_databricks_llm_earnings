from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
import re
from collections import namedtuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from langchain.document_loaders import TextLoader
from typing import List
from typing import Dict
import yaml

with open('../../config.yml', 'r') as file:
    prime_service = yaml.safe_load(file)
    
def get_pdf_txt(pdf_docs: str) -> str:
    """
    Extracts text from PDF documents

    Args:
    - pdf_docs (str): Path to the PDF documents

    Returns:
    - (str): Text data extracted from PDF documents
    """
    # Create a PdfReader object to read the PDF documents
    reader = PdfReader(pdf_docs)
    
    # Initialize an empty string to store the extracted text
    text = ''
    
    # Iterate through each page in the PDF documents
    for i, page in enumerate(reader.pages):
        # Extract the text from the current page and append it to the text string
        text += page.extract_text()

    # Return the extracted text
    return text



def split_text(output: List[str], chunk_size: int = 4000, chunk_overlap: int = 0) -> List[str]:
    """
    Splits a list of string output into smaller chunks of equal or near-equal length.

    Args:
    - output (list[str]): A list of string data to be split into smaller chunks.
    - chunk_size (int): The maximum length of each chunk (default=4000).
    - chunk_overlap (int): Amount of overlap between chunks,if any (default=0)

    Returns:
    - (list[str]): The input list split into one or more smaller chunks
    """

    # Create a new instance of RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(        
    separators = [" ", ",", "\n"],
    chunk_size = chunk_size,
    chunk_overlap  = chunk_overlap,
    length_function = len,
    )

    # Split the output text into smaller chunks
    texts = text_splitter.split_text(output[0])
    return texts


def remove_repeat(answer: str) -> str:
    """
    Removes repeat sentences from a given string output.

    Args:
    - answer (str): the string containing duplicate sentences

    Returns:
    - (str): the same string as input but with no duplicates.
    """
    # Split the string into sentences
    sentences = answer.split('. ')
    
    # Create a list to store unique sentences
    unique_sentences = []
    
    # Iterate over each sentence
    for sentence in sentences:
        # Check if the sentence is already in the list of unique sentences
        if sentence not in unique_sentences:
            # If not, add it to the list
            unique_sentences.append(sentence)
    
    # Join the unique sentences with '. ' separator
    result = '. '.join(unique_sentences)
    
    # Return the result
    return result


def clean_text(raw_text: str) -> List:
    """
    Cleans up text extracted from PDF documents.

    Args:
    raw_text (str): The text extracted from the PDF document.

    Returns:
    list: A list containing the cleaned up text.
    """
    output = []
    text = ""
    text = raw_text
    # Merge hyphenated words
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    # Fix newlines in the middle of sentences
    text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    output.append(text)
    return output


def format_text(texts: List[str]) -> List[namedtuple]:
    """
    Formats the extracted text as a structured document.

    Args:
    texts (list): A list of text strings representing pages of a document.

    Returns:
    list: A list of namedtuples containing the page content and metadata.
    """
  
    # Initialize an empty list to store the formatted documents
    formatted_documents = []
    page_content = []
    Document = namedtuple('Document', ['page_content', 'metadata'])
    
    # Iterate through each page of text
    for i in range(len(texts)):
        
        # Get the content of the current page
        page_content = texts[i]
        
        # Define the metadata for the current page
        metadata = {
            'source': 'earnings_call.pdf',
            'page': i + 1,
        }
        
        # Create a named tuple with the page content and metadata
        formatted_document = Document(page_content, metadata)
        
        # Append the formatted document to the list
        formatted_documents.append(formatted_document)
    
    # Return the list of formatted documents
    return formatted_documents

def remove_repeat(answer: str) -> str:
    """
    This function takes in a longer text and removes any duplicate sentences.
    
    Parameters:
    ----------
    answer : str
        The longer text to check for duplicate sentences.
        
    Returns:
    -------
    result : str
        'answer' with all duplicate sentences removed.
    """
    # Split the text into sentences
    sentences = answer.split('. ')
    
    # Initialize an empty list to store unique sentences
    unique_sentences = []
    
    # Iterate over each sentence in the input text
    for sentence in sentences:
        # If the sentence is not already in the unique_sentences list
        if sentence not in unique_sentences:
            # Add the sentence to the unique_sentences list
            unique_sentences.append(sentence)
    
    # Join the unique sentences back into a string with the '.' delimiter
    result = '. '.join(unique_sentences)
    
    # Return the result
    return result




