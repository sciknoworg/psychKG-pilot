# psychKG‑pilot

Extract structured **construct–measured_by–justification** triples from TEI‑encoded research papers using LLMs.

---

## 🧩 Scripts (in `src/`)

- **`psychKG-IE-HuggingFace.py`**  
  Uses a local Hugging Face model via the Instructor + Pydantic pipeline.

- **`psychKG-IE-OpenAI.py`**  
  Uses OpenAI GPT‑4 API with function‑calling and Pydantic validation. Outputs to `data/IE_output/o3`.

- **`psychKG-IE-ChatAI.py`**  
  Connects to the KISSKI ChatAI API (via the GWDG/KISSKI HPC service) for various open-weights models including from the Qwen model family (e.g., Qwen 2.5‑72B), deepseek and GPT models. Outputs to `data/IE_output/qwen2_5`.

---

## 📥 Input

Raw TEI‑XML papers located in:
```
data/papers_input_tei_xml/
```

---

## 📤 Output

Extracted data saved as JSON to:
```
data/IE_output/
├── o3/       ← OpenAI‑ and ChatAI-based scripts output
└── qwen2_5/  ← ChatAI script output
```

Each JSON file contains a list of entries:
```json
{
  "construct": "...",
  "measured_by": "...",
  "justification": "..."
}
```

---

## ⚙️ Requirements

Packages used:
- `transformers`, `instructor`, `pydantic`, `beautifulsoup4`, `openai`
- Access to KISSKI ChatAI endpoint (AcademicCloud / GWDG HPC)
- GPU recommended for Hugging Face script

---

## ▶️ Usage

### 1. Hugging Face (local)
```bash
python src/psychKG-IE-HuggingFace.py \
  --input_dir data/papers_input_tei_xml \
  --output_dir data/IE_output/qwen2_5
```

### 2. OpenAI GPT‑4
```bash
python src/psychKG-IE-OpenAI.py \
  --input_dir data/papers_input_tei_xml \
  --output_dir data/IE_output/o3
```

### 3. ChatAI via KISSKI
Ensure you have API access to KISSKI ChatAI (see GWDG/KISSKI LLM‑Service) and appropriate credentials, then run:
```bash
python src/psychKG-IE-ChatAI.py
```

---

## ℹ️ Notes

1. **Qwen output also comes via the KISSKI ChatAI** endpoint using Qwen 2.5‑72B weights hosted by the service.
2. **KISSKI ChatAI API** is a secure, OpenAI-compatible endpoint (supports GPT‑4 and open models) and adheres to data privacy rules ([kisski.gwdg.de](https://kisski.gwdg.de/en/leistungen/2-02-llm-service/?utm_source=chatgpt.com), [dfn.de](https://www.dfn.de/wp-content/uploads/2024/10/BT81_Forum_Cloud_GWDG_Chat_AI.pdf?utm_source=chatgpt.com)).

---

## 🚀 Purpose

Built to extract **construct–measurement–justification** triples from psychology papers using LLMs with strong schema validation([medium.com](https://medium.com/%40jenlindadsouza/psychkg-how-to-build-a-minimal-knowledge-graph-for-psychology-fac0c76800ac?utm_source=chatgpt.com), [medium.com](https://medium.com/%40jenlindadsouza/how-i-get-llms-on-hugging-face-to-speak-structured-data-1fb34bf15792?utm_source=chatgpt.com)).

---

## 🔖 Citation

If you use this repository in your work, please cite:

> D'Souza, J., & Wulff, D. (2025). *psychKG-pilot: A Minimal Knowledge Graph for Psychology via LLM-based Structured Extraction* (Version 0.1.0) [Computer software]. TIB & MPIB. https://github.com/sciknoworg/psychKG-pilot

Or use the [`CITATION.cff`](./CITATION.cff) file for automatic citation formats.

---

## 📬 License & Contact

This project is licensed under the MIT License.

If you have questions, feedback, or ideas to improve the project, feel free to open an issue or get in touch with us — we'd love to hear from you!



