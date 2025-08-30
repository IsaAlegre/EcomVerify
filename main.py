from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Esquema de entrada para analizar un ecommerce
class EcommerceInput(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"mensaje": "¡API de EcomVerify funcionando!"}

@app.post("/analizar/")
def analizar_ecommerce(data: EcommerceInput):
    # Aquí irá la lógica para analizar la URL (por ahora, solo devuelve la URL recibida)
    return {"url_recibida": data.url, "resultado": "pendiente de análisis"}