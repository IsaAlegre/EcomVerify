# EcomVerify

_EcomVerify_ es una plataforma para detectar tiendas online piratas, proteger a los usuarios del fraude en e-commerce, reportar sitios sospechosos y compartir experiencias en comunidad.

## Características principales

- **Detección automática** de tiendas fraudulentas usando machine learning y análisis de dominios.
- **Interfaz web moderna y responsiva** desarrollada con React y Tailwind CSS.
- **Reporte de páginas**: los usuarios pueden reportar tiendas sospechosas para alertar a otros.
- **Comunidad**: sección para compartir y leer experiencias sobre compras online.
- **Espacio para fotos**: los usuarios pueden subir imágenes como evidencia o ilustración de sus experiencias.
- **Backend robusto y seguro** basado en FastAPI y PostgreSQL.

## Tecnologías utilizadas

- **Frontend:** React, Tailwind CSS
- **Backend:** Python, FastAPI (`fastapi==0.104.1`)
- **Server:** Uvicorn (`uvicorn==0.24.0`)
- **Base de datos:** PostgreSQL (`psycopg2-binary==2.9.7`)
- **Utilidades:** python-dotenv, tldextract
- **Machine Learning:** scikit-learn, joblib

## Instalación

### Backend

1. Clona el repositorio:
   ```bash
   git clone https://github.com/IsaAlegre/EcomVerify.git
   cd EcomVerify
   ```
2. Instala las dependencias de Python:
   ```bash
   pip install fastapi==0.104.1 uvicorn==0.24.0 psycopg2-binary==2.9.7 python-dotenv==1.0.0 tldextract==3.4.4 scikit-learn==1.3.2 joblib==1.3.2
   ```
3. Configura tus variables de entorno en un archivo `.env`.

4. Inicia el servidor:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend

1. Ve al directorio de frontend:
   ```bash
   cd client
   ```
2. Instala las dependencias:
   ```bash
   npm install
   ```
3. Inicia la aplicación:
   ```bash
   npm run dev
   ```

## Uso

1. Accede a la interfaz web desde tu navegador.
2. Ingresa la URL de la tienda online que deseas verificar.
3. El sistema analizará el dominio y te informará si se trata de una tienda legítima o potencialmente pirata.
4. Si detectas una tienda sospechosa, puedes reportarla para ayudar a otros usuarios.
5. Visita la sección de comunidad para compartir tu experiencia o leer casos de otros usuarios.
6. Sube fotos o capturas de pantalla como evidencia o ilustración en el espacio dedicado a imágenes.



## Contribuciones

¡Las contribuciones son bienvenidas!  
Abre issues o pull requests para sugerencias, mejoras o reportes de errores.

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).

## Autor

Desarrollado por IsaAlegre y luciabz.

---

