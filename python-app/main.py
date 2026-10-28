import os
import asyncio
import httpx
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import feedparser
from openrouter_client import OpenRouterClient
from icon_cache import IconCache

app = FastAPI()

icon_cache = IconCache(cache_dir="static/icon-cache", max_size_mb=10)

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

STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "al", "a", "en", "y", "o", "u", "e", "que",
    "por", "para", "con", "sin", "sobre", "tras", "entre",
    "su", "sus", "es", "son", "fue", "ser", "ha", "han", "hay",
    "como", "mas", "pero", "ya", "muy", "no", "ni", "si",
    "the", "of", "in", "on", "and", "or", "to", "for", "with",
    "from", "by", "at", "as", "is", "are", "was", "were", "be",
    "been", "has", "have", "had", "this", "that", "these", "those",
    "it", "its", "an", "but", "not", "so", "if", "then",
    "than", "into", "over", "after", "before", "up", "down", "out",
}

COUNTRY_FLAGS = {
    "brasil": "br", "brazil": "br", "brazilian": "br", "brasileno": "br",
    "eeuu": "us", "usa": "us", "us": "us", "unitedstates": "us",
    "estadosunidos": "us", "america": "us", "norteamerica": "us",
    "estadounidense": "us", "american": "us", "americanos": "us",
    "espana": "es", "spain": "es", "espanol": "es", "espanola": "es", "spanish": "es",
    "argentina": "ar", "argentino": "ar", "argentinian": "ar",
    "mexico": "mx", "mexican": "mx", "mexicano": "mx",
    "colombia": "co", "colombian": "co", "colombiano": "co",
    "peru": "pe", "peruvian": "pe", "peruano": "pe",
    "chile": "cl", "chilean": "cl", "chileno": "cl",
    "ecuador": "ec", "ecuatoriano": "ec",
    "uruguay": "uy", "uruguayo": "uy",
    "venezuela": "ve", "venezolano": "ve",
    "italia": "it", "italy": "it", "italian": "it", "italiano": "it",
    "polonia": "pl", "poland": "pl", "polish": "pl", "polaco": "pl",
    "francia": "fr", "france": "fr", "french": "fr", "frances": "fr",
    "alemania": "de", "germany": "de", "german": "de", "aleman": "de",
    "reinounido": "gb", "uk": "gb", "unitedkingdom": "gb",
    "inglaterra": "gb", "england": "gb", "britain": "gb", "british": "gb",
    "britanico": "gb", "ingles": "gb",
    "china": "cn", "chinese": "cn", "chino": "cn",
    "japon": "jp", "japan": "jp", "japanese": "jp", "japones": "jp",
    "rusia": "ru", "russia": "ru", "russian": "ru", "ruso": "ru",
    "ucrania": "ua", "ukraine": "ua", "ukrainian": "ua", "ucraniano": "ua",
    "india": "in", "indian": "in", "indio": "in",
    "canada": "ca", "canadian": "ca", "canadiense": "ca",
    "australia": "au", "australian": "au", "australiano": "au",
    "portugal": "pt", "portuguese": "pt", "portugues": "pt",
    "grecia": "gr", "greece": "gr", "greek": "gr", "griego": "gr",
    "turquia": "tr", "turkey": "tr", "turkish": "tr", "turco": "tr",
    "israel": "il", "israeli": "il",
    "iran": "ir", "irani": "ir", "iranian": "ir",
    "irak": "iq", "iraq": "iq", "iraqi": "iq",
    "siria": "sy", "syria": "sy", "syrian": "sy", "sirio": "sy",
    "egipto": "eg", "egypt": "eg", "egyptian": "eg", "egipcio": "eg",
    "sudafrica": "za", "southafrica": "za",
    "marruecos": "ma", "morocco": "ma",
    "argelia": "dz", "algeria": "dz",
    "nigeria": "ng", "nigerian": "ng",
    "kenia": "ke", "kenya": "ke",
    "corea": "kr", "korea": "kr", "southkorea": "kr", "coreadelsur": "kr",
    "coreadelnorte": "kp", "northkorea": "kp",
    "taiwan": "tw", "taipei": "tw",
    "holanda": "nl", "netherlands": "nl", "dutch": "nl", "holandes": "nl",
    "belgica": "be", "belgium": "be", "belgian": "be", "belga": "be",
    "suiza": "ch", "switzerland": "ch", "swiss": "ch", "suizo": "ch",
    "austria": "at", "austrian": "at", "austriaco": "at",
    "suecia": "se", "sweden": "se", "swedish": "se", "sueco": "se",
    "noruega": "no", "norway": "no", "norwegian": "no", "noruego": "no",
    "dinamarca": "dk", "denmark": "dk", "danish": "dk", "danes": "dk",
    "finlandia": "fi", "finland": "fi", "finnish": "fi", "finlandes": "fi",
    "irlanda": "ie", "ireland": "ie", "irish": "ie", "irlandes": "ie",
    "polaco": "pl", "hungria": "hu", "hungary": "hu", "hungarian": "hu",
    "rumania": "ro", "romania": "ro", "rumano": "ro",
    "bulgaria": "bg", "bulgarian": "bg", "bulgaro": "bg",
    "croacia": "hr", "croatia": "hr", "croata": "hr",
    "serbia": "rs", "serbian": "rs", "serbio": "rs",
    "vaticano": "va", "vatican": "va",
}

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

