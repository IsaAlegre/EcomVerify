from fastapi import FastAPI
from pydantic import BaseModel

# Importa tu predictor
from ml.predictor import predecir_ecommerce

app = FastAPI()

class EcommerceInput(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"mensaje": "¡API de EcomVerify funcionando!"}

@app.post("/analizar/")
def analizar_ecommerce(data: EcommerceInput):
    resultado = predecir_ecommerce(data.url)
    return {"url_recibida": data.url, "resultado": resultado}