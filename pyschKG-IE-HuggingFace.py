import os
import json
from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET

from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from instructor import Instructor, patch_instructor

# --------- Step 1: Define Your Pydantic Schema ---------
class PsychTriple(BaseModel):
    topic_or_construct: str
    measured_by: str
    justification: str

# --------- Step 2: Extract Text from TEI XML ---------
def extract_text_from_tei_xml(file_path: str) -> str:
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return " ".join(elem.text.strip() for elem in root.iter() if elem.text)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return ""

# --------- Step 3: Build the Prompt (schema introspection handled by Instructor) ---------
def build_prompt(text: str) -> str:
    return f"""
You are an information extraction assistant.

Given the following psychology research paper, extract structured knowledge triples of the form:
"topic_or_construct" → "measured_by" → "justification"

Paper:
\"\"\"{text}\"\"\"

Return a JSON array of objects, each matching the required schema.
""".strip()

# --------- Step 4: Process One File ---------
def process_file(file_path: str, output_dir: str, llm: Instructor):
    text = extract_text_from_tei_xml(file_path)
    if not text:
        print(f"Skipping empty or malformed text in {file_path}")
        return

    prompt = build_prompt(text[:3000])  # truncate long text if needed

    try:
        # 🧠 This is where Instructor handles prompt formatting + schema validation + retry!
        results: List[PsychTriple] = llm(prompt, output_type=List[PsychTriple])
        output_path = Path(output_dir) / (Path(file_path).stem + ".json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([r.dict() for r in results], f, indent=2)
        print(f"✅ Processed: {file_path}")
    except Exception as e:
        print(f"❌ Failed to process {file_path}: {e}")

# --------- Step 5: Main Execution ---------
def main(input_dir="input_xml", output_dir="extracted_json"):
    os.makedirs(output_dir, exist_ok=True)

    model_name = "mistralai/Mistral-7B-Instruct-v0.1"  # or another instruct model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Load text-generation pipeline
    text_gen_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512)

    # 🧠 Enable Instructor retry + schema formatting
    patched_pipeline = patch_instructor(text_gen_pipeline, max_retries=3)
    llm = Instructor(patched_pipeline)

    for xml_file in Path(input_dir).glob("*.xml"):
        process_file(str(xml_file), output_dir, llm)

if __name__ == "__main__":
    main()
