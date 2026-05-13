import os
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import feedparser
from openrouter_client import OpenRouterClient

app = FastAPI()

try:
    ai_client = OpenRouterClient()
except EnvironmentError:
    ai_client = None

COUNTRIES = [
    {"code": "ES", "name": "España"},
    {"code": "AR", "name": "Argentina"},
    {"code": "MX", "name": "México"},
    {"code": "CO", "name": "Colombia"},
    {"code": "PE", "name": "Perú"},
    {"code": "CL", "name": "Chile"},
    {"code": "EC", "name": "Ecuador"},
    {"code": "UY", "name": "Uruguay"},
    {"code": "VE", "name": "Venezuela"},
    {"code": "IT", "name": "Italia"},
    {"code": "PL", "name": "Polonia"},
]

@app.get("/countries")
def get_countries():
    return COUNTRIES

@app.get("/news")
def get_news(cc: str = Query("ES")):
    url = f"https://news.google.com/rss?hl=es&gl={cc}&ceid={cc}:es-419"
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:20]:
            items.append({
                "title": entry.title,
                "description": entry.get("description", ""),
                "link": entry.link
            })
        return items
    except Exception as e:
        return {"error": str(e)}

@app.get("/get-icon/{icon_name}")
async def get_icon(icon_name: str):
    local_png = f"static/img/{icon_name}.png"
    if os.path.exists(local_png):
        return {"source": "local", "url": f"/img/{icon_name}.png"}
    return {"source": "remote", "query": icon_name}

@app.get("/ai-icons")
async def ai_icons(title: str = Query(...)):
    if not ai_client:
        return {"keywords": []}
    keywords = await ai_client.get_icon_keywords(title)
    return {"keywords": keywords}

@app.get("/")
def read_index():
    return FileResponse("templates/index.html")

app.mount("/", StaticFiles(directory="static"), name="static")