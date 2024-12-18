import base64
import requests
import os

def check_retrieve_transcript_db(title):
    # Specify GitHub credentials
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_OWNER = "Minh-Nguyen-0401" 
    REPO_NAME = "YT_RAG_Transcript_DB"
    FILE_PATH = f"data_trans/{title}.txt"

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    print(f"Searching for file {FILE_PATH}...")
    if response.status_code == 200:
        print(response.status_code)
        print("Found file. Downloading...")
        content = response.json()
        content = base64.b64decode(content["content"]).decode("utf-8")
        return content
    else:
        print(response.status_code)
        return "File not found"



def export_to_github(title, content):
    # Specify GitHub credentials
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_OWNER = "Minh-Nguyen-0401" 
    REPO_NAME = "YT_RAG_Transcript_DB"
    FILE_PATH = f"data_trans/{title}.txt"

    # Set up logic: if the file already exists, do nothing
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    print("Start uploading to github db repo...")
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    # GitHub API endpoint for creating a file
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    data = {
        "message": f"Add {title}.txt", 
        "content": encoded_content,  
        "branch": "main"             
    }

    # Make the PUT request
    response = requests.put(url, json=data, headers=headers)

    if response.status_code == 201:
        print("File added successfully!")
        print(f"File URL: {response.json()['content']['html_url']}")
    else:
        print("Failed to add the file.")
        print(f"Status Code: {response.status_code}")
        print(response.json())

