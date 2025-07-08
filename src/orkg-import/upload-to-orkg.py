import json
from pathlib import Path
from orkg import ORKG, OID
from getpass import getpass
from bs4 import BeautifulSoup

# ---------- Utility Functions ----------

def load_resource_cache(cache_path: Path) -> dict:
    if cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to read resource cache: {e}")
    return {}

def save_resource_cache(resource_cache: dict, cache_path: Path):
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(resource_cache, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to write resource cache: {e}")

def log_uploaded_paper_detailed(paper_log_detailed_path: Path, title: str, paper_id: str):
    try:
        with open(paper_log_detailed_path, 'a', encoding='utf-8') as f:
            f.write(f"{title}\t{paper_id}\n")
    except Exception as e:
        print(f"⚠️ Failed to log detailed paper entry: {e}")

def load_uploaded_titles(paper_log_detailed_path: Path) -> set:
    if paper_log_detailed_path.exists():
        try:
            with open(paper_log_detailed_path, 'r', encoding='utf-8') as f:
                return set(line.split('\t')[0].strip() for line in f if '\t' in line)
        except Exception as e:
            print(f"⚠️ Failed to read uploaded paper titles: {e}")
    return set()

def extract_metadata(tei_path: Path):
    with open(tei_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml-xml')

    def extract_date(d):
        if "when" in d.attrs:
            parts = d["when"].split("-")
            y = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else ""
            return y, m
        return "", ""

    title = soup.find("title").text.strip() if soup.find("title") else ""
    doi = soup.find("idno", type="DOI")
    doi = doi.text.strip() if doi else ""
    authors = [{"label": f"{p.find('forename').text.strip()} {p.find('surname').text.strip()}"} 
               for p in soup.find_all('author') 
               if p.find('forename') and p.find('surname')]
    date_tag = soup.find("date", type="published")
    year, month = extract_date(date_tag) if date_tag else ("", "")
    journal = soup.find("title", level="j")
    published_in = journal.text.strip() if journal else ""

    return {
        "title": title,
        "doi": doi,
        "authors": authors,
        "publicationYear": year,
        "publicationMonth": month,
        "publishedIn": published_in
    }

def append_structured_log(log_path: Path, paper_id: str, resource_entries: list):
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"paper_id": paper_id, "contributions": resource_entries}) + "\n")
    except Exception as e:
        print(f"⚠️ Failed to update structured log: {e}")

# ---------- Entry Point ----------
if __name__ == "__main__":
    host = input("Enter ORKG host URL (e.g., https://www.orkg.org/orkg): ").strip()
    email = input("Enter your ORKG email: ").strip()
    password = getpass("Enter your ORKG password: ").strip()

    print("🔗 Connecting to ORKG...")
    orkg = ORKG(host=host, creds=(email, password))
    print("✅ Connected.")

    template_id = input("Enter the ORKG template ID to use (e.g., R2028613): ").strip()
    orkg.templates.materialize_template(template_id)
    tp = orkg.templates

    data_folder = input("Enter the path to the folder with input JSON files: ").strip()
    log_dir = input("Enter the path to the folder where logs should be stored: ").strip()
    tei_folder = input("Enter the path to the folder with TEI XML files: ").strip()

    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)
    cache_path = log_dir_path / "resource_cache.json"
    paper_log_detailed_path = log_dir_path / "uploaded_papers_detailed.tsv"
    structured_log_path = log_dir_path / "structured_output_log.jsonl"

    resource_cache = load_resource_cache(cache_path)
    uploaded_titles = load_uploaded_titles(paper_log_detailed_path)
    tei_path = Path(tei_folder)
    data_path = Path(data_folder)

    for json_file in sorted(data_path.glob("*.json")):
        tei_file = tei_path / (Path(json_file.stem).stem + ".tei.xml")
        if not tei_file.exists():
            print(f"⚠️ TEI file not found: {tei_file.name}")
            continue

        metadata = extract_metadata(tei_file)

        if not metadata["title"]:
            print(f"⚠️ No title found in metadata for file: {tei_file.name}, skipping.")
            continue

        if metadata["title"] in uploaded_titles:
            print(f"⏩ Skipping already uploaded paper: {metadata['title']}")
            continue

        with open(json_file, 'r', encoding='utf-8') as f:
            entries = json.load(f)

        contributions = []
        counter = 1
        resource_entries = []

        for entry in entries:
            toc = entry["construct"].strip().lower()
            meas = entry["measured_by"].strip().lower()
            just = entry["justification"].strip()

            for label in [toc, meas]:
                if label and label not in resource_cache:
                    try:
                        response = orkg.resources.find_or_add(label=label)
                        resource_id = response.content["id"]
                        resource_cache[label] = resource_id
                        print(f"✅ Added/Found: '{label}' → {resource_id}")
                        save_resource_cache(resource_cache, cache_path)
                    except Exception as e:
                        print(f"❌ Failed to create/find resource for '{label}': {e}")

            toc_id = resource_cache.get(toc)
            meas_id = resource_cache.get(meas)

            if not toc_id or not meas_id:
                print(f"⚠️ Missing resource for '{toc}' or '{meas}'")
                continue

            c = tp.psychology_constructs_and_measurements(
                label=f"contribution {counter}",
                construct=OID(toc_id),
                measured_by=OID(meas_id),
                justification=just
            )
            contributions.append(c)

            resource_entries.append({
                "construct": toc_id,
                "measured_by": meas_id,
                "justification": just
            })

            print(f"✅ Created contribution {counter}")
            counter += 1

        paper = {
            "predicates": [],
            "paper": {
                "title": metadata["title"],
                "doi": metadata["doi"],
                "authors": metadata["authors"],
                "publicationMonth": metadata["publicationMonth"],
                "publicationYear": metadata["publicationYear"],
                "publishedIn": metadata["publishedIn"],
                "researchField": "R343",
                "contributions": [c.template_dict['resource'] for c in contributions]
            }
        }

        try:
            response = orkg.papers.add(params=paper)
            paper_id = response.content["id"]
            log_uploaded_paper_detailed(paper_log_detailed_path, metadata["title"], paper_id)
            append_structured_log(structured_log_path, paper_id, resource_entries)
            print(f"📄 Paper uploaded: {metadata['title']} → {paper_id}")
        except Exception as e:
            print(f"❌ Failed to upload paper: {e}")
