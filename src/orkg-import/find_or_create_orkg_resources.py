from orkg import ORKG
from pathlib import Path
from getpass import getpass

# --- Get input from user ---
host = input("Enter ORKG host URL (e.g., https://www.orkg.org/orkg): ").strip()
email = input("Enter your ORKG email: ").strip()
password = getpass("Enter your ORKG password: ").strip()
input_path = input("Enter the path to the input file (one label per line): ").strip()

# --- Validate input file ---
input_file = Path(input_path)
if not input_file.exists():
    print(f"❌ Input file '{input_path}' does not exist.")
    exit(1)

# --- Derive output file path ---
output_file = input_file.with_name("output_resources.tsv")

# --- Connect to ORKG instance ---
print("🔗 Connecting to ORKG...")
orkg = ORKG(host=host, creds=(email, password))
print("✅ Connected.")

# --- Read names ---
with open(input_file, 'r', encoding='utf-8') as f:
    names = [line.strip() for line in f if line.strip()]

# --- Process names ---
with open(output_file, 'w', encoding='utf-8') as out_file:
    out_file.write("name\tresource_id\n")
    for name in names:
        try:
            resource = orkg.resources.find_or_add(label=name)
            out_file.write(f"{name}\t{resource.id}\n")
            print(f"✅ {name} -> {resource.id}")
        except Exception as e:
            print(f"❌ Failed for '{name}': {e}")

print(f"\n📁 Done! Output written to: {output_file.resolve()}")
