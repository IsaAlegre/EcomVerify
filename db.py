import psycopg2
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import sys
# Cargar variables de entorno
load_dotenv()

# Obtener variables de entorno SIN valores por defecto
def get_env_variable(var_name):
    """Obtiene una variable de entorno o muestra error si no existe"""
    value = os.getenv(var_name)
    if value is None:
        print(f"❌ ERROR: La variable de entorno {var_name} no está definida")
        print("   Asegúrate de tener un archivo .env con todas las variables requeridas")
        sys.exit(1)
    return value


DB_HOST = get_env_variable('DB_HOST')
DB_NAME = get_env_variable('DB_NAME')
DB_USER = get_env_variable('DB_USER')
DB_PASS = get_env_variable('DB_PASS')
DB_PORT = get_env_variable('DB_PORT')

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def init_db():
    """Inicializar la base de datos PostgreSQL"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS analisis (
                id SERIAL PRIMARY KEY,
                url TEXT UNIQUE NOT NULL,
                resultado VARCHAR(20) NOT NULL,
                confianza FLOAT NOT NULL,
                detalles JSONB,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Base de datos PostgreSQL inicializada correctamente")
    except Exception as e:
        print(f"Error al inicializar BD PostgreSQL: {e}")
    finally:
        conn.close()

def save_analysis(url, resultado, confianza, detalles):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # PostgreSQL usa %s como placeholder y soporta JSONB nativamente
        cur.execute(
            """
            INSERT INTO analisis (url, resultado, confianza, detalles)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (url) 
            DO UPDATE SET 
                resultado = EXCLUDED.resultado,
                confianza = EXCLUDED.confianza,
                detalles = EXCLUDED.detalles,
                fecha_actualizacion = CURRENT_TIMESTAMP
            """, (url, resultado, confianza, json.dumps(detalles))
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_analysis(url):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT url, resultado, confianza, detalles FROM analisis WHERE url = %s", 
            (url,)
        )
        result = cur.fetchone()
        if result:
            return {
                "url": result[0],
                "resultado": result[1],
                "confianza": result[2],
                "detalles": result[3] or {}
            }
        return None
    finally:
        cur.close()
        conn.close()

def list_urls():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT url, resultado, confianza, fecha_creacion 
            FROM analisis 
            ORDER BY fecha_creacion DESC
        """)
        results = cur.fetchall()
        return [{
            "url": r[0], 
            "resultado": r[1], 
            "confianza": r[2],
            "fecha_analisis": r[3].isoformat() if r[3] else None
        } for r in results]
    finally:
        cur.close()
        conn.close()

# Inicializar la base de datos al importar
init_db()