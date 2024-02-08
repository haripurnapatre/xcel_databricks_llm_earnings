p_overview = """<s>[INST] <<SYS>>
Please analyze the quarterly earnings call transcript for {company} and provide a comprehensive financial outlook for the company based on the context provided. If cannot analyze the quarterly earnings call transcript output the outline.


Output answer in JSON using the following format: {{"Summary": Summary, "Revenue growth drivers and challenges": Revenue growth drivers and challenges, "Margin performance and expense management": Margin performance and expense management, "Earnings quality and non-GAAP metrics": Earnings quality and non-GAAP metrics, "Capital allocation and cash flow": Capital allocation and cash flow, "Guidance and forward-looking statements": Guidance and forward-looking statements, "Conclusion": Conclusion}} Do not add array's to the response.
<</SYS>>

[/INST]
 Your analysis should include the following:
[
{{"Summary": "explanation": "A brief overview of the company's financial performance during the quarter, highlighting key metrics such as revenue, net income, and earnings per share."}},
{{"Revenue growth drivers and challenges": "explanation": "The revenue growth drivers of the company."}},
{{"Margin performance and expense management": "explanation": "The margin performance and expense management of the company."}},
{{"Earnings quality and non-GAAP metrics": "explanation": "The company's earnings quality and non-GAAP metrics"}},
{{"Capital allocation and cash flow": "explanation": "The company's capital allocation and cash flow."}},
{{"Guidance and forward-looking statements": "explanation": "Guidance and forward-looking statements for the company."}},
{{"Conclusion": "explanation": "A summary of your analysis, including a rating or recommendation on the company's stock based on your assessment of its financial outlook."}}
] </s>


<s>[INST]  
Output answer in JSON using the following format: {{"Summary": Summary, "Revenue growth drivers and challenges": Revenue growth drivers and challenges, "Margin performance and expense management": Margin performance and expense management, "Earnings quality and non-GAAP metrics": Earnings quality and non-GAAP metrics, "Capital allocation and cash flow": Capital allocation and cash flow, "Guidance and forward-looking statements": Guidance and forward-looking statements, "Conclusion" : Conclusion}} Do not add array's and quotes within the response.
context: {BODY}
[/INST]"""


p_summary = """<s>[INST] <<SYS>>
You are a financial analyst summarizing earnings call reports.
<</SYS>>
Given the report, write a detailed summary covering all the points in the report. 
report: {BODY}
[/INST]"""



p_preqa = """<s>[INST] <<SYS>>
We have provided text chunks from a report and corrosponding sentiment found in the paragraph from a report of the quarterly earnings call transcript for [Company Name] and We have the opportunity to give reasoning for the sentiment value found in the paragraphs.


Output the sentiment value in JSON using the following format: {{"Paragraph": Paragraph, "Short Explanation": Short Explanation, "Reasoning" : Reasoning, 'Label': Label, 'Sentiment': Sentiment}}
Add to the new report by summarizing all the JSON format categories from the previous report only if needed. Do not add qotation marks in the Sentiment explanation. Include each JSON category in the output.
<</SYS>>

[/INST]

[
{{"Paragraph": "explanation": "Paragraph Provided"}},
{{"Short Explanation": "explanation": "Short Explanation explaining the reasoning behind the sentiment in the paragraph in upto 5 words"}},
{{"Reasoning": "explanation": "Reasoning explaining the existing sentiment found in the sentence"}},
{{"Label": "explanation": "Give a single label out of the following categories only - Financial Performance, Market Trends, Strategic Initiatives, Operational Highlights, Guidance and Outlook, Investor Relations, Risk Management, Legal Issues, Regulatory Issues, Introduction, Name"}},
{{"Sentiment": "explanation": "existing sentiment"}}
] </s>


<s>[INST]  
Given the paragraph return the sentiment value in JSON using the following format: {{"Paragraph": Paragraph, "Short Explanation": Short Explanation, "Reasoning": Reasoning, 'Label': Label, 'Sentiment': Sentiment}}
paragraph: {BODY1}
existing sentiment: {BODY2}
[/INST]"""

p_qa = """<s>[INST] <<SYS>>
We have provided question answer conversation from an earnings call report and we have the opportunity to find the summary in the question and answer from the report of the quarterly earnings call transcript for [Company Name].


Output the report in JSON using the following format: {{"Sentences Question": Sentences Question, "Summary Answer": Summary Answer, "Importance Score": Importance Score, "Importance Highlight": Importance Highlight,  "Label": Label}}
Add to the new report by summarizing all the JSON format categories from the previous report only if needed. Do not add qotation marks in the Sentiment explanation. Include each JSON category in the output.
<</SYS>>

[/INST]

[
{{"Sentences Question": "explanation": "Sentences Provided in Question"}},
{{"Summary Answer": "explanation": "Give a detailed summary of the answer"}},
{{"Importance Score": "explanation": "Give a numerical Information score based on how much important information is covered in the question and answer conversation. The score should be a numerical value"}},
{{"Importance Highlight": "explanation": "Highlight the important information covered in the text"}},
{{"Label": "explanation": "Give a label out of only one of the following categories: Financial Performance, Market Trends, Strategic Initiatives, Operational Highlights, Guidance and Outlook, Investor Relations, Risk Management, Legal Issues, Regulatory Issues, Introduction, Name"}}
] </s>


<s>[INST]  
Given the sentences return the report in JSON using the following format: {{"Sentences Question": Sentences Question, "Summary Answer": Summary Answer, "Importance Score": Importance Score, "Importance Highlight": Importance Highlight,  "Label": Label}}
question answer conversation: {BODY1}
[/INST]"""

p_summary_overview = """<s>[INST] <<SYS>>
You are a financial analyst summarizing earnings call reports.
<</SYS>>
Write a detailed summary for the following report under 20 points.
report: {BODY}
[/INST]"""
