import os
import requests
from pathlib import Path
from time import sleep

# Configuration
GROBID_URL = "https://orkg.org/grobid/api/processFulltextDocument"
PDF_INPUT_DIR = "input_pdfs"       # Folder containing PDF files
TEI_OUTPUT_DIR = "output_tei"      # Folder to store TEI XML files

# Ensure output directory exists
os.makedirs(TEI_OUTPUT_DIR, exist_ok=True)

# Loop through each PDF in the input directory
for pdf_file in Path(PDF_INPUT_DIR).glob("*.pdf"):
    tei_output_path = Path(TEI_OUTPUT_DIR) / (pdf_file.stem + '.tei.xml')
    
    # Skip if already processed
    if tei_output_path.exists():
        print(f"Skipping already processed file: {pdf_file.name}")
        continue

    with open(pdf_file, 'rb') as f:
        files = {
            'input': (pdf_file.name, f, 'application/pdf')
        }
        print(f"Processing: {pdf_file.name}")
        try:
            response = requests.post(GROBID_URL, files=files)
            if response.status_code == 200:
                with open(tei_output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(response.text)
            else:
                print(f"Failed to process {pdf_file.name} - Status code: {response.status_code}")
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")

    sleep(1)  # Avoid overloading GROBID server
