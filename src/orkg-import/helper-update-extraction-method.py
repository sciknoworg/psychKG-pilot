import requests
from getpass import getpass
from pathlib import Path

# --- CONFIG ---
BASE_URL = "https://orkg.org"
TOKEN_URL = f"{BASE_URL}/oauth/token"
LIST_ENDPOINT = "/api/papers/"
RESOURCE_UPDATE_ENDPOINT = f"{BASE_URL}/api/resources/{{resource_id}}"

CLIENT_ID = "orkg-client"
CLIENT_SECRET = "secret"
CACHE_FILE = Path("updated_contributions.txt")

HEADERS = {}
updated_ids = set()


def load_updated_ids():
    if CACHE_FILE.exists():
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def log_updated_id(contribution_id):
    with CACHE_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{contribution_id}\n")


def get_new_token():
    print("🔐 Access token expired or not set. Please authenticate.")
    username = input("ORKG email: ").strip()
    password = getpass("ORKG password: ").strip()

    response = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "password",
            "username": username,
            "password": password
        },
        headers={"Accept": "application/json"}
    )

    if response.status_code != 200:
        print(f"❌ Failed to get access token: {response.status_code}")
        print(response.text)
        exit(1)

    token = response.json()["access_token"]
    print("✅ New access token acquired.")
    return token


def set_headers(token):
    global PAPER_HEADERS, RESOURCE_HEADERS
    PAPER_HEADERS = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.orkg.paper.v2+json;charset=UTF-8",
        "Accept": "application/vnd.orkg.paper.v2+json"
    }
    RESOURCE_HEADERS = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json"
    }


def update_contribution_extraction_method(contribution_id):
    if contribution_id in updated_ids:
        print(f"⏩ Skipping already updated contribution {contribution_id}")
        return

    url = RESOURCE_UPDATE_ENDPOINT.format(resource_id=contribution_id)
    payload = {"extraction_method": "AUTOMATIC"}

    try:
        response = requests.put(url, headers=RESOURCE_HEADERS, json=payload, timeout=(30, 15))
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error for {contribution_id}: {e}")
        return

    if 200 <= response.status_code < 300:
        print(f"✅ Updated contribution {contribution_id}")
        updated_ids.add(contribution_id)
        log_updated_id(contribution_id)
    elif response.status_code == 401:
        print(f"🔁 Token expired while updating {contribution_id}. Re-authenticating...")
        token = get_new_token()
        set_headers(token)
        update_contribution_extraction_method(contribution_id)
    else:
        print(f"❌ Failed to update {contribution_id} ({response.status_code}): {response.text}")


params = {
    "page": 0,
    "size": 30,
    "sort": "created_at,desc",
    "visibility": "NON_FEATURED",
    "created_by": "3a55ad95-645b-4c1f-b614-d2293718ee0b",
    "research_field": "R343",
    "created_at_start": "2025-07-06T00:00:00Z"
}


def main():
    global updated_ids
    updated_ids = load_updated_ids()

    token = input("🔐 Enter your ORKG access token (or leave blank to login): ").strip()
    if not token:
        token = get_new_token()
    set_headers(token)

    while True:
        try:
            response = requests.get(f"{BASE_URL}{LIST_ENDPOINT}", params=params, headers=PAPER_HEADERS, timeout=(30, 15))
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch papers: {e}")
            break

        if response.status_code == 401:
            print("🔁 Token expired while fetching papers. Re-authenticating...")
            token = get_new_token()
            set_headers(token)
            continue
        elif response.status_code != 200:
            print(f"❌ Failed to fetch papers: {response.status_code}")
            break

        data = response.json()
        papers = data.get("content", [])
        if not papers:
            print("✅ No more papers to process.")
            break

        for paper in papers:
            contributions = paper.get("contributions", [])
            for contribution in contributions:
                contribution_id = contribution.get("id")
                if contribution_id:
                    update_contribution_extraction_method(contribution_id)

        if data.get("last", True):
            break

        params["page"] += 1


if __name__ == "__main__":
    main()
