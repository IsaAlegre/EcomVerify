import re
import tldextract
import joblib
from urllib.parse import urlparse
import numpy as np

# Palabras sospechosas comunes en ecommerce piratas
PALABRAS_SOSPECHOSAS = [
    "ofert", "barat", "descuent", "replica", "fake", "imitacion",
    "superdescuento", "megaoferta", "original", "autentico", "outlet",
    "liquidacion", "rebaja", "promocion", "gang", "chollo"
]

def extraer_features(url: str):
    """Extrae características de la URL para el modelo"""
    parsed_url = urlparse(url)
    dominio = parsed_url.netloc.lower()
    path = parsed_url.path.lower()
    
    # Extraer información del dominio
    ext = tldextract.extract(url)
    subdominio = ext.subdomain
    dominio_principal = ext.domain
    tld = ext.suffix
    
    # Características
    features = {
        "longitud_url": len(url),
        "longitud_dominio": len(dominio),
        "tiene_https": 1 if parsed_url.scheme == "https" else 0,
        "num_palabras_sospechosas": sum(1 for palabra in PALABRAS_SOSPECHOSAS if palabra in url.lower()),
        "num_caracteres_especiales": len(re.findall(r'[^a-zA-Z0-9.-]', dominio)),
        "tiene_ip": 1 if re.match(r'^\d+\.\d+\.\d+\.\d+$', dominio) else 0,
        "edad_dominio_simulada": min(len(dominio_principal) / 10, 1.0),  # Simulación
        "ratio_numeros": len(re.findall(r'\d', url)) / len(url) if len(url) > 0 else 0,
    }
    
    return list(features.values())

def obtener_detalles_analisis(url: str, features: list):
    """Genera detalles explicativos más detallados del análisis"""
    detalles = {
        "longitud_url": features[0],
        "protocolo_seguro": "Sí" if features[2] == 1 else "No ⚠️",
        "palabras_sospechosas_detectadas": features[3],
        "caracteres_especiales": features[4],
        "usa_direccion_ip": "Sí ⚠️" if features[5] == 1 else "No",
        "longitud_nombre_dominio": features[6],
        "ratio_numeros": f"{features[7] * 100:.1f}%"
    }
    
    # Razones de sospecha específicas
    razones = []
    
    if features[3] >= 3:
        razones.append(f"❌ Demasiadas palabras de marketing agresivo ({features[3]} detectadas)")
    elif features[3] > 0:
        razones.append(f"⚠️ Palabras de marketing detectadas ({features[3]})")
    
    if features[4] >= 4:
        razones.append(f"❌ Demasiados caracteres especiales en el dominio ({features[4]})")
    elif features[4] >= 2:
        razones.append(f"⚠️ Caracteres especiales en dominio ({features[4]})")
    
    if features[5] == 1:
        razones.append("❌ Usa dirección IP en lugar de dominio (muy sospechoso)")
    
    if features[2] == 0:
        razones.append("❌ No usa HTTPS (conexión no segura)")
    
    if features[7] > 0.25:
        razones.append(f"❌ Alto porcentaje de números en la URL ({features[7] * 100:.1f}%)")
    elif features[7] > 0.15:
        razones.append(f"⚠️ Porcentaje moderado de números en la URL ({features[7] * 100:.1f}%)")
    
    if features[6] < 3:
        razones.append("⚠️ Nombre de dominio muy corto (posiblemente sospechoso)")
    
    # Razones de confianza
    razones_confianza = []
    if features[2] == 1:
        razones_confianza.append("✅ Usa HTTPS (conexión segura)")
    if features[5] == 0:
        razones_confianza.append("✅ Usa nombre de dominio (no IP)")
    if features[3] == 0:
        razones_confianza.append("✅ Sin palabras de marketing agresivo")
    if features[4] <= 1:
        razones_confianza.append("✅ Pocos caracteres especiales")
    
    detalles["razones_sospecha"] = razones if razones else ["✅ No se detectaron señales claras de riesgo"]
    detalles["razones_confianza"] = razones_confianza
    detalles["total_señales_riesgo"] = len(razones)
    detalles["total_señales_confianza"] = len(razones_confianza)
    
    return detalles

