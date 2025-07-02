import os
import json
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup

from pydantic import BaseModel, ValidationError
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from instructor import Instructor
from tqdm import tqdm
import torch

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
        print(f"Error parsing {tei_path}: {e}")
        return ""

# --------- Step 3: Build the Prompt ---------
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
        print(f"⚠️ Skipping empty or malformed text in {file_path}")
        return

    prompt = build_prompt(text[:100000])  # Truncate for context limits
    output_path = Path(output_dir) / (Path(file_path).stem + ".json")
    prompt_path = output_path.with_suffix(".prompt.txt")

    # Log the prompt for debugging
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    try:
        results = llm(prompt, output_type=List[PsychTriple])
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([r.dict() for r in results], f, indent=2)
        print(f"✅ {file_path} | Extracted {len(results)} triples")
    except ValidationError as ve:
        print(f"❌ Validation failed for {file_path}:\n{ve}")
    except Exception as e:
        print(f"❌ Failed to process {file_path}: {e}")

# --------- Step 5: Main Execution ---------
def main(input_dir="input_xml", output_dir="extracted_json"):
    os.makedirs(output_dir, exist_ok=True)

    model_name = "Qwen/Qwen2.5-72B-Instruct"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )

    text_gen_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=8000,
        return_full_text=False
    )

    # No patch_instructor anymore – just wrap the HF pipeline
    llm = Instructor(text_gen_pipeline)

    files = list(Path(input_dir).glob("*.xml"))
    for xml_file in tqdm(files, desc="Processing TEI XML files"):
        process_file(str(xml_file), output_dir, llm)

if __name__ == "__main__":
    main()
