import os
import re
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from google import genai

app = FastAPI(
    title="Agente Autónomo RPA API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

cliente = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def extraer_texto_rapido(url):
    # Cabeceras para simular un navegador real sin abrirlo visualmente
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9"
    }
    # Petición ultrarrápida con límite de 10 segundos
    respuesta = requests.get(url, headers=headers, timeout=10)
    respuesta.raise_for_status()
    
    # Limpieza estructural para extraer solo el texto legible
    html = respuesta.text
    html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    texto = re.sub(r'<[^>]+>', ' ', html)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

@app.get("/")
def home():
    return {"estado": "activo", "mensaje": "API operativa y ligera."}

@app.get("/ejecutar-agente")
def ejecutar_agente(url: str, objetivo: str = "Servicios de optimización digital"):
    try:
        print(f"🕵️ [API] Extrayendo al instante: {url}")
        
        # 1. EXTRACCIÓN LIGERA Y RÁPIDA (Sin bloqueos de RAM)
        try:
            texto_web = extraer_texto_rapido(url)
        except Exception as e_web:
            raise HTTPException(status_code=400, detail=f"Error de conexión con la web: {str(e_web)}")

        texto_limpio = texto_web[:15000]
        if not texto_limpio.strip():
            raise HTTPException(status_code=400, detail="La web no tiene texto legible.")
        
        # 2. IA B2B CON GEMINI
        prompt = f"""
        Eres un Director Comercial (SDR) experto en B2B. 
        He extraído este texto de una empresa objetivo: {url}
        Servicio a vender: "{objetivo}"
        
        Texto web:
        ---
        {texto_limpio}
        ---
        
        Analiza y devuelve ÚNICAMENTE código JSON válido con esta estructura exacta, sin marcas markdown ni texto extra:
        {{
            "nombre_empresa": "Nombre de la empresa",
            "a_que_se_dedican": "Resumen en 1 frase",
            "angulo_de_venta": "Justificación táctica",
            "asunto_email": "Asunto corto",
            "borrador_email": "Email hiper-personalizado de 3 párrafos."
        }}
        """
        
        respuesta = cliente.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )

        return {
            "exito": True,
            "url_analizada": url,
            "reporte_ia": respuesta.text
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
