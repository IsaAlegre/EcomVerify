import joblib
import re

# Carga tu modelo previamente entrenado (ajusta la ruta y nombre)
# model = joblib.load("ml/models/ecommerce_model.pkl")

def extraer_features(url: str):
    # Ejemplo simple: longitud del dominio y si contiene palabras sospechosas
    sospechosas = ["oferta", "barato", "descuento", "replica", "fake"]
    features = {
        "longitud": len(url),
        "sospechosa": int(any(palabra in url.lower() for palabra in sospechosas)),
        # Agrega más features según tu modelo
    }
    return [features["longitud"], features["sospechosa"]]

def predecir_ecommerce(url: str):
    # features = extraer_features(url)
    # resultado = model.predict([features])[0]
    # Simulación de predicción (reemplaza por tu modelo real)
    features = extraer_features(url)
    if features[1] == 1 or features[0] > 40:
        return "pirata"
    else:
        return "legitimo"