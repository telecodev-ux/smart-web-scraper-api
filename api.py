from fastapi import FastAPI, HTTPException
from playwright.sync_api import sync_playwright
from google import genai
from google.genai.errors import ServerError
import time

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="Agente Autónomo RPA API",
    description="API industrial de automatización web y procesamiento con IA",
    version="1.0"
)

# Conectamos el cerebro con tu clave de Google AI Studio
# AHORA (seguro y profesional):
import os
cliente = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
@app.get("/")
def home():
    return {"estado": "activo", "mensaje": "El microservicio del agente autónomo está listo para operar."}

@app.get("/ejecutar-agente")
def ejecutar_agente(tema: str = "Ciberseguridad"):
    try:
        with sync_playwright() as p:
            # Lanzamos el navegador en modo headless=True para entornos de servidor (como Render)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print(f"🌐 [API] El agente entra a Wikipedia para buscar: {tema}")
            page.goto("https://es.wikipedia.org")
            
            page.fill("input[name='search']", tema)
            page.press("input[name='search']", "Enter")
            
            page.wait_for_selector("p")
            
            todos_los_parrafos = page.locator("p").all_inner_texts()
            parrafos_reales = [texto for texto in todos_los_parrafos if len(texto.strip()) > 20]
            contenido_bruto = "\n".join(parrafos_reales[:3])
            
            browser.close()
            
            print("🧠 [API] Procesando información con Inteligencia Artificial...")
            prompt = f"""
            Eres un consultor experto. Analiza el siguiente texto obtenido de una búsqueda automatizada sobre '{tema}'
            y redacta 3 recomendaciones clave o conclusiones estratégicas que una empresa deba conocer.
            
            Texto bruto: {contenido_bruto}
            """
            
            # Lógica de reintento ante saturación 503
            intentos = 3
            respuesta_texto = ""
            for intento in range(intentos):
                try:
                    respuesta = cliente.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=prompt,
                    )
                    respuesta_texto = respuesta.text
                    break
                except ServerError:
                    if intento < intentos - 1:
                        time.sleep(3)
                    else:
                        raise HTTPException(status_code=503, detail="Servidores de Google saturados temporalmente.")
            
            return {
                "exito": True,
                "tema_buscado": tema,
                "reporte_ia": respuesta_texto
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
