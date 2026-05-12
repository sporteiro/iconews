from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import feedparser

app = FastAPI()

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

@app.get("/")
def read_index():
    return FileResponse("templates/index.html")

app.mount("/", StaticFiles(directory="static"), name="static")