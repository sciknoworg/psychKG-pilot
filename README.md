# psychKG-pilot

A minimal pipeline to extract structured psychological knowledge (constructs and measures) from PDF research articles using GROBID and OpenAI structured output parsing.

## Directory Structure

```
psychKG-pilot/
├── grobid_batch_process.py
├── psychKG-IE.py
├── input_pdfs/
│   ├── paper1.pdf
│   ├── paper2.pdf
│   ├── ...
├── output_tei/
```


## Setup

```bash
git clone https://github.com/sciknoworg/psychKG-pilot.git
cd psychKG-pilot
pip install requests openai beautifulsoup4 pydantic
```