async def fetch_from_iconify(icon_name: str) -> tuple[bool, str]:
    try:
        await asyncio.sleep(0.1)
        async with httpx.AsyncClient(timeout=10.0) as client:
            search_url = f"https://api.iconify.design/search?query={icon_name}&limit=1"
            search_response = await client.get(search_url)

            if search_response.status_code in (1015, 429):
                return False, "rate_limited"

            search_response.raise_for_status()
            search_data = search_response.json()

            if not search_data.get("icons") or len(search_data["icons"]) == 0:
                return False, "not_found"

            icon_name_found = search_data["icons"][0]

            await asyncio.sleep(0.1)

            svg_url = f"https://api.iconify.design/{icon_name_found}.svg"
            svg_response = await client.get(svg_url)

            if svg_response.status_code == 429:
                return False, "rate_limited"

            svg_response.raise_for_status()

            return True, svg_response.text

    except httpx.HTTPStatusError as e:
        if e.response.status_code in (1015, 429):
            return False, "rate_limited"
        return False, str(e)
    except Exception as e:
        return False, str(e)


FONT_AWESOME_MAPPING = {
    "police": "fa-solid fa-user-shield",
    "policia": "fa-solid fa-user-shield",
    "cop": "fa-solid fa-user-shield",
    "car": "fa-solid fa-car",
    "cars": "fa-solid fa-car",
    "auto": "fa-solid fa-car",
    "coche": "fa-solid fa-car",
    "vehicle": "fa-solid fa-car",
    "house": "fa-solid fa-house",
    "home": "fa-solid fa-house",
    "casa": "fa-solid fa-house",
    "user": "fa-solid fa-user",
    "usuario": "fa-solid fa-user",
    "money": "fa-solid fa-dollar-sign",
    "dinero": "fa-solid fa-coins",
    "euro": "fa-solid fa-euro-sign",
    "euros": "fa-solid fa-euro-sign",
    "dollar": "fa-solid fa-dollar-sign",
    "dollars": "fa-solid fa-dollar-sign",
    "salud": "fa-solid fa-heart-pulse",
    "health": "fa-solid fa-heart-pulse",
    "justice": "fa-solid fa-scale-balanced",
    "justicia": "fa-solid fa-scale-balanced",
    "court": "fa-solid fa-scale-balanced",
    "courtroom": "fa-solid fa-scale-balanced",
    "gobierno": "fa-solid fa-landmark",
    "government": "fa-solid fa-landmark",
    "election": "fa-solid fa-vote-yea",
    "elections": "fa-solid fa-vote-yea",
    "elecciones": "fa-solid fa-vote-yea",
    "vote": "fa-solid fa-vote-yea",
    "voting": "fa-solid fa-vote-yea",
    "war": "fa-solid fa-person-military-rifle",
    "guerra": "fa-solid fa-person-military-rifle",
    "peace": "fa-solid fa-dove",
    "paz": "fa-solid fa-dove",
    "fire": "fa-solid fa-fire",
    "fuego": "fa-solid fa-fire",
    "incendio": "fa-solid fa-fire",
    "water": "fa-solid fa-water",
    "agua": "fa-solid fa-water",
    "earth": "fa-solid fa-earth-americas",
    "tierra": "fa-solid fa-earth-americas",
    "world": "fa-solid fa-earth-americas",
    "mundo": "fa-solid fa-earth-americas",
    "weather": "fa-solid fa-cloud-sun",
    "clima": "fa-solid fa-cloud-sun",
    "news": "fa-solid fa-newspaper",
    "noticias": "fa-solid fa-newspaper",
    "tech": "fa-solid fa-microchip",
    "tecnologia": "fa-solid fa-microchip",
    "technology": "fa-solid fa-microchip",
    "phone": "fa-solid fa-phone",
    "telefono": "fa-solid fa-phone",
    "computer": "fa-solid fa-computer",
    "ordenador": "fa-solid fa-computer",
    "internet": "fa-solid fa-globe",
    "email": "fa-solid fa-envelope",
    "correo": "fa-solid fa-envelope",
    "calendar": "fa-solid fa-calendar",
    "calendario": "fa-solid fa-calendar",
    "clock": "fa-solid fa-clock",
    "reloj": "fa-solid fa-clock",
    "time": "fa-solid fa-clock",
    "tiempo": "fa-solid fa-clock",
    "camera": "fa-solid fa-camera",
    "camara": "fa-solid fa-camera",
    "photo": "fa-solid fa-image",
    "foto": "fa-solid fa-image",
    "video": "fa-solid fa-video",
    "music": "fa-solid fa-music",
    "musica": "fa-solid fa-music",
    "sport": "fa-solid fa-futbol",
    "sports": "fa-solid fa-futbol",
    "deporte": "fa-solid fa-futbol",
    "deportes": "fa-solid fa-futbol",
    "football": "fa-solid fa-futbol",
    "futbol": "fa-solid fa-futbol",
    "soccer": "fa-solid fa-futbol",
    "ball": "fa-solid fa-basketball",
    "pelota": "fa-solid fa-basketball",
    "food": "fa-solid fa-utensils",
    "comida": "fa-solid fa-utensils",
    "restaurant": "fa-solid fa-utensils",
    "school": "fa-solid fa-school",
    "escuela": "fa-solid fa-school",
    "education": "fa-solid fa-graduation-cap",
    "educacion": "fa-solid fa-graduation-cap",
    "book": "fa-solid fa-book",
    "libro": "fa-solid fa-book",
    "library": "fa-solid fa-book-open",
    "biblioteca": "fa-solid fa-book-open",
    "work": "fa-solid fa-briefcase",
    "trabajo": "fa-solid fa-briefcase",
    "job": "fa-solid fa-briefcase",
    "business": "fa-solid fa-building",
    "empresa": "fa-solid fa-building",
    "shop": "fa-solid fa-shop",
    "tienda": "fa-solid fa-shop",
    "store": "fa-solid fa-store",
    "market": "fa-solid fa-cart-shopping",
    "mercado": "fa-solid fa-cart-shopping",
    "bank": "fa-solid fa-building-columns",
    "banco": "fa-solid fa-building-columns",
    "banking": "fa-solid fa-building-columns",
    "cash": "fa-solid fa-money-bill",
    "gas": "fa-solid fa-gas-pump",
    "petroleo": "fa-solid fa-gas-pump",
    "oil": "fa-solid fa-oil-can",
    "energy": "fa-solid fa-bolt",
    "energia": "fa-solid fa-bolt",
    "power": "fa-solid fa-plug",
    "electric": "fa-solid fa-lightbulb",
    "electricidad": "fa-solid fa-lightbulb",
    "solar": "fa-solid fa-solar-panel",
    "wind": "fa-solid fa-wind",
    "viento": "fa-solid fa-wind",
    "forest": "fa-solid fa-tree",
    "bosque": "fa-solid fa-tree",
    "tree": "fa-solid fa-tree",
    "arbol": "fa-solid fa-tree",
    "city": "fa-solid fa-city",
    "ciudad": "fa-solid fa-city",
    "building": "fa-solid fa-building",
    "edificio": "fa-solid fa-building",
    "road": "fa-solid fa-road",
    "carretera": "fa-solid fa-road",
    "street": "fa-solid fa-road",
    "calle": "fa-solid fa-road",
    "traffic": "fa-solid fa-traffic-light",
    "trafico": "fa-solid fa-traffic-light",
    "plane": "fa-solid fa-plane",
    "avion": "fa-solid fa-plane",
    "aviacion": "fa-solid fa-plane",
    "airport": "fa-solid fa-plane-arrival",
    "aeropuerto": "fa-solid fa-plane-arrival",
    "train": "fa-solid fa-train",
    "tren": "fa-solid fa-train",
    "bus": "fa-solid fa-bus",
    "autobus": "fa-solid fa-bus",
    "ship": "fa-solid fa-ship",
    "barco": "fa-solid fa-ship",
    "boat": "fa-solid fa-ship",
    "bicycle": "fa-solid fa-bicycle",
    "bicicleta": "fa-solid fa-bicycle",
    "truck": "fa-solid fa-truck",
    "camion": "fa-solid fa-truck",
    "danger": "fa-solid fa-triangle-exclamation",
    "peligro": "fa-solid fa-triangle-exclamation",
    "warning": "fa-solid fa-triangle-exclamation",
    "alert": "fa-solid fa-bell",
    "alerta": "fa-solid fa-bell",
    "emergency": "fa-solid fa-truck-medical",
    "emergencia": "fa-solid fa-truck-medical",
    "hospital": "fa-solid fa-hospital",
    "doctor": "fa-solid fa-user-doctor",
    "medico": "fa-solid fa-user-doctor",
    "medicine": "fa-solid fa-pills",
    "medicina": "fa-solid fa-pills",
    "virus": "fa-solid fa-virus",
    "covid": "fa-solid fa-virus",
    "pandemic": "fa-solid fa-virus",
    "pandemia": "fa-solid fa-virus",
    "sick": "fa-solid fa-bed-pulse",
    "enfermo": "fa-solid fa-bed-pulse",
    "protection": "fa-solid fa-shield-halved",
    "proteccion": "fa-solid fa-shield-halved",
    "security": "fa-solid fa-lock",
    "seguridad": "fa-solid fa-lock",
    "crime": "fa-solid fa-handcuffs",
    "crimen": "fa-solid fa-handcuffs",
    "prison": "fa-solid fa-dungeon",
    "prision": "fa-solid fa-dungeon",
    "jail": "fa-solid fa-dungeon",
    "carcel": "fa-solid fa-dungeon",
    "dead": "fa-solid fa-skull",
    "muerto": "fa-solid fa-skull",
    "death": "fa-solid fa-skull",
    "muerte": "fa-solid fa-skull",
    "grave": "fa-solid fa-monument",
    "tumba": "fa-solid fa-monument",
    "wedding": "fa-solid fa-rings-wedding",
    "boda": "fa-solid fa-rings-wedding",
    "marriage": "fa-solid fa-rings-wedding",
    "matrimonio": "fa-solid fa-rings-wedding",
    "family": "fa-solid fa-people-group",
    "familia": "fa-solid fa-people-group",
    "child": "fa-solid fa-child",
    "nino": "fa-solid fa-child",
    "baby": "fa-solid fa-baby",
    "bebe": "fa-solid fa-baby",
    "man": "fa-solid fa-person",
    "hombre": "fa-solid fa-person",
    "woman": "fa-solid fa-person-dress",
    "mujer": "fa-solid fa-person-dress",
    "dog": "fa-solid fa-dog",
    "perro": "fa-solid fa-dog",
    "cat": "fa-solid fa-cat",
    "gato": "fa-solid fa-cat",
    "bird": "fa-solid fa-dove",
    "pajaro": "fa-solid fa-dove",
    "animal": "fa-solid fa-paw",
    "animals": "fa-solid fa-paw",
    "president": "fa-solid fa-user-tie",
    "presidente": "fa-solid fa-user-tie",
    "minister": "fa-solid fa-user-tie",
    "ministro": "fa-solid fa-user-tie",
    "king": "fa-solid fa-crown",
    "rey": "fa-solid fa-crown",
    "queen": "fa-solid fa-crown",
    "reina": "fa-solid fa-crown",
    "pope": "fa-solid fa-cross",
    "papa": "fa-solid fa-cross",
    "vatican": "fa-solid fa-cross",
    "church": "fa-solid fa-church",
    "iglesia": "fa-solid fa-church",
    "meeting": "fa-solid fa-handshake",
    "reunion": "fa-solid fa-handshake",
    "summit": "fa-solid fa-handshake",
    "cumbre": "fa-solid fa-handshake",
    "agreement": "fa-solid fa-file-signature",
    "acuerdo": "fa-solid fa-file-signature",
    "treaty": "fa-solid fa-file-signature",
    "tratado": "fa-solid fa-file-signature",
    "law": "fa-solid fa-gavel",
    "ley": "fa-solid fa-gavel",
    "judge": "fa-solid fa-gavel",
    "juez": "fa-solid fa-gavel",
    "trade": "fa-solid fa-arrows-rotate",
    "comercio": "fa-solid fa-arrows-rotate",
    "tariff": "fa-solid fa-percent",
    "arancel": "fa-solid fa-percent",
    "sanction": "fa-solid fa-ban",
    "sancion": "fa-solid fa-ban",
    "economy": "fa-solid fa-chart-line",
    "economia": "fa-solid fa-chart-line",
    "inflation": "fa-solid fa-arrow-trend-up",
    "inflacion": "fa-solid fa-arrow-trend-up",
    "stock": "fa-solid fa-chart-line",
    "stocks": "fa-solid fa-chart-line",
    "crypto": "fa-solid fa-bitcoin-sign",
    "bitcoin": "fa-solid fa-bitcoin-sign",
    "strike": "fa-solid fa-hand-fist",
    "huelga": "fa-solid fa-hand-fist",
    "protest": "fa-solid fa-hand-fist",
    "protesta": "fa-solid fa-hand-fist",
    "refugee": "fa-solid fa-person-walking-arrow-right",
    "refugiado": "fa-solid fa-person-walking-arrow-right",
    "migrant": "fa-solid fa-person-walking-arrow-right",
    "migrante": "fa-solid fa-person-walking-arrow-right",
    "border": "fa-solid fa-border-all",
    "frontera": "fa-solid fa-border-all",
    "attack": "fa-solid fa-burst",
    "ataque": "fa-solid fa-burst",
    "terrorism": "fa-solid fa-burst",
    "terrorismo": "fa-solid fa-burst",
    "bomb": "fa-solid fa-bomb",
    "bomba": "fa-solid fa-bomb",
    "explosion": "fa-solid fa-bomb",
    "missile": "fa-solid fa-rocket",
    "misil": "fa-solid fa-rocket",
    "rocket": "fa-solid fa-rocket",
    "cohete": "fa-solid fa-rocket",
    "space": "fa-solid fa-rocket",
    "espacio": "fa-solid fa-rocket",
    "moon": "fa-solid fa-moon",
    "luna": "fa-solid fa-moon",
    "sun": "fa-solid fa-sun",
    "sol": "fa-solid fa-sun",
    "star": "fa-solid fa-star",
    "estrella": "fa-solid fa-star",
    "rain": "fa-solid fa-cloud-rain",
    "lluvia": "fa-solid fa-cloud-rain",
    "storm": "fa-solid fa-cloud-bolt",
    "tormenta": "fa-solid fa-cloud-bolt",
    "snow": "fa-solid fa-snowflake",
    "nieve": "fa-solid fa-snowflake",
    "heat": "fa-solid fa-temperature-high",
    "calor": "fa-solid fa-temperature-high",
    "cold": "fa-solid fa-temperature-low",
    "frio": "fa-solid fa-temperature-low",
    "heart": "fa-solid fa-heart",
    "corazon": "fa-solid fa-heart",
    "brain": "fa-solid fa-brain",
    "cerebro": "fa-solid fa-brain",
    "cancer": "fa-solid fa-ribbon",
    "vaccine": "fa-solid fa-syringe",
    "vacuna": "fa-solid fa-syringe",
    "surgery": "fa-solid fa-syringe",
    "cirugia": "fa-solid fa-syringe",
    "passport": "fa-solid fa-passport",
    "pasaporte": "fa-solid fa-passport",
    "cancel": "fa-solid fa-ban",
    "cancelar": "fa-solid fa-ban",
    "cancelado": "fa-solid fa-ban",
    "canceled": "fa-solid fa-ban",
    "cancelled": "fa-solid fa-ban",
    "arrival": "fa-solid fa-plane-arrival",
    "arrive": "fa-solid fa-plane-arrival",
    "arrives": "fa-solid fa-plane-arrival",
    "llega": "fa-solid fa-plane-arrival",
    "llegar": "fa-solid fa-plane-arrival",
    "llegada": "fa-solid fa-plane-arrival",
    "departure": "fa-solid fa-plane-departure",
    "salida": "fa-solid fa-plane-departure",
}


