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
ALL_PROPERTIES_URL = f"https://api.github.com/orgs/{ORG_NAME}/properties/schema"
PROP_VALUES_URL = f"https://api.github.com/orgs/{ORG_NAME}/custom-property-values"

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
                "Name": repo["name"],
                "Visibility": "Private" if repo["private"] else "Public",
                "Fork": repo["fork"],
                "URL": repo["html_url"],
                "Last Updated": repo["updated_at"]
            })
        page += 1
    return repos

def get_all_custom_properties():
    response = requests.get(ALL_PROPERTIES_URL, headers=HEADERS)
    if response.status_code != 200:
        print("Error fetching custom properties:", response.status_code, response.text)
        return []
    return response.json()

def get_all_property_values():
    values = {}
    page = 1
    while True:
        response = requests.get(PROP_VALUES_URL, headers=HEADERS, params={"per_page": 100, "page": page})
        if response.status_code != 200:
            print("Error fetching custom property values:", response.status_code, response.text)
            break
        data = response.json()
        if not data:
            break
        for item in data:
            repo_name = item["repository"]["name"]
            prop_name = item["property"]["name"]
            value = item.get("value")
            if repo_name not in values:
                values[repo_name] = {}
            values[repo_name][prop_name] = value
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

    all_property_values = get_all_property_values()

    for repo in repos:
        repo_name = repo["Name"]
        custom_props = all_property_values.get(repo_name, {})
        for key, value in custom_props.items():
            repo[f"Custom: {key}"] = value

    save_to_excel(repos)
    print("✅ Report saved as repos_report_with_custom_properties.xlsx")
