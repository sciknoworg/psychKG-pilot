import os
from pathlib import Path
from bs4 import BeautifulSoup

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

def find_title_in_folder(folder_path: str, target_title: str):
    folder = Path(folder_path)
    target_title_lower = target_title.lower()

    for file_path in folder.glob("*.xml"):
        try:
            metadata = extract_metadata(file_path)
            title = metadata.get("title", "")
            if title.lower() == target_title_lower:
                print(f"✅ Match found: {file_path.name}")
                return file_path.name
        except Exception as e:
            print(f"⚠️ Error processing {file_path.name}: {e}")

    print("❌ No match found.")
    return None

# Example usage
folder_path = "C:/Users/dsouzaj/Desktop/Datasets/psychKG-pilot/data/papers_input_tei_xml"
target_title = "Decision Making Under Extinction Risk"
find_title_in_folder(folder_path, target_title)
