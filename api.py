import os
import time
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

def extraer_texto_infalible(url):
    jina_url = f"https://r.jina.ai/{url}"
    headers = {"Accept": "text/plain"}
    respuesta = requests.get(jina_url, headers=headers, timeout=20)
    respuesta.raise_for_status()
    return respuesta.text

@app.get("/")
def home():
    return {"estado": "activo", "mensaje": "API operativa con reintentos automáticos."}

@app.get("/ejecutar-agente")
def ejecutar_agente(url: str, objetivo: str = "Servicios de optimización digital"):
    try:
        print(f"🕵️ [API] Extrayendo mediante proxy: {url}")
        
        # 1. EXTRACCIÓN ANTI-BLOQUEOS
        try:
            texto_web = extraer_texto_infalible(url)
        except Exception as e_web:
            raise HTTPException(status_code=400, detail=f"Bloqueo absoluto en la web: {str(e_web)}")

        texto_limpio = texto_web[:15000]
        if not texto_limpio.strip():
            raise HTTPException(status_code=400, detail="La web no tiene texto legible.")
        
        # 2. IA B2B CON REINTENTOS AUTOMÁTICOS ANTE SATURACIÓN (503)
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
        
        respuesta = None
        for intento in range(3):
            try:
                respuesta = cliente.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                )
                if respuesta and respuesta.text:
                    break
            except Exception as e:
                print(f"⚠️ Reintento {intento + 1}/3 por alta demanda: {e}")
                time.sleep(3)

        if not respuesta or not respuesta.text:
            raise HTTPException(status_code=503, detail="El servicio de IA está saturado. Vuelve a darle al botón en unos segundos.")

        return {
            "exito": True,
            "url_analizada": url,
            "reporte_ia": respuesta.text
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
