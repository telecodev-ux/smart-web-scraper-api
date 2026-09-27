from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup

# Inicializamos la API
app = FastAPI(
    title="Smart Web Scraper API", 
    description="API para extraer encabezados y enlaces de cualquier URL"
)

# Creamos el punto de acceso (endpoint)
@app.get("/extraer/")
def extraer_datos(url: str):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="La URL debe empezar por http:// o https://")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="No se pudo acceder a la web")
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. Extraer Encabezados
        headings = []
        for tag in ["h1", "h2", "h3"]:
            for item in soup.find_all(tag):
                text = item.get_text(strip=True)
                if text:
                    headings.append({"etiqueta": tag.upper(), "texto": text})
                    
        # 2. Extraer Enlaces
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if href.startswith("http"):
                links.append({"texto": text or "Sin Texto", "url": href})
                
        # La API devuelve los datos estructurados (JSON)
        return {
            "estado": "exito",
            "url_analizada": url,
            "total_encabezados": len(headings),
            "total_enlaces": len(links),
            "datos": {
                "encabezados": headings,
                "enlaces": links
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
