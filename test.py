import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
OWNER = os.getenv("OWNER")
REPO = os.getenv("REPO")
BRANCH = os.getenv("BRANCH")
FILE_PATH = "index.html"

# Example HTML content
content = "<!DOCTYPE html><html><body><h1>Hello</h1></body></html>"
content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

# Endpoint for file
url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Step 1: Check if file exists to get sha
r = requests.get(url, headers=headers, params={"ref": BRANCH})
sha = None
if r.status_code == 200:
    sha = r.json()["sha"]

# Step 2: Prepare payload
data = {
    "message": "Update index.html via script",
    "content": content_b64,
    "branch": BRANCH,
    "committer": {"name": "Python Bot", "email": "bot@example.com"}
}
if sha:
    data["sha"] = sha  # required if file exists

# Step 3: Upload (create or update)
response = requests.put(url, headers=headers, json=data)

if response.status_code in (200, 201):
    print("✅ index.html updated successfully!")
else:
    print("❌ Failed:", response.status_code, response.text)