def verificar_terminos_condiciones(url: str):
    """Verifica si el sitio tiene términos y condiciones accesibles"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Patrones comunes de URLs de términos y condiciones
        terminos_patterns = [
            "/terminos",
            "/terminos-y-condiciones", 
            "/terms",
            "/terms-and-conditions",
            "/legal",
            "/privacidad",
            "/privacy"
        ]
        
        # Intentar acceder a la página principal
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar enlaces a términos y condiciones
        terminos_links = []
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if any(pattern in href for pattern in terminos_patterns):
                terminos_links.append(href)
        
        return {
            "tiene_terminos": len(terminos_links) > 0,
            "enlaces_encontrados": terminos_links,
            "puntuacion": 0.8 if len(terminos_links) > 0 else 0.2
        }
        
    except Exception:
        return {"tiene_terminos": False, "enlaces_encontrados": [], "puntuacion": 0.3}
def verificar_comentarios_quejas(url: str):
    """Verifica si hay comentarios o quejas de usuarios"""
    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        
        # Términos que indican quejas o problemas
        terminos_quejas = [
            "estafa", "fraude", "engaño", "mentira", "no funciona", 
            "no llega", "no recibo", "robo", "timó", "timaron",
            "queja", "reclamo", "demanda", "demandar", "demandado",
            "problema", "error", "falla", "defectuoso", "mal estado",
            "no responde", "no contestan", "atención al cliente pésima",
            "devolución", "reembolso", "arrepentimiento"
        ]
        
        response = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower()
        
        # Buscar quejas en el texto
        quejas_encontradas = []
        for queja in terminos_quejas:
            if queja in text:
                quejas_encontradas.append(queja)
        
        # Buscar en secciones de comentarios o reseñas
        secciones_comentarios = []
        for element in soup.find_all(['div', 'section', 'article']):
            class_list = element.get('class', [])
            id_attr = element.get('id', '')
            text_content = element.get_text().lower()
            
            # Patrones que indican sección de comentarios
            patrones_comentarios = ['comment', 'review', 'rating', 'testimonial', 'reseña', 'comentario']
            
            if (any(p in str(class_list).lower() for p in patrones_comentarios) or
                any(p in id_attr.lower() for p in patrones_comentarios) or
                any(p in text_content for p in ['deja tu comentario', 'escribe tu reseña'])):
                
                # Contar comentarios negativos en esta sección
                comentarios_negativos = sum(1 for q in terminos_quejas if q in text_content)
                if comentarios_negativos > 0:
                    secciones_comentarios.append({
                        'tipo': 'seccion_comentarios',
                        'comentarios_negativos': comentarios_negativos
                    })
        
        return {
            "quejas_detectadas": quejas_encontradas,
            "total_quejas": len(quejas_encontradas),
            "secciones_comentarios": secciones_comentarios,
            "tiene_comentarios_negativos": len(quejas_encontradas) > 0 or len(secciones_comentarios) > 0,
            "puntuacion_riesgo": min(0.7, len(quejas_encontradas) * 0.1 + len(secciones_comentarios) * 0.2)
        }
        
    except Exception:
        return {
            "quejas_detectadas": [],
            "total_quejas": 0,
            "secciones_comentarios": [],
            "tiene_comentarios_negativos": False,
            "puntuacion_riesgo": 0.0
        }

def verificar_enlaces_rotos(url: str):
    """Verifica si los enlaces importantes llevan a ninguna parte"""
    try:
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin
        
        response = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        enlaces_importantes = []
        enlaces_rotos = []
        
        # Enlaces críticos que deben funcionar
        enlaces_criticos = []
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text().lower()
            
            # Identificar enlaces importantes
            if any(p in href or p in text for p in [
                'contacto', 'contact', 'about', 'nosotros', 'soporte', 
                'help', 'ayuda', 'terminos', 'terms', 'privacidad', 'privacy',
                'devolucion', 'return', 'garantia', 'warranty'
            ]):
                enlaces_criticos.append({
                    'texto': text,
                    'href': href,
                    'es_externo': href.startswith('http') and url not in href
                })
        
        # Verificar algunos enlaces críticos (muestra)
        for enlace in enlaces_criticos[:5]:  # Limitar a 5 para no saturar
            try:
                if enlace['es_externo']:
                    # Para enlaces externos, verificar solo disponibilidad
                    enlaces_importantes.append({
                        'url': enlace['href'],
                        'estado': 'externo',
                        'texto': enlace['texto'][:50] + '...' if len(enlace['texto']) > 50 else enlace['texto']
                    })
                else:
                    # Para enlaces internos, verificar respuesta
                    link_url = urljoin(url, enlace['href'])
                    resp = requests.head(link_url, timeout=3, allow_redirects=True)
                    if resp.status_code >= 400:
                        enlaces_rotos.append({
                            'url': link_url,
                            'estado': f'error_{resp.status_code}',
                            'texto': enlace['texto'][:50] + '...' if len(enlace['texto']) > 50 else enlace['texto']
                        })
                    else:
                        enlaces_importantes.append({
                            'url': link_url,
                            'estado': f'ok_{resp.status_code}',
                            'texto': enlace['texto'][:50] + '...' if len(enlace['texto']) > 50 else enlace['texto']
                        })
            except:
                enlaces_rotos.append({
                    'url': enlace['href'],
                    'estado': 'timeout_error',
                    'texto': enlace['texto'][:50] + '...' if len(enlace['texto']) > 50 else enlace['texto']
                })
        
        return {
            "enlaces_importantes": enlaces_importantes,
            "enlaces_rotos": enlaces_rotos,
            "total_enlaces_rotos": len(enlaces_rotos),
            "tiene_enlaces_rotos": len(enlaces_rotos) > 0,
            "puntuacion_riesgo": min(0.5, len(enlaces_rotos) * 0.15)
        }
        
    except Exception:
        return {
            "enlaces_importantes": [],
            "enlaces_rotos": [],
            "total_enlaces_rotos": 0,
            "tiene_enlaces_rotos": False,
            "puntuacion_riesgo": 0.0
        }

def verificar_terminos_detallado(url: str):
    """Verificación más detallada de términos y condiciones"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        terminos_info = verificar_terminos_condiciones(url)
        
        # Si no tiene enlaces de términos, verificar directamente páginas comunes
        if not terminos_info["tiene_terminos"]:
            paginas_comunes = [
                "/terminos-y-condiciones",
                "/terms",
                "/legal",
                "/privacidad"
            ]
            
            for pagina in paginas_comunes:
                try:
                    terminos_url = url + pagina
                    resp = requests.get(terminos_url, timeout=5)
                    if resp.status_code == 200:
                        terminos_info["tiene_terminos"] = True
                        terminos_info["enlaces_encontrados"].append(pagina)
                        terminos_info["puntuacion"] = 0.6  # Menor puntuación porque lo encontramos por fuerza bruta
                        break
                except:
                    continue
        
        # Verificar si los enlaces de términos realmente funcionan
        enlaces_funcionando = []
        for enlace in terminos_info["enlaces_encontrados"]:
            try:
                terminos_url = url + enlace if enlace.startswith('/') else enlace
                if not terminos_url.startswith('http'):
                    terminos_url = url + '/' + enlace
                
                resp = requests.head(terminos_url, timeout=3, allow_redirects=True)
                if resp.status_code == 200:
                    enlaces_funcionando.append({
                        'url': terminos_url,
                        'estado': 'funcionando'
                    })
                else:
                    enlaces_funcionando.append({
                        'url': terminos_url,
                        'estado': f'error_{resp.status_code}'
                    })
            except:
                enlaces_funcionando.append({
                    'url': enlace,
                    'estado': 'error_conexion'
                })
        
        terminos_info["enlaces_verificados"] = enlaces_funcionando
        terminos_info["enlaces_funcionando"] = len([e for e in enlaces_funcionando if e['estado'] == 'funcionando'])
        terminos_info["tiene_terminos_funcionales"] = terminos_info["enlaces_funcionando"] > 0
        
        # Ajustar puntuación basado en enlaces funcionales
        if terminos_info["tiene_terminos"]:
            if terminos_info["enlaces_funcionando"] > 0:
                terminos_info["puntuacion"] = 0.9
            else:
                terminos_info["puntuacion"] = 0.4  # Tiene enlaces pero no funcionan
        
        return terminos_info
        
    except Exception:
        return {
            "tiene_terminos": False,
            "enlaces_encontrados": [],
            "puntuacion": 0.1,
            "enlaces_funcionando": 0,
            "tiene_terminos_funcionales": False
        }
