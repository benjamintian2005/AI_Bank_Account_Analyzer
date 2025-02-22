import os
import pdfplumber
import pytesseract
import pandas as pd
import json
from flask import Flask, request, jsonify
from PIL import Image
from openai import OpenAI
from flask_cors import CORS

#create flask app
app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://localhost:3000"}})  # Allow requests from React frontend
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

client = OpenAI()

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    
    # If no text is extracted, try OCR (for scanned PDFs)
    if not text.strip():
        text = extract_text_using_ocr(pdf_path)
    
    return text.strip()

# Extract text using OCR for scanned PDFs
def extract_text_using_ocr(pdf_path):
    images = pdfplumber.open(pdf_path).pages[0].to_image(resolution=300).original
    return pytesseract.image_to_string(images)

# AI Summarization
def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI financial analyst. Summarize the following financial document in as much detail as possible. And if you were a bank would you give this indicual a loan"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:

        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    extracted_text = extract_text_from_pdf(file_path)
    if not extracted_text:
        return jsonify({"error": "No readable text found in PDF"}), 500

    summary = summarize_text(extracted_text)
    return jsonify({"result": summary})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
