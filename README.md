# psychKG‑pilot

Extract structured psychological constructs from TEI‑encoded research papers using large language models.

## 🧩 Scripts (`src/`)

- **`psychKG-IE-HuggingFace.py`**  
  Uses Hugging Face models (e.g., Qwen 2.5, Instructor + Pydantic) to extract structured triples.

- **`psychKG-IE-OpenAI.py`**  
  Uses OpenAI GPT‑4 (via API) with function‑calling and Pydantic for structured output.

- **`psychKG-IE-ChatAI.py`**  
  Uses the OpenAI Assistant API (ChatGPT‑style) with structured function calls and validation.

## 📂 Input

Raw TEI‑XML files located in:
```
data/papers_input_tei_xml/
```

## 📤 Output

Extracted JSON output saved to:
```
data/IE_output/
├── o3/       ← outputs from OpenAI-based scripts
└── qwen2_5/  ← outputs from ChatAI script
```

Each JSON file contains a list of entries with:
```json
{
  "construct": "...",
  "measured_by": "...",
  "justification": "..."
}
```

## ▶️ Usage

### Hugging Face model:
```bash
python src/psychKG-IE-HuggingFace.py \
  --input_dir data/papers_input_tei_xml \
  --output_dir data/IE_output/qwen2_5
```

### OpenAI-based scripts:
```bash
export OPENAI_API_KEY="YOUR_KEY"
python src/psychKG-IE-OpenAI.py \
  --input_dir data/papers_input_tei_xml \
  --output_dir data/IE_output/o3

python src/psychKG-IE-ChatAI.py \
  --input_dir data/papers_input_tei_xml \
  --output_dir data/IE_output/o3
```

## ✅ Requirements

- Python packages: `transformers`, `instructor`, `pydantic`, `beautifulsoup4`, `openai`
- GPU recommended for Hugging Face script (Qwen 2.5‑72B)
- GPT‑4 and Assistants API access for OpenAI-based scripts

---

Built to extract **construct–measurement–justification** triples from psychology papers using LLMs with strong schema validation([medium.com](https://medium.com/%40jenlindadsouza/psychkg-how-to-build-a-minimal-knowledge-graph-for-psychology-fac0c76800ac?utm_source=chatgpt.com), [medium.com](https://medium.com/%40jenlindadsouza/how-i-get-llms-on-hugging-face-to-speak-structured-data-1fb34bf15792?utm_source=chatgpt.com)).
```

---

You can download this and place it as `README.md` at your project root. Let me know if you'd like links, examples, or additional sections!