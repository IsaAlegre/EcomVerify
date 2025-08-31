import psycopg2
import os

# Configuración de la conexión (ajusta estos valores a tu entorno)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'ecomverify')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASS = os.getenv('DB_PASS', '4655')

# Función para obtener conexión

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

# Función para guardar análisis

def save_analysis(url, resultado):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO analisis (url, resultado)
        VALUES (%s, %s)
        """, (url, resultado)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_analysis(url):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT resultado FROM analisis WHERE url = %s", (url,)
    )
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None

# Función para listar todas las URLs guardadas
def list_urls():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT url, resultado FROM analisis")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [{"url": r[0], "resultado": r[1]} for r in results]


if __name__ == "__main__":
    try:
        conn = get_connection()
        print("¡Conexión exitosa a la base de datos!")
        conn.close()
    except Exception as e:
        print("Error al conectar:", e)
