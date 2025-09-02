from fastapi import FastAPI, Header, HTTPException, Body
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
import base64
import requests

# Load .env
load_dotenv()

# Env vars
TOKEN = os.getenv("TOKEN")       # GitHub PAT with Contents: write
OWNER = os.getenv("OWNER")       # e.g. "Receptional736"
REPO = os.getenv("REPO")         # e.g. "tv_screen"
BRANCH = os.getenv("BRANCH")     # e.g. "main"
API_TOKEN = os.getenv("API_TOKEN", "super-secret")  # for protecting /update

FILE_PATH = "index.html"
LOCAL_HTML_FILE = "index.html"

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve local index.html"""
    try:
        with open(LOCAL_HTML_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>No index.html found</h1>"


@app.put("/update")
async def update_html(
    html: str = Body(..., media_type="text/plain", description="HTML content to update")
):
    """
    Accept plain text/HTML directly as a string parameter
    """
    
    # === Optional: Check authorization ===
    # if authorization != f"Bearer {API_TOKEN}":
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Use the html parameter directly
    html_str = html
    
    if not html_str:
        raise HTTPException(status_code=400, detail="HTML content cannot be empty")
    
    # === 1. Update local file ===
    try:
        with open(LOCAL_HTML_FILE, "w", encoding="utf-8") as f:
            f.write(html_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update local file: {str(e)}")
    
    # === 2. Base64 encode for GitHub ===
    content_b64 = base64.b64encode(html_str.encode("utf-8")).decode("utf-8")
    
    # === 3. GitHub API ===
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    # Check if file exists (need sha if updating)
    r = requests.get(url, headers=headers, params={"ref": BRANCH})
    sha = r.json().get("sha") if r.status_code == 200 else None
    
    # Prepare payload
    data = {
        "message": "Update index.html via FastAPI",
        "content": content_b64,
        "branch": BRANCH,
        "committer": {"name": "FastAPI Bot", "email": "bot@example.com"}
    }
    if sha:
        data["sha"] = sha
    
    # Send PUT to GitHub
    response = requests.put(url, headers=headers, json=data)
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=f"GitHub update failed: {response.text}")
    
    return {
        "status": "ok",
        "message": "index.html updated on GitHub & locally",
        "html_length": len(html_str)
    }