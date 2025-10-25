import tabula
import pandas as pd
from pdfminer.high_level import extract_text

# Function to extract tables using tabula-py
def extract_tables_from_pdf(pdf_path):
    try:
        # Extract tables from all pages in the PDF
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, guess=True, strip_text=True)
        print(f"Found {len(tables)} tables in the PDF.")
        return tables
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []

# Function to clean and process extracted tables
def clean_and_save_tables(tables):
    for idx, table in enumerate(tables):
        # Remove rows where all values are NaN (empty)
        table_cleaned = table.dropna(axis=0, how='all')
        
        # Clean column names: remove spaces, convert to lowercase
        table_cleaned.columns = table_cleaned.columns.str.strip().str.lower()

        # Save the cleaned table to a CSV file
        table_cleaned.to_csv(f"cleaned_table_{idx}.csv", index=False)
        print(f"Cleaned table_{idx}.csv saved successfully.")

# Function to extract raw text from PDF using pdfminer.six (optional)
def extract_text_from_pdf(pdf_path):
    try:
        # Extract text from the PDF
        text = extract_text(pdf_path)
        print(f"Extracted text from PDF (first 500 characters): \n{text[:500]}")
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

# Main script to extract and process tables
def main():
    # Step 1: Extract tables using tabula-py
    tables = extract_tables_from_pdf(pdf_path)
    
    # If tables were found, clean and save them
    if tables:
        clean_and_save_tables(tables)
    
    # Step 2: If no tables were found, try extracting raw text from the PDF
    if not tables:
        print("No tables found, extracting raw text from PDF...")
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Optionally: You can save the extracted text to a file or process it further
        with open("extracted_text.txt", "w") as file:
            file.write(extracted_text)
        print("Raw text saved to 'extracted_text.txt'.")

if __name__ == "__main__":
    main()