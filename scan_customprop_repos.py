import requests
import pandas as pd
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = os.getenv("GITHUB_ORG")
PROPERTY_NAME = "your-property-name"  # Replace with your actual custom property name

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

REPOS_API_URL = f"https://api.github.com/orgs/{ORG_NAME}/repos"
CUSTOM_PROP_VALUES_API_URL = f"https://api.github.com/orgs/{ORG_NAME}/custom-property-values"

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

def get_custom_property_values(property_name):
    values = {}
    page = 1
    while True:
        params = {
            "property_name": property_name,
            "per_page": 100,
            "page": page
        }
        response = requests.get(CUSTOM_PROP_VALUES_API_URL, headers=HEADERS, params=params)
        if response.status_code != 200:
            print("Error fetching custom property values:", response.status_code, response.text)
            break
        data = response.json()
        if not data:
            break
        for item in data:
            repo_name = item["repository"]["name"]
            values[repo_name] = item.get("value")
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

    custom_prop_values = get_custom_property_values(PROPERTY_NAME)

    for repo in repos:
        repo_name = repo["Name"]
        repo["Custom Property Value"] = custom_prop_values.get(repo_name, None)

    save_to_excel(repos)
    print("Report saved as repos_report_with_custom_properties.xlsx")
