from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import get_analysis, save_analysis, list_urls
from ml.predictor import predecir_ecommerce, obtener_detalles_analisis
import traceback

app = FastAPI(title="EcomVerify API", version="1.0.0")

class EcommerceInput(BaseModel):
    url: str

class AnalysisResult(BaseModel):
    url: str
    resultado: str
    confianza: float
    detalles: dict
    fuente: str

@app.get("/")
def read_root():
    return {"mensaje": "¡API de EcomVerify funcionando!", "version": "1.0.0"}

@app.get("/urls/")
def listar_urls():
    try:
        return list_urls()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar URLs: {str(e)}")

@app.post("/analizar/", response_model=AnalysisResult)
def analizar_ecommerce(data: EcommerceInput):
    url = data.url
    
    # Validar URL básica
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL debe comenzar con http:// o https://")
    
    try:
        # Verificar si ya existe en la base de datos
        resultado_db = get_analysis(url)
        if resultado_db:
            print("Resultado encontrado en base de datos")
            return {
                "url": url,
                "resultado": resultado_db["resultado"],
                "confianza": resultado_db.get("confianza", 0.8),
                "detalles": resultado_db.get("detalles", {}),
                "fuente": "base de datos"
            }
        
        # Realizar nuevo análisis con ML
        print("Realizando nuevo análisis con ML...")
        resultado_ml, confianza, detalles = predecir_ecommerce(url)
        print(f"Resultado ML: {resultado_ml}, Confianza: {confianza}")

        # Guardar en base de datos
        save_analysis(url, resultado_ml, confianza, detalles)
        print("Análisis guardado en base de datos")

        return {
            "url": url,
            "resultado": resultado_ml,
            "confianza": confianza,
            "detalles": detalles,
            "fuente": "modelo ML"
        }
        
    except Exception as e:
        print(f"Error completo: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error en el análisis: {str(e)}")

@app.get("/estado/")
def estado_sistema():
    try:
        # Verificar conexión a BD
        urls = list_urls()
        return {
            "estado": "operativo",
            "urls_analizadas": len(urls),
            "bd_conectada": True
        }
    except:
        return {
            "estado": "parcialmente operativo",
            "bd_conectada": False
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)