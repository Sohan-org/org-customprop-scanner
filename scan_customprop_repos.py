import requests
import pandas as pd
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = os.getenv("GITHUB_ORG")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

REPOS_API_URL = f"https://api.github.com/orgs/{ORG_NAME}/repos"
CUSTOM_PROP_API_URL = f"https://api.github.com/orgs/{ORG_NAME}/properties/values/repositories"

def get_repos():
    repos = []
    page = 1
    while True:
        response = requests.get(REPOS_API_URL, headers=HEADERS, params={"per_page": 100, "page": page})
        if response.status_code != 200:
            print("Error fetching repos:", response.status_code, response.text)
            break
        data = response.json()
        if not data:
            break
        for repo in data:
            repos.append({
                "ID": repo["id"],
                "Name": repo["name"],
                "Visibility": "Private" if repo["private"] else "Public",
                "Fork": repo["fork"],
                "URL": repo["html_url"],
                "Last Updated": repo["updated_at"]
            })
        page += 1
    return repos

def get_all_custom_property_values():
    values = {}
    page = 1
    while True:
        response = requests.get(CUSTOM_PROP_API_URL, headers=HEADERS, params={"per_page": 100, "page": page})
        if response.status_code != 200:
            print("Error fetching custom properties:", response.status_code, response.text)
            break
        data = response.json()
        if not data:
            break
        for item in data:
            repo_id = item["repository_id"]
            props = {p["property_name"]: p["value"] for p in item.get("properties", [])}
            values[repo_id] = props
        page += 1
    return values

def save_to_excel(data):
    df = pd.DataFrame(data)
    df.to_excel("repos_report_with_custom_properties.xlsx", index=False)

if __name__ == "__main__":
    repos = get_repos()
    if not repos:
        print("No repositories found or error occurred.")
        exit(1)

    custom_prop_map = get_all_custom_property_values()

    for repo in repos:
        repo_id = repo["ID"]
        custom_props = custom_prop_map.get(repo_id, {})
        repo.update(custom_props)

    # Remove internal ID before saving
    for repo in repos:
        repo.pop("ID", None)

    save_to_excel(repos)
    print("✅ Report saved as repos_report_with_custom_properties.xlsx")
