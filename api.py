import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from playwright.sync_api import sync_playwright
from google import genai

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="Agente Autónomo RPA API",
    description="API industrial de automatización web y procesamiento con IA",
    version="1.0"
)

# Configuración de seguridad CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# Conectamos el cliente moderno de Google GenAI SDK
cliente = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.get("/")
def home():
    return {"estado": "activo", "mensaje": "El microservicio del agente autónomo está listo para operar."}

@app.get("/ejecutar-agente")
def ejecutar_agente(url: str, objetivo: str = "Haz un resumen de esta página"):
    try:
        print(f"🕵️ [API] Entrando en la URL: {url}")
        
        # 1. NAVEGACIÓN UNIVERSAL CON PLAYWRIGHT
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Vamos a la web que pide el cliente (con tiempo extra por si es lenta)
            page.goto(url, timeout=60000)
            
            # Extraemos TODO el texto visible de la página (ignorando el código fuente oculto)
            texto_web = page.inner_text("body")
            browser.close()

        # Cortamos un poco el texto por si la web es gigantesca
        texto_limpio = texto_web[:20000] 
        
        print("🧠 [API] Procesando los datos extraídos con Gemini...")
        
        # 2. PROCESAMIENTO DINÁMICO CON GEMINI (Uso de cliente.models.generate_content)
        prompt = f"""
        Eres un agente de inteligencia corporativa de alto nivel.
        He extraído en bruto el texto de esta página web: {url}
        
        El cliente te ha dado esta orden exacta: "{objetivo}"
        
        Texto extraído de la web:
        ---
        {texto_limpio}
        ---
        
        Analiza el texto y cumple la orden del cliente. Ignora los menús de navegación, 
        cookies o textos basura. Devuelve la información limpia, directa y bien estructurada.
        """
        
        respuesta = cliente.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )

        return {
            "exito": True,
            "url_analizada": url,
            "objetivo_cliente": objetivo,
            "reporte_ia": respuesta.text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
