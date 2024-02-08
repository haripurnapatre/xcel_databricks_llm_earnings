from src.llm_setup.experiment_utils import *
from src.data_processing.data_format import *
from src.data_processing.data_extraction import *
from src.llm_setup.prompt import *
from src.llm_setup.llm_call import *
import yaml

with open('../../config.yml', 'r') as file:
    config_params = yaml.safe_load(file)
    
def ir_overview_report(pdf_files: List[str], company_name: List[str], p_overview : str, p_summary : str) -> None:
    """
    This function generates an overview report for investor relations based on PDF files and company names.
    
    Args:
        pdf_files (List[str]): A list of PDF file paths.
        company_name (List[str]): A list of company names.
        p_overview (str): LLM Prompt to generate overview by category.
        p_summary (str): LLM Prompt to generate summary by category.
        
    Returns:
        None
    """

    # Iterate over the PDF files and company names
    for j, i in enumerate(pdf_files):
        company = company_name[j]

        # Print the current company name
        print(f'Company: {company}')

        # Extract text from the PDF file
        raw_txt = get_pdf_txt(i)

        # Clean the extracted text
        cleaned_txt = clean_text(raw_txt)

        # Split the cleaned text into sections
        split_txt = split_text(cleaned_txt)

        # Format the split text
        formatted_txt = format_text(split_txt)

        # Remove the last two elements from the formatted text
        formatted_txt = formatted_txt[0:len(formatted_txt)-2]

        # Generate the report for the company overview
        ans_comb = generate_report(formatted_txt, p_overview, company)

        # Clean the report chunks by removing disclaimers
        cleaned_chunks = remove_disclaimer(ans_comb) 

        # Extract relevant data from cleaned report chunks
        summary_cntxt = extract_data(cleaned_chunks)

        # Combine the extracted data into a final report
        final_report = combine_extract(summary_cntxt)

        # Summarize the response in an excel report
        xcel_report = summarize_response(final_report, p_summary)

        # Create a DataFrame from the excel report
        df_response = pd.DataFrame(xcel_report, index=[0])

        # Save the DataFrame as a CSV report
        df_response.to_csv(f"{config_params['pull_report']['reports_dir'].replace('dbfs:', '/dbfs')}{company}_IR_Report.csv")


def preqa_report(pdf_files: List[str], company_name: List[str], model_names: List[str], p_preqa : str) -> None:
    """
    Generate a PreQA report for a list of PDF files, with specific company names and model names.
    
    Args:
        pdf_files: A list of strings representing the paths to the PDF files.
        company_name: A list of strings representing the company names corresponding to the PDF files.
        model_names: A list of strings representing the names of the models for sentiment analysis.
        p_preqa (str): LLM Prompt to analyze sentiment by paragraph
    
    Returns:
        None
    """
    # iterate over the list of PDF files
    for j, i in enumerate(pdf_files):

        # get the company name for the current file
        company = company_name[j]

        # extract the text from the PDF file
        text = extract_text_qa(i)

        # split the document into sections
        doc_split = preqa_split(text)

        # remove any disclaimers from the document
        doc = preqa_remove_disclaimer(doc_split)

        # perform sentiment analysis using the provided models
        results = sentiment_analysis(model_names, doc)

        # calculate the maximum tokens available for the model call
        model_max_tokens = 32768
        temp = p_preqa.format(BODY1 = results['sentence'].iloc[0], BODY2 = results['Label'].iloc[0]) 
        token_est = int(len(temp)/2)
        call_max_tokens = model_max_tokens - token_est

        # create an instance of the DatabricksMixtral class
        llm = DatabricksMixtral(max_tokens=call_max_tokens, temperature=0)

        # generate the final answer using preqa
        final_ans = llm_preqa(results, llm, p_preqa)

        # extract the sentiment using the provided function
        sentiment_llama = extract_qa(final_ans)

        # create a DataFrame for the sentiment results
        df_sentiment = pd.DataFrame(sentiment_llama)

        # concatenate the sentiment DataFrame with the original results DataFrame
        df_final_sentiment = pd.concat([df_sentiment.rename(columns={'Label' : 'Category'}), results], axis = 1)

        # save the final sentiment report to a CSV file
        df_final_sentiment.to_csv(f"{config_params['pull_report']['reports_dir'].replace('dbfs:', '/dbfs')}{company}_PreQA_Sentiment.csv")
        
def qa_report(pdf_files: List[str], company_name: List[str], p_qa : str) -> None:
    """
    Generates a QA report for a list of PDF files.

    Args:
    pdf_files (List[str]): A list of PDF file paths.
    company_name (List[str]): A list of company names corresponding to the PDF files.
    p_qa (str): LLM Prompt to extract q&a with importance scores and highlights

    Returns:
    None
    """
    for j, i in enumerate(pdf_files):
       # Get the company name for the current PDF file 
       company = company_name[j]

       # Print the company name
       print(f'Company: {company}')

       # Extract the text from the PDF
       text = extract_text_qa(i)

       # Convert the text to a suitable format
       comb_text = convert_text(text)

       # Split the combined text into separate documents
       comb_text_split = doc_split(comb_text)

       # Perform question answering on the split documents
       final_ans = llm_qa(comb_text_split, p_qa)

       # Extract the relevant information from the question answering result
       sentiment_llama = extract_qa(final_ans)

       # Create a DataFrame from the extracted information
       df_qa = pd.DataFrame(sentiment_llama)

       # save the final sentiment report to a CSV file
       df_qa.to_csv(f"{config_params['pull_report']['reports_dir'].replace('dbfs:', '/dbfs')}{company}_QA_Report.csv")


def highlight_pdf(pdf_files: List, company_name: List, model_names: List) -> None:
    """
    Highlights text in the PDF files based on the sentiment analysis results.
    
    Args:
        pdf_files (List): A list of PDF files to process.
        company_name (List): A list of company names corresponding to the PDF files.
        model_names (List): A list of sentiment analysis model names.
    
    Returns:
        None
    """
    # iterate over each PDF file and corresponding company name
    for j, i in enumerate(pdf_files):
        # get the current company name
        company = company_name[j]
        print(company)

        # extract text from the PDF
        text = extract_text_qa(i)

        # preprocess the extracted text
        doc = preqa_remove_disclaimer(text)

        # split text into sentences
        sentence_individual = split_sentence(doc)

        # perform sentiment analysis
        results = sentiment_analysis(model_names, sentence_individual)

        # filter results based on score and negative label
        results = results[(results['score'] > 0.9) | (results['Label'].str.strip() == 'Negative')]

        # open the PDF document
        docs  = fitz.open(i)
        
        # iterate over each sentence in the results
        for page in docs:
            print(page)
            for j, text in enumerate(results['sentence']):

                # search for the sentence in the page
                quads = page.search_for(text, quads=True)

                # add a highlight annotation for each matched sentence
                for quad in quads:
                    # set the colors of the annotation based on the sentiment label
                    annot = page.add_highlight_annot(quad)
                    if results['Label'].iloc[j] == 'Negative':
                        annot.set_colors(stroke=[1, 0.8, 0.8])
                    elif results['Label'].iloc[j] == 'Positive':
                        annot.set_colors(stroke=[0.7, 0.9, 0.4])
                    elif results['Label'].iloc[j] == 'Neutral':
                        annot.set_colors(stroke=[0.7, 0.9, 0.9])

                    # update the annotation
                    annot.update()
        
        # save the modified PDF with highlighted annotations for the current company
        docs.save(f"{config_params['pull_report']['reports_dir'].replace('dbfs:', '/dbfs')}{company}_highlight.pdf")
