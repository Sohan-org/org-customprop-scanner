import requests
import pandas as pd
import os

GITHUB_ORG = os.getenv("MY_GITHUB_ORG")
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}

def get_all_repos(org):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error fetching repos: {response.status_code}, {response.text}")
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_custom_properties(org):
    url = f"https://api.github.com/orgs/{org}/properties/values"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching custom properties: {response.status_code}, {response.text}")
    return response.json()

def generate_excel_report(org):
    print("Fetching repositories...")
    repos = get_all_repos(org)
    print(f"Total repositories: {len(repos)}")

    print("Fetching custom properties...")
    custom_props_data = get_custom_properties(org)
    custom_props_map = {item["repository_id"]: item.get("properties", {}) for item in custom_props_data}

    records = []
    for repo in repos:
        repo_id = repo["id"]
        repo_name = repo["name"]
        record = {
            "Repository Name": repo_name,
            "Description": repo.get("description") or "",
            "Visibility": repo.get("visibility"),
            "Stars": repo.get("stargazers_count"),
            "Forks": repo.get("forks_count"),
            "Last Updated": repo.get("updated_at")
        }

        # Add custom properties if any
        custom_props = custom_props_map.get(repo_id, {})
        record.update(custom_props)

        records.append(record)

    print("Creating Excel report...")
    df = pd.DataFrame(records)
    df.to_excel("github_custom_properties.xlsx", index=False)
    print("✅ Report saved to github_custom_properties.xlsx")

if __name__ == "__main__":
    generate_excel_report(GITHUB_ORG)
