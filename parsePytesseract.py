import pdfplumber
import pytesseract
import pandas as pd
import json
from PIL import Image
from openai import OpenAI

import json
client = OpenAI()

# Function to extract text using OCR (for scanned PDFs)
def ocr_image(image):
    return pytesseract.image_to_string(image)

# Function to clean extracted table data
def clean_table(df):
    df = df.dropna(how='all')  # Remove empty rows
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Remove extra spaces
    df = df.replace('', pd.NA).dropna(how='all', axis=1)  # Remove empty columns
    df.columns = df.iloc[0]  # Set first row as header
    df = df[1:].reset_index(drop=True)  # Remove the header row from data
    return df

# Function to extract tables from PDF and save as CSV/JSON
def extract_tables(pdf_path, output_format='csv'):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            for table in extracted_tables:
                if table:  # Ensure table is not empty
                    df = pd.DataFrame(table)
                    df = clean_table(df)
                    tables.append(df)
    
    if tables:
        result = pd.concat(tables, ignore_index=True)
        if output_format == 'csv':
            result.to_csv('output.csv', index=False)
            print("Tables saved to output.csv")
        elif output_format == 'json':
            result.to_json('output.json', orient='records', indent=4)
            print("Tables saved to output.json")
    else:
        print("No tables found in the PDF.")

# Example usage
pdf_path = "BankStatement1.pdf"
extract_tables(pdf_path, 'json')



# Load JSON data
with open("output.json", "r") as file:
    data = json.load(file)

# Convert to prompt-friendly format
transactions_text = "\n".join(
    [f"{entry['Transaction Date']}: {entry['Credit']} - {entry['Balance']}" for entry in data]
)

# Use AI to summarize spending trends
response = client.chat.completions.create(model="gpt-4",
messages=[
    {"role": "system", "content": "You are a financial analyst."},
    {"role": "user", "content": f"Analyze these transactions and summarize spending patterns:\n{transactions_text}"}
])

print(response.choices[0].message.content)
