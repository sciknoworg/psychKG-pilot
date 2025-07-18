import os
import json
import re
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup

from pydantic import BaseModel, ValidationError
from instructor import Instructor
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from tqdm import tqdm
import torch

# --------- Schema ---------
class PsychTriple(BaseModel):
    construct: str
    measured_by: str
    justification: str

# --------- TEI XML Extraction ---------
def extract_text_from_tei_xml(tei_path: str) -> str:
    try:
        with open(tei_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'lxml-xml')
            body = soup.find('text')
            return body.get_text(separator='\n') if body else ''
    except Exception as e:
        print(f"Error parsing {tei_path}: {e}")
        return ""

# --------- Prompt Builder ---------
def build_prompt(text: str) -> str:
    return f"""
You are an expert in psychology and computational knowledge representation. Your task is to extract key scientific information from psychology research articles to build a structured knowledge graph.

The knowledge graph aims to represent the relationships between psychological **topics or constructs** and their associated **measurement instruments or scales**. Specifically, for each article, extract information in the form of triples that capture:

1) The psychological topic or construct being studied  
2) The measurement instrument or scale used to assess it  
3) A brief justification (1–3 sentences) from the article text supporting this measurement link

Guidelines:
- Extract meaningful **phrases** (not full sentences or vague descriptions) for both `construct` and `measured_by`, suitable for inclusion in a knowledge graph.
- Include a short justification for each extraction that clearly supports the connection.
- If the article does not discuss psychological constructs and how they are measured (e.g., no mention of constructs, instruments, or scales), return an empty list `[]`.

Input Paper:
\"\"\"{text}\"\"\"

Output: Provide your response as a JSON list in the following format:

[
  {{
    "construct": "...",
    "measured_by": "...",
    "justification": "..."
  }},
  ...
]
""".strip()

# --------- Hugging Face Chat-Like Wrapper ---------
class HuggingFaceWrapper:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def create(self, messages, response_model, **kwargs):
        # Assume last user message is the actual prompt
        prompt = messages[-1]["content"]
        response = self.pipeline(prompt, **kwargs)[0]["generated_text"]

        # Clean JSON block from model output
        cleaned = re.sub(r"^```(?:json)?\n|\n```$", "", response.strip(), flags=re.IGNORECASE)
        try:
            parsed = json.loads(cleaned)
            return [response_model.__args__[0](**item) for item in parsed]
        except Exception as e:
            raise ValueError(f"❌ Failed to decode JSON: {e}\n\nRaw response:\n{response}")

# --------- Process One File ---------
def process_file(file_path: str, prompt_dir: str, json_dir: str, llm: Instructor) -> bool:
    text = extract_text_from_tei_xml(file_path)
    if not text:
        print(f"⚠️ Skipping empty or malformed text in {file_path}")
        return False

    prompt = build_prompt(text[:100000])
    prompt_path = Path(prompt_dir) / (Path(file_path).stem + ".prompt.txt")
    output_path = Path(json_dir) / (Path(file_path).stem + ".json")

    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"🔍 Sending prompt for {file_path} to the Hugging Face LLM...")

    try:
        results = llm.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            response_model=List[PsychTriple],
            max_new_tokens=1500,
            temperature=0.2
        )

        if not results:
            print(f"✅ {file_path} | Extracted 0 triples")
            return False

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in results], f, indent=2)
        print(f"✅ {file_path} | Extracted {len(results)} triples")
        return True

    except ValidationError as ve:
        print(f"❌ Validation failed for {file_path}:\n{ve}")
    except Exception as e:
        print(f"❌ Failed to process {file_path}: {e}")
    return False

# --------- Main ---------
def main():
    model_name = input("Enter Hugging Face model name (e.g., Qwen/Qwen2.5-7B-Instruct): ").strip()
    input_dir = input("Enter input directory with .xml files: ").strip()
    prompt_dir = input("Enter directory to save prompts: ").strip()
    json_dir = input("Enter directory to save JSON outputs: ").strip()

    for d in [input_dir, prompt_dir, json_dir]:
        os.makedirs(d, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        return_full_text=False
    )

    # ✅ Wrap pipeline to mimic OpenAI-style chat.create interface
    wrapped = HuggingFaceWrapper(pipe)
    llm = Instructor(create=wrapped.create)

    files = list(Path(input_dir).glob("*.xml"))
    if not files:
        print(f"⚠️ No .xml files found in {input_dir}")
        return

    total_articles = 0
    satisfied_articles = 0

    for xml_file in tqdm(files, desc="Processing TEI XML files"):
        total_articles += 1
        success = process_file(str(xml_file), prompt_dir, json_dir, llm)
        if success:
            satisfied_articles += 1

    print("\n=== Extraction Summary ===")
    print(f"Total articles processed: {total_articles}")
    print(f"Articles with extracted constructs and measures: {satisfied_articles}")
    print(f"Articles without relevant content: {total_articles - satisfied_articles}")

if __name__ == "__main__":
    main()