def normalize_text(text: str) -> str:
    return (
        text.strip().lower()
        .replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u").replace("ñ", "n")
        .replace("ü", "u")
    )


def get_font_awesome_icon(icon_name: str) -> str:
    if not icon_name:
        return None

    name = icon_name.strip().lower()

    if name in STOPWORDS:
        return None

    normalized = normalize_text(name)

    if normalized in STOPWORDS:
        return None

    if len(normalized) < 3:
        return None

    return FONT_AWESOME_MAPPING.get(normalized)


def get_country_flag(icon_name: str) -> str:
    if not icon_name:
        return None

    normalized = normalize_text(icon_name)
    normalized = "".join(ch for ch in normalized if ch.isalnum())

    if len(normalized) < 2:
        return None

    if normalized in STOPWORDS:
        return None

    return COUNTRY_FLAGS.get(normalized)


async def fetch_from_iconstack(icon_name: str) -> tuple[bool, str]:
    try:
        fa_class = get_font_awesome_icon(icon_name)
        if fa_class:
            return True, fa_class
        return False, "not_found"
    except Exception as e:
        return False, str(e)


@app.get("/get-icon/{icon_name}")
async def get_icon(icon_name: str):
    safe_name = os.path.basename(icon_name)
    if not safe_name or "/" in safe_name or "\\" in safe_name or ".." in safe_name:
        return {"source": "none"}

    cached_path = icon_cache.get(safe_name)
    if cached_path:
        return {"source": "cached", "url": f"/icon-cache/{safe_name}.svg"}

    country_code = get_country_flag(safe_name)
    if country_code:
        flag_path = f"static/country-flags-main/svg/{country_code}.svg"
        if os.path.exists(flag_path):
            return {"source": "local", "url": f"/country-flags-main/svg/{country_code}.svg"}

    local_png = f"static/img/{safe_name}.png"
    if os.path.exists(local_png):
        return {"source": "local", "url": f"/img/{safe_name}.png"}

    fa_class = get_font_awesome_icon(safe_name)
    if fa_class:
        return {"source": "fontawesome", "class": fa_class}

    success, content = await fetch_from_iconify(safe_name)
    if success:
        icon_cache.put(safe_name, content)
        return {"source": "cached", "url": f"/icon-cache/{safe_name}.svg"}

    return {"source": "none"}

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