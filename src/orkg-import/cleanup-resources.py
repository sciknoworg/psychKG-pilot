import csv
from pathlib import Path
from getpass import getpass
from orkg import ORKG

def clean_orkg_resources(input_tsv_path: str, orkg: ORKG):
    input_path = Path(input_tsv_path)

    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        return

    with input_path.open('r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)

    cleaned_rows = []
    for index, row in enumerate(rows):
        if len(row) != 2:
            print(f"\n⚠️ Malformed row at line {index + 1}: {row}")
            while True:
                action = input("Options: [s]kip / [e]dit manually / [d]elete resource / [q]uit → ").strip().lower()
                if action == 's':
                    print("⏭️ Skipping row.")
                    break
                elif action == 'e':
                    new_title = input("Enter paper title: ").strip()
                    new_resource_id = input("Enter ORKG resource ID: ").strip()
                    if new_title and new_resource_id:
                        cleaned_rows.append([new_title, new_resource_id])
                    else:
                        print("⚠️ Incomplete input. Skipping this row.")
                    break
                elif action == 'd':
                    resource_id = input("Enter ORKG resource ID to delete: ").strip()
                    if resource_id:
                        try:
                            response = orkg.resources.delete(id=resource_id)
                            if response.status_code in (200, 204):
                                print(f"🗑️ Successfully deleted resource: {resource_id}")
                                continue  # Do not add to cleaned list
                            else:
                                print(f"⚠️ Failed to delete {resource_id}: {response.status_code}")
                        except Exception as e:
                            error_msg = str(e)
                            if "the provided id is not in the graph" in error_msg.lower():
                                print(f"ℹ️ Resource {resource_id} already deleted. Skipping.")
                                continue  # Do not add to cleaned list
                            else:
                                print(f"❌ Error deleting {resource_id}: {error_msg}")
                    else:
                        print("⚠️ No ID provided. Skipping deletion.")
                    break
                elif action == 'q':
                    print("👋 Exiting.")
                    return
                else:
                    print("Invalid option. Please type 's', 'e', 'd', or 'q'.")
            continue

        title = row[0].strip()
        resource_id = row[1].strip()

        if not title and resource_id:
            try:
                response = orkg.resources.delete(id=resource_id)
                if response.status_code in (200, 204):
                    print(f"🗑️ Successfully deleted resource: {resource_id}")
                    continue  # Do not add to cleaned list
                else:
                    print(f"⚠️ Failed to delete {resource_id}: {response.status_code}")
            except Exception as e:
                error_msg = str(e)
                if "the provided id is not in the graph" in error_msg.lower():
                    print(f"ℹ️ Resource {resource_id} already deleted. Skipping.")
                    continue  # Do not add to cleaned list
                else:
                    print(f"❌ Error deleting {resource_id}: {error_msg}")
        elif title and resource_id:
            cleaned_rows.append([title, resource_id])

    with input_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(cleaned_rows)

    print("\n✅ Cleaned TSV file written successfully.")

def main():
    host = input("Enter ORKG host URL (e.g., https://www.orkg.org/orkg): ").strip()
    email = input("Enter your ORKG email: ").strip()
    password = getpass("Enter your ORKG password: ").strip()

    print("🔗 Connecting to ORKG...")
    orkg = ORKG(host=host, creds=(email, password))
    print("✅ Connected.")

    input_file = input("Enter the path to your TSV file: ").strip()
    clean_orkg_resources(input_file, orkg)

if __name__ == "__main__":
    main()
