import os
import json
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup

from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from instructor import Instructor, patch_instructor

# --------- Step 1: Define Your Pydantic Schema ---------
class PsychTriple(BaseModel):
    topic_or_construct: str
    measured_by: str
    justification: str

# --------- Step 2: Extract Text from TEI XML ---------
def extract_text_from_tei_xml(tei_path: str) -> str:
    try:
        with open(tei_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'lxml-xml')
            body = soup.find('text')
            return body.get_text(separator='\n') if body else ''
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return ""

# --------- Step 3: Build the Prompt (schema introspection handled by Instructor) ---------
def build_prompt(text: str) -> str:
    return f"""
You are an expert in psychology and computational knowledge representation. Your task is to extract key scientific information from psychology research articles to build a structured knowledge graph.

The knowledge graph aims to represent the relationships between psychological **topics or constructs** and their associated **measurement instruments or scales**. Specifically, for each article, extract information in the form of triples that capture:

1) The psychological topic or construct being studied
2) The measurement instrument or scale used to assess it
3) A brief justification (1–3 sentences) from the article text supporting this measurement link

Guidelines:
- Extract meaningful **phrases** (not full sentences or vague descriptions) for both `topic_or_construct` and `measured_by`, suitable for inclusion in a knowledge graph.
- Include a short justification for each extraction that clearly supports the connection.
- If the article does not discuss psychological constructs and how they are measured (e.g., no mention of constructs, instruments, or scales), return an empty list `[]`.

Input Paper:
\"\"\"{text}\"\"\"

Output: Provide your response as a JSON list in the following format:

[
  {{
    "topic_or_construct": "...",
    "measured_by": "...",
    "justification": "..."
  }},
  ...
]
""".strip()

# --------- Step 4: Process One File ---------
def process_file(file_path: str, output_dir: str, llm: Instructor):
    text = extract_text_from_tei_xml(file_path)
    if not text:
        print(f"Skipping empty or malformed text in {file_path}")
        return

    prompt = build_prompt(text[:100000])  # the context length for Qwen is 128K tokens

    try:
        # This is where Instructor handles prompt formatting + schema validation + retry!
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

    model_name = "Qwen/Qwen2.5-72B-Instruct"  # or another instruct model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Load text-generation pipeline
    text_gen_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=8000) #Qwen can generate upto 8K tokens

    # 🧠 Enable Instructor retry + schema formatting
    patched_pipeline = patch_instructor(text_gen_pipeline, max_retries=3)
    llm = Instructor(patched_pipeline)

    for xml_file in Path(input_dir).glob("*.xml"):
        process_file(str(xml_file), output_dir, llm)

if __name__ == "__main__":
    main()
