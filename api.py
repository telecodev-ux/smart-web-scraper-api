import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from playwright.sync_api import sync_playwright
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

@app.get("/")
def home():
    return {"estado": "activo", "mensaje": "El microservicio del agente autónomo está listo para operar."}

@app.get("/ejecutar-agente")
def ejecutar_agente(url: str, objetivo: str = "Servicios de optimización digital"):
    try:
        print(f"🕵️ [API] Entrando en la URL: {url}")
        
        # 1. SCRAPING ULTRARRÁPIDO CON PLAYWRIGHT
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Bloqueamos imágenes, fuentes y CSS para acelerar la carga x10
            page = context.new_page()
            page.route("**/*.{png,jpg,jpeg,svg,css,woff,woff2}", lambda route: route.abort())
            
            try:
                # Solo esperamos a que el texto/DOM esté listo (máx 15s)
                page.goto(url, timeout=15000, wait_until="domcontentloaded")
                texto_web = page.inner_text("body")
            except Exception as e_web:
                browser.close()
                raise HTTPException(status_code=400, detail=f"Error cargando la web objetivo: {str(e_web)}")
            
            browser.close()

        texto_limpio = texto_web[:15000]
        if not texto_limpio.strip():
            raise HTTPException(status_code=400, detail="La web no devolvió texto accesible.")

        print("🧠 [API] Procesando estrategia comercial con Gemini...")
        
        prompt = f"""
        Eres un Director Comercial (SDR) experto en B2B de alto nivel.
        He extraído el texto en bruto de la web de una empresa objetivo: {url}
        
        Nuestra empresa ofrece este servicio/producto: "{objetivo}"
        
        Texto extraído de la web objetivo:
        ---
        {texto_limpio}
        ---
        
        Analiza a esta empresa y redacta una estrategia de contacto en formato JSON estricto. 
        Devuelve ÚNICAMENTE código JSON válido con esta estructura exacta, sin texto adicional ni bloques markdown:
        {{
            "nombre_empresa": "Nombre comercial detectado",
            "a_que_se_dedican": "Resumen de su modelo de negocio en 1 frase",
            "angulo_de_venta": "Justificación estratégica de por qué necesitan nuestro servicio",
            "asunto_email": "Un asunto corto, intrigante y no comercial (máx 5 palabras)",
            "borrador_email": "Email directo de 3 párrafos cortos. Primer párrafo: rompehielos hiper-personalizado sobre algo específico de su web. Segundo párrafo: el valor de nuestro servicio. Tercer párrafo: llamada a la acción de baja fricción."
        }}
        """
        
        respuesta = cliente.models.generate_content(
            model="gemini-2.5-flash",
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
