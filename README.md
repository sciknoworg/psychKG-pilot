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



Instructions to run on a GPU server

1. Create a Python virtual environment

```
python3.11 -m venv myenv3_11
```

Replace myenv_11 with your preferred environment name.

2. Activate the virtual environment

```
source myenv3_11/bin/activate
```

pip install --upgrade pip
pip install beautifulsoup4
pip install instructor
pip install transformers
pip install torch
pip install accelerate


After o3 processing
=== Extraction Summary ===
Total articles processed: 1618
Articles with extracted constructs and measures: 1464
Articles without relevant content: 154

After Qwen 2.5 (72B Instruct) processing
=== Extraction Summary ===
Total new articles processed: 1,618
Articles with extracted constructs and measures: 1,387
Articles without relevant content: 231 