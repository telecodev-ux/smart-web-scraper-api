import os
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
    # Usamos Jina Reader para saltarnos los bloqueos de IP corporativos
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        "Accept": "text/plain"
    }
    # Jina hace el trabajo duro, le damos 20 segundos
    respuesta = requests.get(jina_url, headers=headers, timeout=20)
    respuesta.raise_for_status()
    return respuesta.text

@app.get("/")
def home():
    return {"estado": "activo", "mensaje": "API operativa con motor antibloqueos."}

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
        
        # 2. IA B2B CON GEMINI (VERSIÓN 3.8)
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
        
        # Restaurado el modelo correcto que admite tu cuenta de Google
        respuesta = cliente.models.generate_content(
            model="gemini-3.8-flash",
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
