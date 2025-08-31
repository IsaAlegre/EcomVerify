
from fastapi import FastAPI
from pydantic import BaseModel
from db import get_analysis, save_analysis, list_urls
from ml.predictor import predecir_ecommerce
import os
import openai
import requests

# Configura tu API key de OpenAI y Google Safe Browsing en variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

def analizar_con_openai(url):
    prompt = f"¿Es seguro comprar en este sitio web: {url}? Responde solo 'seguro' o 'pirata'."
    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return respuesta.choices[0].message['content'].strip().lower()



app = FastAPI()

class EcommerceInput(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"mensaje": "¡API de EcomVerify funcionando!"}

@app.get("/urls/")
def listar_urls():
    return list_urls()

@app.post("/analizar/")
def analizar_ecommerce(data: EcommerceInput):
    url = data.url
    resultado = get_analysis(url)
    if resultado:
        return {"url": url, "resultado": resultado, "fuente": "base de datos"}
    # Consultar con Google Safe Browsing
    gsb_api_key = os.getenv("GSB_API_KEY")
    resultado_gsb = analizar_con_google_safe_browsing(url, gsb_api_key) if gsb_api_key else None
    # Consultar con OpenAI
    resultado_openai = analizar_con_openai(url) if openai.api_key else None
    # Consultar con tu propio modelo
    resultado_local = predecir_ecommerce(url)
    # Lógica combinada: si alguna IA externa dice "pirata", es pirata
    resultados = [resultado_gsb, resultado_openai, resultado_local]
    if "pirata" in resultados:
        resultado_final = "pirata"
        fuente = "IA externa/local"
    else:
        resultado_final = "seguro"
        fuente = "IA externa/local"
    save_analysis(url, resultado_final)
    return {"url": url, "resultado": resultado_final, "fuente": fuente, "detalles": resultados}