def verificar_entidades_reguladoras(url: str):
    """Verifica menciones a entidades reguladoras"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower()
        
        # Entidades reguladoras comunes
        entidades = {
            "defensa_consumidor": ["defensa al consumidor", "proconsumo", "derechos del consumidor"],
            "camara_comercio": ["cámara de comercio", "registro mercantil"],
            "superintendencia": ["superintendencia", "supersociedades", "superfinanciera"],
            "reclamos": ["libro de reclamaciones", "sistema de reclamos"],
            "certificaciones": ["ssl", "https", "certificado", "verisign", "digicert"]
        }
        
        resultados = {}
        for entidad, palabras in entidades.items():
            resultados[entidad] = any(palabra in text for palabra in palabras)
        
        # Calcular puntuación
        puntuacion = sum(1 for tiene in resultados.values() if tiene) / len(entidades)
        
        return {
            "menciones_entidades": resultados,
            "puntuacion": puntuacion,
            "total_menciones": sum(1 for tiene in resultados.values() if tiene)
        }
        
    except Exception:
        return {"menciones_entidades": {}, "puntuacion": 0.1, "total_menciones": 0}
    
def verificar_contacto(url: str):
    """Verifica información de contacto válida"""
    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        # Buscar información de contacto
        tiene_direccion = re.search(r'\b(calle|avenida|av\.|cra\.|carrera|número|no\.)\b', text, re.IGNORECASE)
        tiene_telefono = re.search(r'(\+?\d{2,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}', text)
        tiene_email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        # Buscar enlaces de contacto
        contact_links = []
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if any(x in href for x in ['contacto', 'contact', 'about', 'nosotros', 'soporte']):
                contact_links.append(href)
        
        return {
            "tiene_direccion": bool(tiene_direccion),
            "tiene_telefono": bool(tiene_telefono),
            "tiene_email": bool(tiene_email),
            "enlaces_contacto": contact_links,
            "puntuacion": (bool(tiene_direccion) + bool(tiene_telefono) + bool(tiene_email) + (len(contact_links) > 0)) / 4
        }
        
    except Exception:
        return {"tiene_direccion": False, "tiene_telefono": False, "tiene_email": False, "enlaces_contacto": [], "puntuacion": 0.1}

def predecir_ecommerce(url: str):
    """Predice si un ecommerce es confiable o pirata con verificaciones completas"""
    try:
        # Extraer características básicas de la URL
        features = extraer_features(url)
        
        # Obtener valores individuales para mejor legibilidad
        palabras_sospechosas = features[3]
        caracteres_especiales = features[4]
        tiene_https = features[2]
        tiene_ip = features[5]
        ratio_numeros = features[7]
        
        # Calcular puntuación de riesgo base (0-1)
        riesgo = 0.0
        
        # 1. Análisis de la URL (riesgo base)
        if palabras_sospechosas >= 3:
            riesgo += 0.4
        elif palabras_sospechosas == 2:
            riesgo += 0.2
        elif palabras_sospechosas == 1:
            riesgo += 0.1
        
        if tiene_https == 0:
            riesgo += 0.3
        
        if tiene_ip == 1:
            riesgo += 0.3
        
        if caracteres_especiales >= 4:
            riesgo += 0.2
        elif caracteres_especiales >= 2:
            riesgo += 0.1
        
        if ratio_numeros > 0.25:
            riesgo += 0.2
        elif ratio_numeros > 0.15:
            riesgo += 0.1
        
        # 2. Verificaciones adicionales detalladas
        terminos_info = verificar_terminos_detallado(url)
        entidades_info = verificar_entidades_reguladoras(url)
        contacto_info = verificar_contacto(url)
        quejas_info = verificar_comentarios_quejas(url)
        enlaces_info = verificar_enlaces_rotos(url)
        
        # 🔥 NUEVAS REGLAS ESTRICTAS - SI CUMPLE ALGUNA, ES PIRATA
        es_claramente_pirata = False
        razones_pirata = []
        
        # Regla 1: Sin términos y condiciones funcionales
        if not terminos_info["tiene_terminos_funcionales"]:
            es_claramente_pirata = True
            razones_pirata.append("❌ No tiene términos y condiciones funcionales")
            riesgo += 0.4
        
        # Regla 2: Tiene quejas de usuarios
        if quejas_info["tiene_comentarios_negativos"] and quejas_info["total_quejas"] >= 3:
            es_claramente_pirata = True
            razones_pirata.append(f"❌ Tiene {quejas_info['total_quejas']} quejas de usuarios detectadas")
            riesgo += 0.3
        
        # Regla 3: Muchos enlaces rotos en secciones importantes
        if enlaces_info["total_enlaces_rotos"] >= 3:
            es_claramente_pirata = True
            razones_pirata.append(f"❌ Tiene {enlaces_info['total_enlaces_rotos']} enlaces rotos en secciones importantes")
            riesgo += 0.3
        
        # Ajustes de riesgo adicionales
        if not terminos_info["tiene_terminos"]:
            riesgo += 0.15
        
        if entidades_info["total_menciones"] == 0:
            riesgo += 0.10
            
        if contacto_info["puntuacion"] < 0.5:
            riesgo += 0.10
        
        riesgo += quejas_info["puntuacion_riesgo"]
        riesgo += enlaces_info["puntuacion_riesgo"]
        
        # Limitar riesgo máximo
        riesgo = min(riesgo, 1.0)
        
        # 3. DECISIÓN FINAL - REGLAS ESTRICTAS
        if es_claramente_pirata or riesgo >= 0.3:  # Umbral más bajo
            resultado = "pirata"
            confianza = max(riesgo, 0.7)  # Mínimo 70% de confianza si es pirata por reglas estrictas
        else:
            resultado = "confiable"
            confianza = 1 - riesgo
        
        # Obtener detalles del análisis
        detalles = obtener_detalles_analisis(url, features)
        
        # Agregar todas las verificaciones
        detalles.update({
            "terminos_condiciones": terminos_info,
            "entidades_reguladoras": entidades_info,
            "informacion_contacto": contacto_info,
            "comentarios_quejas": quejas_info,
            "enlaces_rotos": enlaces_info,
            "verificaciones_completadas": True,
            "reglas_estrictas": {
                "es_claramente_pirata": es_claramente_pirata,
                "razones": razones_pirata if es_claramente_pirata else ["✅ No se activaron reglas estrictas de piratería"]
            }
        })
        
        # Agregar puntuación de riesgo
        detalles["puntuacion_riesgo"] = round(riesgo, 2)
        detalles["nivel_riesgo"] = obtener_nivel_riesgo(riesgo)
        detalles["decision"] = f"Umbral: 0.3, Riesgo: {riesgo:.2f}, Reglas estrictas: {es_claramente_pirata}"
        
        return resultado, confianza, detalles
        
    except Exception as e:
        return "pirata", 0.9, {
            "error": str(e), 
            "advertencia": "Error crítico en análisis - Marcado como precaución",
            "verificaciones_completadas": False,
            "puntuacion_riesgo": 0.9,
            "nivel_riesgo": "muy alto"
        }
        
    except Exception as e:
        # En caso de error crítico, considerar como sospechoso con alta confianza
        return "pirata", 0.8, {
            "error": str(e), 
            "advertencia": "Error crítico en análisis",
            "verificaciones_completadas": False,
            "puntuacion_riesgo": 0.8
        }

def obtener_nivel_riesgo(puntuacion: float) -> str:
    """Convierte la puntuación de riesgo en un nivel descriptivo"""
    if puntuacion >= 0.7:
        return "muy alto"
    elif puntuacion >= 0.5:
        return "alto"
    elif puntuacion >= 0.35:
        return "moderado"
    elif puntuacion >= 0.2:
        return "bajo"
    else:
        return "muy bajo"