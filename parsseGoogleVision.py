import fitz  # PyMuPDF
from google.cloud import vision
from google.oauth2 import service_account
import io
import re
import pandas as pd

# Path to your Google Cloud credentials JSON file
key_path = "your json file"

# Create credentials
credentials = service_account.Credentials.from_service_account_file(key_path)

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF using Google Cloud Vision API.
    """
    client = vision.ImageAnnotatorClient(credentials=credentials)
    pdf_document = fitz.open(pdf_path)
    extracted_text = ""

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")

        # Use Google Cloud Vision to extract text
        image = vision.Image(content=img_bytes)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            extracted_text += texts[0].description + "\n"  # Full text is in the first annotation

    # Print the extracted text for debugging
    print("Extracted Text:\n", extracted_text)
    return extracted_text

def parse_transactions(text):
    """
    Parses extracted text into structured transactions.
    """
    transactions = []
    lines = text.split("\n")

    # Regex patterns to identify transaction details
    date_pattern = r"\d{2}-\w{3}-\d{4}"  # Matches dates in DD-MMM-YYYY format (e.g., 01-Apr-2018)
    amount_pattern = r"[-+]?\d{1,3}(?:,\d{3})*\.\d{2}"  # Matches amounts with commas (e.g., 1,000.00)

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Extract transaction date
        date_match = re.search(date_pattern, line)
        if date_match:
            transaction_date = date_match.group()

            # Initialize description and amounts
            description = line.replace(transaction_date, "").strip()
            debit = 0.0
            credit = 0.0
            balance = 0.0

            # Look ahead for the next lines to get the full transaction details
            while i + 1 < len(lines):
                next_line = lines[i + 1].strip()

                # Check if the next line contains amounts
                amount_matches = re.findall(amount_pattern, next_line.replace(",", ""))
                if len(amount_matches) >= 3:  # Debit, Credit, Balance
                    debit = float(amount_matches[0])
                    credit = float(amount_matches[1])
                    balance = float(amount_matches[2])
                    i += 1
                    break

                # Append to the description if the line is part of the current transaction
                description += " " + next_line
                i += 1

            # Determine transaction type and amount
            if debit > 0:
                amount = -debit  # Negative for withdrawals
                transaction_type = "withdrawal"
            elif credit > 0:
                amount = credit  # Positive for deposits
                transaction_type = "deposit"
            else:
                amount = 0.0
                transaction_type = "unknown"

            # Add transaction to the list
            transactions.append({
                "Date": transaction_date,
                "Description": description,
                "Amount": amount,
                "Type": transaction_type,
                "Balance": balance
            })

        i += 1

    return transactions

def save_to_csv(transactions, output_path):
    """
    Saves transactions to a CSV file.
    """
    df = pd.DataFrame(transactions)
    df.to_csv(output_path, index=False)

# Example usage
if __name__ == "__main__":
    pdf_path = "BankStatement1.pdf"  # Replace with your PDF file path
    output_csv_path = "transactions.csv"  # Output CSV file path

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(pdf_path)

    # Parse transactions from the extracted text
    transactions = parse_transactions(extracted_text)
    print("Parsed Transactions:\n", transactions)

    # Save transactions to a CSV file
    save_to_csv(transactions, output_csv_path)
    print(f"Transactions saved to {output_csv_path}")

    