import json
from pathlib import Path

def flatten_fields(entry):
    """Ensure 'construct' and 'measured_by' are strings, not lists."""
    for key in ["construct", "measured_by"]:
        if key in entry and isinstance(entry[key], list):
            entry[key] = " / ".join(entry[key])
    return entry

def update_json_files():
    folder_path = input("📂 Enter the path to the folder containing .tei.json files: ").strip()
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        print(f"❌ Invalid folder path: {folder}")
        return

    json_files = list(folder.glob("*.tei.json"))
    print(f"🔍 Found {len(json_files)} '.tei.json' files to process.")

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            updated_data = []
            for entry in data:
                # Rename key if needed
                if "topic_or_construct" in entry:
                    entry["construct"] = entry.pop("topic_or_construct")
                # Flatten list fields
                entry = flatten_fields(entry)
                updated_data.append(entry)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=2)

            print(f"✅ Updated: {file_path.name}")
        except Exception as e:
            print(f"❌ Failed to process {file_path.name}: {e}")

if __name__ == "__main__":
    update_json_files()
