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
      # 2. PROCESAMIENTO COMERCIAL B2B CON GEMINI
        prompt = f"""
        Eres un Director Comercial (SDR) experto en B2B de alto nivel.
        He extraído el texto en bruto de la web de una empresa objetivo: {url}
        
        Nuestra empresa ofrece este servicio/producto: "{objetivo}"
        
        Texto extraído de la web objetivo:
        ---
        {texto_limpio}
        ---
        
        Analiza a esta empresa y redacta una estrategia de contacto en formato JSON estricto. 
        Devuelve ÚNICAMENTE código JSON válido con esta estructura exacta, sin texto adicional:
        {{
            "nombre_empresa": "Nombre comercial detectado",
            "a_que_se_dedican": "Resumen de su modelo de negocio en 1 frase",
            "angulo_de_venta": "Justificación estratégica de por qué necesitan nuestro servicio",
            "asunto_email": "Un asunto corto, intrigante y no comercial (máx 5 palabras)",
            "borrador_email": "Email directo de 3 párrafos cortos. Primer párrafo: rompehielos hiper-personalizado sobre algo específico de su web. Segundo párrafo: el valor de nuestro servicio. Tercer párrafo: llamada a la acción de baja fricción."
        }}
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
