import os
import json
import getpass
from pathlib import Path
from openai import OpenAI
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List

# Define structured output classes
class PsychTriple(BaseModel):
    topic_or_construct: List[str]
    measured_by: List[str]
    justification: str

class PsychTripleList(BaseModel):
    extractions: List[PsychTriple]

# Define system message template
SYSTEM_PROMPT = '''
You are an expert in psychology and computational knowledge representation. Your task is to extract key scientific information from psychology research articles to build a structured knowledge graph. 

The knowledge graph aims to represent the relationships between psychological **topics or constructs** and their associated **measurement instruments or scales**. Specifically, for each article, you will extract information of the form:

1) "Topic or Construct"
2) [Property: "measured by"] -> [Value: "Measure"]

Each article may contain multiple such records. These extractions help build a machine-readable semantic network that connects psychological concepts with their empirical operationalizations.

For each extraction, provide a short justification from the text (1-3 sentences) that supports why this construct was measured by the identified measure.

As far as possible, extract meaningful **phrases** (rather than whole sentences or vague descriptions) as **entities** suitable for inclusion in a knowledge graph for both `topic_or_construct` and `measured_by` fields.

However, not all articles are relevant to this task. If the article does not discuss psychological constructs and how they are measured (e.g., does not mention constructs, measurement techniques, or instruments), return an empty list `[]`.
'''

# Extract text from TEI XML
def extract_text_from_tei(tei_path):
    with open(tei_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml-xml')
        body = soup.find('text')
        return body.get_text(separator='\n') if body else ''

# Run the OpenAI model on one document
def extract_triples_from_article(client, article_text):
    try:
        response = client.responses.parse(
            model="o3",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract the constructs and their measures from the following article:\n{article_text}"},
            ],
            text_format=PsychTripleList
        )
        return [triple.model_dump() for triple in response.output_parsed.extractions]
    except Exception as e:
        print(f"Extraction failed: {e}")
        return []

# Main function to iterate over folder
def main():
    api_key = getpass.getpass('Enter your OpenAI API key: ')
    client = OpenAI(api_key=api_key)

    input_folder = input("Enter the path to the folder containing TEI XML files: ").strip()
    output_folder = input("Enter the output folder path: ").strip()
    os.makedirs(output_folder, exist_ok=True)

    total_articles = 0
    satisfied_articles = 0

    for tei_file in Path(input_folder).glob("*.xml"):
        total_articles += 1
        print(f"Processing {tei_file.name}...")
        article_text = extract_text_from_tei(tei_file)
        if not article_text.strip():
            print(f"No text extracted from {tei_file.name}, skipping.")
            continue

        extracted_data = extract_triples_from_article(client, article_text)
        if extracted_data:
            satisfied_articles += 1
            output_path = Path(output_folder) / (tei_file.stem + '.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2)
        else:
            print(f"No relevant information found in {tei_file.name}, skipping write.")

    print("\n=== Extraction Summary ===")
    print(f"Total articles processed: {total_articles}")
    print(f"Articles with extracted constructs and measures: {satisfied_articles}")
    print(f"Articles without relevant content: {total_articles - satisfied_articles}")

if __name__ == "__main__":
    main()
