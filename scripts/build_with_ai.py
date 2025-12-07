import os
import json
import time
import requests
from pathlib import Path

# Configuración
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
TEMPLATES_DIR = BASE_DIR / 'templates'
PUBLIC_DIR = BASE_DIR / 'public'

BRANDS_FILE = DATA_DIR / 'brands.json'
CATALOG_FILE = DATA_DIR / 'catalog.json'
GENERATED_CONTENT_FILE = DATA_DIR / 'generated_content.json'

# API de Gemini
GEMINI_API_KEY = "AIzaSyAt6AiC-LSf9IMe3HGPz-pf-uSZLaTjI7I"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

# URLs de tienda para repuestos
STORE_URL = "https://casadelcalefon.uy"
SPARE_PARTS_URLS = {
    "resistencia_rosca": f"{STORE_URL}/resistencias-rosca",
    "resistencia_brida": f"{STORE_URL}/resistencias-brida",
    "termostato_varilla": f"{STORE_URL}/termostatos-varilla",
    "termostato_contacto": f"{STORE_URL}/termostatos-contacto",
    "termostato_digital": f"{STORE_URL}/termostatos-digitales",
    "anodo_magnesio": f"{STORE_URL}/anodos-magnesio",
    "valvula_seguridad": f"{STORE_URL}/valvulas-seguridad",
    "junta_brida": f"{STORE_URL}/juntas-brida",
    "cable_alimentacion": f"{STORE_URL}/cables-alimentacion"
}

def load_json(filepath):
    """Carga un archivo JSON"""
    if not filepath.exists():
        return [] if filepath.name != 'generated_content.json' else {}
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def save_json(filepath, data):
    """Guarda datos en un archivo JSON"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_template(filename):
    """Lee un archivo de plantilla HTML"""
    path = TEMPLATES_DIR / filename
    if not path.exists():
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    """Escribe contenido en un archivo"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def call_gemini_api(prompt, max_retries=3):
    """Llama a la API de Gemini con reintentos"""
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 2048,
        }
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"   ⚠️ API Error {response.status_code}: {response.text}")
            
            # Esperar antes de reintentar
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        except Exception as e:
            print(f"   ⚠️ Exception en API: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    return None

def generate_brand_intro(brand):
    """Genera contenido introductorio para una marca usando Gemini"""
    prompt = f"""Eres un técnico experto en reparación de calefones eléctricos en Uruguay con 15 años de experiencia. 

Genera SOLO el contenido HTML (SIN etiquetas html, head, body, ni estructura del documento) para la página principal de la marca **{brand}**.

IMPORTANTE: NO incluyas etiquetas <!DOCTYPE>, <html>, <head>, <body>, ni <section>. Solo el contenido directo.

ESTRUCTURA REQUERIDA:

1. **Párrafo introductorio** con clase "lead":
<p class="lead">... Historia de {brand} en Uruguay, modelos comunes, capacidades típicas (30-100L) ...</p>

2. **Lista de características técnicas** (4-5 puntos):
<ul class="space-y-2">
    <li><i class="fas fa-check text-primary mr-2"></i>Tipo de resistencia común</li>
    <li><i class="fas fa-check text-primary mr-2"></i>Tipo de termostato</li>
    ...
</ul>

3. **Párrafo sobre reparaciones**:
<p>... Fallas comunes, disponibilidad de repuestos, nivel de complejidad ...</p>

FORMATO: Solo HTML limpio, sin ```html, sin markdown, sin estructura de documento.
LONGITUD: 200-280 palabras.
IDIOMA: Español de Uruguay."""

    content = call_gemini_api(prompt)
    if content:
        # Limpiar markdown y estructura no deseada
        content = content.replace('```html', '').replace('```', '').strip()
        # Eliminar etiquetas de estructura si las hay
        import re
        content = re.sub(r'<!DOCTYPE[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</?html[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<head>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'</?body[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</?main[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</?section[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        return content.strip()
    
    # Fallback si falla la API
    return f"""
<p class="lead">Los calefones eléctricos <strong>{brand}</strong> son ampliamente utilizados en hogares uruguayos, reconocidos por su confiabilidad y facilidad de instalación. La marca ofrece una variedad de modelos que van desde los 30 hasta los 100 litros de capacidad.</p>

<p>Características técnicas destacadas de los equipos {brand}:</p>
<ul class="space-y-2">
    <li><i class="fas fa-check text-primary mr-2"></i><strong>Resistencias de calidad:</strong> Disponibles en versiones de rosca y brida según el modelo</li>
    <li><i class="fas fa-check text-primary mr-2"></i><strong>Termostatos confiables:</strong> Sistemas de control de temperatura precisos</li>
    <li><i class="fas fa-check text-primary mr-2"></i><strong>Tanques duraderos:</strong> Fabricados en acero vitrificado con protección anticorrosiva</li>
    <li><i class="fas fa-check text-primary mr-2"></i><strong>Repuestos disponibles:</strong> Amplia disponibilidad en el mercado local</li>
</ul>

<p>Las reparaciones más comunes en calefones {brand} incluyen el reemplazo de resistencias quemadas, termostatos descalibrados y mantenimiento preventivo del ánodo de magnesio. Los repuestos son de fácil acceso en Uruguay y la mayoría de las reparaciones pueden realizarse sin necesidad de desinstalar completamente el equipo.</p>
"""

def generate_model_intro(brand, model_name, description, specs):
    """Genera contenido introductorio para un modelo específico"""
    prompt = f"""Eres un técnico especializado en reparación de calefones {brand} en Uruguay.

Genera SOLO fragmentos HTML (SIN etiquetas html, head, body, section) para el modelo **{brand} {model_name}**.

DATOS DEL MODELO:
- Descripción: {description}
- Resistencia: {specs.get('resistencia', 'N/A')}
- Termostato: {specs.get('termostato', 'N/A')}
- Ánodo: {specs.get('anodo', 'N/A')}
- Herramientas: {', '.join(specs.get('herramientas', []))}

GENERA EXACTAMENTE ESTA ESTRUCTURA:

<p class="lead">... Posicionamiento del {model_name} en la línea {brand}, capacidad y aplicaciones, tecnología destacada ...</p>

<h3 class="text-xl font-bold mt-6 mb-4 text-gray-800">Ventajas Técnicas del Modelo</h3>
<ul class="space-y-3">
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Punto 1:</strong> Detalle sobre resistencia {specs.get('resistencia', '')}</span></li>
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Punto 2:</strong> Facilidad de mantenimiento</span></li>
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Punto 3:</strong> Eficiencia energética</span></li>
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Punto 4:</strong> Durabilidad del tanque</span></li>
</ul>

<p class="mt-6">... Componentes de mantenimiento frecuente, dificultad de reparaciones DIY con herramientas mencionadas ...</p>

IMPORTANTE: NO incluyas ```html, ni etiquetas de estructura. Solo el fragmento HTML directo.
LONGITUD: 180-250 palabras."""

    content = call_gemini_api(prompt)
    if content:
        content = content.replace('```html', '').replace('```', '').strip()
        return content
    
    # Fallback mejorado
    resistencia_tipo = specs.get('resistencia', 'estándar')
    termostato_tipo = specs.get('termostato', 'universal')
    
    return f"""
<p class="lead">El <strong>{brand} {model_name}</strong> es un calefón eléctrico confiable que se destaca en el mercado uruguayo por su equilibrio entre rendimiento y facilidad de mantenimiento. {description}</p>

<p>Este modelo incorpora tecnología probada que garantiza un suministro constante de agua caliente para hogares de tamaño medio. Su diseño permite acceso directo a los componentes principales, facilitando las tareas de mantenimiento preventivo y reparaciones.</p>

<h3 class="text-xl font-bold mt-6 mb-4 text-gray-800">Ventajas Técnicas del Modelo</h3>
<ul class="space-y-3">
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Sistema de calentamiento:</strong> Equip ado con {resistencia_tipo}, optimizada para máxima eficiencia energética</span></li>
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Control preciso:</strong> {termostato_tipo} permite ajuste de temperatura según necesidad</span></li>
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Mantenimiento simplificado:</strong> Componentes estándar de fácil reemplazo</span></li>
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Protección anticorrosiva:</strong> Sistema de ánodo de magnesio para mayor durabilidad</span></li>
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Repuestos accesibles:</strong> Amplia disponibilidad en el mercado local</span></li>
</ul>

<p class="mt-6">Las reparaciones más comunes involucran el reemplazo periódico de la resistencia y el mantenimiento del ánodo. Con las herramientas adecuadas ({', '.join(specs.get('herramientas', ['herramientas básicas']))}) y siguiendo las guías técnicas, muchas tareas pueden realizarse sin asistencia profesional.</p>
"""

def generate_diagnosis_cards(brand, specs=None):
    """Genera contenido HTML para las tarjetas de diagnóstico personalizadas por marca"""
    resistencia_tipo = specs.get('resistencia', 'estándar') if specs else 'estándar'
    tiene_brida = 'brida' in resistencia_tipo.lower()
    
    return f"""
<div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-md border-2 border-blue-200 p-8 hover:shadow-xl transition-all duration-300 group cursor-pointer">
    <div class="flex items-center mb-5">
        <div class="bg-blue-500 text-white rounded-full w-14 h-14 flex items-center justify-center mr-5 group-hover:scale-110 transition-transform shadow-sm">
            <i class="fas fa-power-off text-2xl"></i>
        </div>
        <h3 class="text-2xl font-bold text-gray-800 group-hover:text-blue-600 transition-colors">No Enciende</h3>
    </div>
    <p class="text-gray-600 mb-5 leading-relaxed">El calefón {brand} no se activa al encenderlo. Sin luz piloto ni señales de funcionamiento.</p>
    <ul class="space-y-3 text-sm text-gray-700">
        <li class="flex items-start"><i class="fas fa-caret-right text-blue-500 mr-3 mt-1"></i><span><strong>Disyuntor:</strong> Verificar que el disyuntor térmico no haya saltado</span></li>
        <li class="flex items-start"><i class="fas fa-caret-right text-blue-500 mr-3 mt-1"></i><span><strong>Termostato de seguridad:</strong> Puede haberse activado por sobrecalentamiento</span></li>
        <li class="flex items-start"><i class="fas fa-caret-right text-blue-500 mr-3 mt-1"></i><span><strong>Cableado:</strong> Revisar conexiones internas sueltas o quemadas</span></li>
        <li class="flex items-start"><i class="fas fa-caret-right text-blue-500 mr-3 mt-1"></i><span><strong>Alimentación:</strong> Medir voltaje en los bornes de entrada</span></li>
    </ul>
</div>

<div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl shadow-md border-2 border-orange-200 p-8 hover:shadow-xl transition-all duration-300 group cursor-pointer">
    <div class="flex items-center mb-5">
        <div class="bg-orange-500 text-white rounded-full w-14 h-14 flex items-center justify-center mr-5 group-hover:scale-110 transition-transform shadow-sm">
            <i class="fas fa-thermometer-empty text-2xl"></i>
        </div>
        <h3 class="text-2xl font-bold text-gray-800 group-hover:text-orange-600 transition-colors">No Calienta</h3>
    </div>
    <p class="text-gray-600 mb-5 leading-relaxed">El equipo enciende y la luz indicadora funciona, pero el agua sale tibia o fría.</p>
    <ul class="space-y-3 text-sm text-gray-700">
        <li class="flex items-start"><i class="fas fa-caret-right text-orange-500 mr-3 mt-1"></i><span><strong>Resistencia:</strong> Medir continuidad con multímetro (debe mostrar 30-40Ω)</span></li>
        <li class="flex items-start"><i class="fas fa-caret-right text-orange-500 mr-3 mt-1"></i><span><strong>Termostato:</strong> Verificar ajuste de temperatura y continuidad</span></li>
        <li class="flex items-start"><i class="fas fa-caret-right text-orange-500 mr-3 mt-1"></i><span><strong>Sarro acumulado:</strong> Resistencia cubierta reduce eficiencia drásticamente</span></li>
        <li class="flex items-start"><i class="fas fa-caret-right text-orange-500 mr-3 mt-1"></i><span><strong>Sedimentos:</strong> Tanque lleno de sedimentos reduce capacidad térmica</span></li>
    </ul>
</div>

<div class="bg-gradient-to-br from-red-50 to-red-100 rounded-xl shadow-md border-2 border-red-200 p-8 hover:shadow-xl transition-all duration-300 group cursor-pointer">
    <div class="flex items-center mb-5">
        <div class="bg-red-500 text-white rounded-full w-14 h-14 flex items-center justify-center mr-5 group-hover:scale-110 transition-transform shadow-sm">
            <i class="fas fa-tint text-2xl"></i>
        </div>
        <h3 class="text-2xl font-bold text-gray-800 group-hover:text-red-600 transition-colors">Pierde Agua</h3>
    </div>
    <p class="text-gray-600 mb-5 leading-relaxed">Goteo continuo o fuga visible desde el calefón, válvula o conexiones.</p>
    <ul class="space-y-3 text-sm text-gray-700">
        {"<li class='flex items-start'><i class='fas fa-caret-right text-red-500 mr-3 mt-1'></i><span><strong>Junta de brida:</strong> La goma de la brida se deteriora con el tiempo</span></li>" if tiene_brida else ""}
        <li class="flex items-start"><i class="fas fa-caret-right text-red-500 mr-3 mt-1"></i><span><strong>Válvula de seguridad:</strong> Goteo normal cuando hay sobrepresión</span></li>
        <li class="flex items-start"><i class="fas fa-caret-right text-red-500 mr-3 mt-1"></i><span><strong>Rosca de resistencia:</strong> Teflón deteriorado en resistencias a rosca</span></li>
        <li class="flex items-start"><i class="fas fa-caret-right text-red-500 mr-3 mt-1"></i><span><strong>Tanque perforado:</strong> Corrosión avanzada, requiere reemplazo completo</span></li>
        <li class="flex items-start"><i class="fas fa-caret-right text-red-500 mr-3 mt-1"></i><span><strong>Conexiones:</strong> Revisar apriete de niples de entrada/salida</span></li>
    </ul>
</div>
"""

def generate_repair_guides(resistencia_tipo=""):
    """Genera contenido HTML para las guías de reparación personalizadas"""
    es_brida = 'brida' in resistencia_tipo.lower()
    es_rosca = 'rosca' in resistencia_tipo.lower()
    
    tipo_resistencia_texto = "de brida" if es_brida else "a rosca" if es_rosca else ""
    
    return f"""
<a href="./reparaciones/cambiar-resistencia.html" class="group bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6 hover:border-green-500 hover:shadow-lg transition-all duration-300 flex items-start">
    <div class="bg-green-100 text-green-600 rounded-full w-12 h-12 flex items-center justify-center mr-5 group-hover:bg-green-500 group-hover:text-white transition-colors flex-shrink-0">
        <i class="fas fa-bolt text-xl"></i>
    </div>
    <div>
        <h3 class="text-lg font-bold text-gray-800 group-hover:text-green-600 transition-colors mb-2">Cómo cambiar la resistencia {tipo_resistencia_texto}</h3>
        <p class="text-sm text-gray-500">Guía completa paso a paso para reemplazar resistencias quemadas o con sarro</p>
        <div class="flex items-center mt-2 text-xs text-gray-400">
            <i class="fas fa-clock mr-1"></i> <span>30-45 minutos</span>
            <span class="mx-2">•</span>
            <i class="fas fa-signal mr-1"></i> <span>Dificultad: Media</span>
        </div>
    </div>
</a>

<a href="./reparaciones/cambiar-termostato.html" class="group bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6 hover:border-blue-500 hover:shadow-lg transition-all duration-300 flex items-start">
    <div class="bg-blue-100 text-blue-600 rounded-full w-12 h-12 flex items-center justify-center mr-5 group-hover:bg-blue-500 group-hover:text-white transition-colors flex-shrink-0">
        <i class="fas fa-thermometer-half text-xl"></i>
    </div>
    <div>
        <h3 class="text-lg font-bold text-gray-800 group-hover:text-blue-600 transition-colors mb-2">Cómo cambiar el termostato</h3>
        <p class="text-sm text-gray-500">Identificación, diagnóstico y sustitución de termostatos defectuosos</p>
        <div class="flex items-center mt-2 text-xs text-gray-400">
            <i class="fas fa-clock mr-1"></i> <span>20-30 minutos</span>
            <span class="mx-2">•</span>
            <i class="fas fa-signal mr-1"></i> <span>Dificultad: Baja</span>
        </div>
    </div>
</a>

<a href="./reparaciones/cambiar-valvula.html" class="group bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6 hover:border-purple-500 hover:shadow-lg transition-all duration-300 flex items-start">
    <div class="bg-purple-100 text-purple-600 rounded-full w-12 h-12 flex items-center justify-center mr-5 group-hover:bg-purple-500 group-hover:text-white transition-colors flex-shrink-0">
        <i class="fas fa-faucet text-xl"></i>
    </div>
    <div>
        <h3 class="text-lg font-bold text-gray-800 group-hover:text-purple-600 transition-colors mb-2">Reemplazo de válvula de seguridad</h3>
        <p class="text-sm text-gray-500">Prevención de sobrepresión y solución de goteos permanentes</p>
        <div class="flex items-center mt-2 text-xs text-gray-400">
            <i class="fas fa-clock mr-1"></i> <span>15-25 minutos</span>
            <span class="mx-2">•</span>
            <i class="fas fa-signal mr-1"></i> <span>Dificultad: Baja</span>
        </div>
    </div>
</a>

<a href="./reparaciones/mantenimiento-anodo.html" class="group bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6 hover:border-orange-500 hover:shadow-lg transition-all duration-300 flex items-start">
    <div class="bg-orange-100 text-orange-600 rounded-full w-12 h-12 flex items-center justify-center mr-5 group-hover:bg-orange-500 group-hover:text-white transition-colors flex-shrink-0">
        <i class="fas fa-shield-alt text-xl"></i>
    </div>
    <div>
        <h3 class="text-lg font-bold text-gray-800 group-hover:text-orange-600 transition-colors mb-2">Mantenimiento del ánodo de magnesio</h3>
        <p class="text-sm text-gray-500">Protección anticorrosión para prolongar hasta 5 años la vida útil del tanque</p>
        <div class="flex items-center mt-2 text-xs text-gray-400">
            <i class="fas fa-clock mr-1"></i> <span>25-40 minutos</span>
            <span class="mx-2">•</span>
            <i class="fas fa-signal mr-1"></i> <span>Dificultad: Media</span>
        </div>
    </div>
</a>
"""

def generate_spare_parts_section(specs):
    """Genera una sección de repuestos recomendados con enlaces a la tienda"""
    html = '<div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 sm:p-8 mb-12 border-2 border-blue-200">'
    html += '<div class="flex items-center mb-6">'
    html += '<div class="bg-blue-500 text-white p-3 rounded-lg mr-4 shadow-sm">'
    html += '<i class="fas fa-shopping-cart text-xl"></i>'
    html += '</div>'
    html += '<div>'
    html += '<h2 class="text-2xl font-bold text-gray-800">Repuestos Recomendados</h2>'
    html += '<p class="text-gray-600 text-sm">Consigue los repuestos originales en nuestra tienda</p>'
    html += '</div>'
    html += '</div>'
    
    html += '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">'
    
    # Resistencia
    resistencia_type = specs.get('resistencia', '')
    if 'rosca' in resistencia_type.lower():
        url = SPARE_PARTS_URLS['resistencia_rosca']
        icon = 'fa-bolt'
        tipo = 'Resistencia de Rosca'
    elif 'brida' in resistencia_type.lower():
        url = SPARE_PARTS_URLS['resistencia_brida']
        icon = 'fa-bolt'
        tipo = 'Resistencia de Brida'
    else:
        url = SPARE_PARTS_URLS['resistencia_rosca']
        icon = 'fa-bolt'
        tipo = 'Resistencia'
    
    html += f'''
    <a href="{url}" target="_blank" class="group bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 hover:shadow-md transition-all flex items-center">
        <div class="bg-blue-100 text-blue-600 rounded-full w-12 h-12 flex items-center justify-center mr-4 group-hover:bg-blue-500 group-hover:text-white transition-colors">
            <i class="fas {icon}"></i>
        </div>
        <div class="flex-1">
            <h4 class="font-bold text-gray-800 group-hover:text-blue-600 transition-colors">{tipo}</h4>
            <p class="text-xs text-gray-500">{resistencia_type}</p>
        </div>
        <i class="fas fa-external-link-alt text-gray-400 group-hover:text-blue-500"></i>
    </a>
    '''
    
    # Termostato
    termostato_type = specs.get('termostato', '')
    if 'varilla' in termostato_type.lower():
        url = SPARE_PARTS_URLS['termostato_varilla']
        tipo = 'Termostato de Varilla'
    elif 'contacto' in termostato_type.lower():
        url = SPARE_PARTS_URLS['termostato_contacto']
        tipo = 'Termostato de Contacto'
    elif 'digital' in termostato_type.lower():
        url = SPARE_PARTS_URLS['termostato_digital']
        tipo = 'Termostato Digital'
    else:
        url = SPARE_PARTS_URLS['termostato_contacto']
        tipo = 'Termostato'
    
    html += f'''
    <a href="{url}" target="_blank" class="group bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-orange-500 hover:shadow-md transition-all flex items-center">
        <div class="bg-orange-100 text-orange-600 rounded-full w-12 h-12 flex items-center justify-center mr-4 group-hover:bg-orange-500 group-hover:text-white transition-colors">
            <i class="fas fa-thermometer-half"></i>
        </div>
        <div class="flex-1">
            <h4 class="font-bold text-gray-800 group-hover:text-orange-600 transition-colors">{tipo}</h4>
            <p class="text-xs text-gray-500">{termostato_type}</p>
        </div>
        <i class="fas fa-external-link-alt text-gray-400 group-hover:text-orange-500"></i>
    </a>
    '''
    
    # Ánodo
    anodo_type = specs.get('anodo', 'Estándar')
    html += f'''
    <a href="{SPARE_PARTS_URLS['anodo_magnesio']}" target="_blank" class="group bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-green-500 hover:shadow-md transition-all flex items-center">
        <div class="bg-green-100 text-green-600 rounded-full w-12 h-12 flex items-center justify-center mr-4 group-hover:bg-green-500 group-hover:text-white transition-colors">
            <i class="fas fa-shield-alt"></i>
        </div>
        <div class="flex-1">
            <h4 class="font-bold text-gray-800 group-hover:text-green-600 transition-colors">Ánodo de Magnesio</h4>
            <p class="text-xs text-gray-500">{anodo_type}</p>
        </div>
        <i class="fas fa-external-link-alt text-gray-400 group-hover:text-green-500"></i>
    </a>
    '''
    
    # Válvula de seguridad
    html += f'''
    <a href="{SPARE_PARTS_URLS['valvula_seguridad']}" target="_blank" class="group bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-purple-500 hover:shadow-md transition-all flex items-center">
        <div class="bg-purple-100 text-purple-600 rounded-full w-12 h-12 flex items-center justify-center mr-4 group-hover:bg-purple-500 group-hover:text-white transition-colors">
            <i class="fas fa-faucet"></i>
        </div>
        <div class="flex-1">
            <h4 class="font-bold text-gray-800 group-hover:text-purple-600 transition-colors">Válvula de Seguridad</h4>
            <p class="text-xs text-gray-500">3/4" - 6 bar</p>
        </div>
        <i class="fas fa-external-link-alt text-gray-400 group-hover:text-purple-500"></i>
    </a>
    '''
    
    # Si es brida, añadir junta
    if 'brida' in resistencia_type.lower():
        html += f'''
        <a href="{SPARE_PARTS_URLS['junta_brida']}" target="_blank" class="group bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-red-500 hover:shadow-md transition-all flex items-center md:col-span-2">
            <div class="bg-red-100 text-red-600 rounded-full w-12 h-12 flex items-center justify-center mr-4 group-hover:bg-red-500 group-hover:text-white transition-colors">
                <i class="fas fa-circle-notch"></i>
            </div>
            <div class="flex-1">
                <h4 class="font-bold text-gray-800 group-hover:text-red-600 transition-colors">Junta de Brida</h4>
                <p class="text-xs text-gray-500">Compatible con {resistencia_type}</p>
            </div>
            <i class="fas fa-external-link-alt text-gray-400 group-hover:text-red-500"></i>
        </a>
        '''
    
    html += '</div>'
    html += '</div>'
    
    return html

def build_site_with_ai(brands_per_batch=5, start_from=0):
    """Genera el sitio completo con contenido de IA de forma incremental"""
    print("[*] Iniciando generacion de sitio con IA...")
    print(f"[*] Usando Gemini 2.0 Flash API...")
    print(f"[*] Modo incremental: {brands_per_batch} marcas por lote, comenzando desde marca #{start_from}")
    
    # Cargar datos
    brands_list = load_json(BRANDS_FILE)
    catalog = load_json(CATALOG_FILE)
    generated_content = load_json(GENERATED_CONTENT_FILE)
    
    # Indexar catálogo por marca
    catalog_map = {item['brand']: item for item in catalog}
    
    # Cargar plantilla maestra
    layout_template = read_template('plantilla_maestra.html')
    
    if not layout_template:
        print("❌ Error: No se encontró la plantilla maestra")
        return
    
    # Determinar rango de marcas a procesar
    end_at = min(start_from + brands_per_batch, len(brands_list))
    brands_to_process = brands_list[start_from:end_at]
    
    print(f"[*] Total de marcas: {len(brands_list)}")
    print(f"[*] Procesando marcas {start_from+1} a {end_at} ({len(brands_to_process)} marcas en este lote)")
    
    api_calls_made = 0
    
    for idx, brand in enumerate(brands_to_process):
        global_idx = start_from + idx
        print(f"\n   [{global_idx+1}/{len(brands_list)}] >> {brand}")
        slug = brand.replace(' ', '-').lower()
        brand_dir = PUBLIC_DIR / slug
        
        # Generar contenido introductorio si no existe
        cache_key = f"brand_intro_{slug}"
        if cache_key not in generated_content:
            print(f"      [AI] Generando contenido con IA...")
            intro_content = generate_brand_intro(brand)
            if intro_content:
                generated_content[cache_key] = intro_content
                save_json(GENERATED_CONTENT_FILE, generated_content)
                api_calls_made += 1
                print(f"      [OK] Contenido generado (API calls: {api_calls_made})")
                time.sleep(2)  # Rate limiting aumentado
            else:
                print(f"      [ERROR] No se pudo generar contenido, usando fallback")
                intro_content = f"<p class='lead'>Información técnica sobre calefones {brand}.</p>"
        else:
            intro_content = generated_content[cache_key]
            print(f"      [CACHE] Usando contenido cacheado")
        
        # Datos del catálogo
        brand_data = catalog_map.get(brand)
        
        # Generar HTML de lista de modelos
        model_list_html = ""
        if brand_data and brand_data.get('models'):
            for m in brand_data['models']:
                model_list_html += f'''
                <div class="bg-gradient-to-br from-white to-gray-50 border-2 border-gray-200 rounded-xl p-6 hover:border-primary hover:shadow-lg transition-all duration-300 cursor-pointer group">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-xl font-bold text-gray-800 group-hover:text-primary transition-colors">{m['name']}</h3>
                        <i class="fas fa-arrow-right text-gray-400 group-hover:text-primary group-hover:translate-x-1 transition-all"></i>
                    </div>
                    <p class="text-gray-600 text-sm mb-4">{m['description']}</p>
                    <div class="flex items-center text-xs text-gray-500">
                        <i class="fas fa-info-circle mr-2"></i>
                        <a href="./modelos/{m['id']}.html" class="hover:text-primary transition-colors">Ver especificaciones</a>
                    </div>
                </div>
                '''
        
        # Generar página principal de marca (index.html)
        # Usar specs del primer modelo si existe para personalizar diagnóstico
        first_model_specs = brand_data['models'][0]['specs'] if brand_data and brand_data.get('models') else {}
        diagnosis_cards = generate_diagnosis_cards(brand, first_model_specs)
        repair_guides = generate_repair_guides(first_model_specs.get('resistencia', ''))
        
        page_content = f'''
        <div class="prose prose-lg max-w-none">
            {intro_content}
        </div>
        '''
        
        final_html = layout_template.replace('{{pageTitle}}', f'Reparación de Calefones {brand} - Guía Técnica Completa')
        final_html = final_html.replace('{{pageDescription}}', f'Guía completa de reparación para calefones {brand}. Diagnóstico de fallas, reemplazo de resistencias, termostatos y mantenimiento preventivo.')
        final_html = final_html.replace('{{currentUrl}}', f'https://calefones-landing.pages.dev/{slug}/')
        final_html = final_html.replace('{{h1Title}}', f'Calefones {brand}')
        final_html = final_html.replace('{{subtitle}}', 'Reparación profesional y diagnóstico técnico')
        final_html = final_html.replace('{{brandName}}', brand)
        final_html = final_html.replace('{{brandSlug}}', slug)
        final_html = final_html.replace('{{currentPageTitle}}', 'Inicio')
        final_html = final_html.replace('{{introContent}}', page_content)
        final_html = final_html.replace('{{modelListHtml}}', model_list_html)
        final_html = final_html.replace('{{diagnosisCards}}', diagnosis_cards)
        final_html = final_html.replace('{{repairGuides}}', repair_guides)
        final_html = final_html.replace('{{extraHead}}', '')
        
        write_file(brand_dir / 'index.html', final_html)
        print(f"      [OK] Pagina principal generada")
        
        # Generar páginas de modelos específicos
        if brand_data and brand_data.get('models'):
            for m in brand_data['models']:
                print(f"      [+] Modelo: {m['name']}")
                specs = m.get('specs', {})
                
                # Generar contenido del modelo con IA si no existe
                model_cache_key = f"model_intro_{slug}_{m['id']}"
                if model_cache_key not in generated_content:
                    print(f"         [AI] Generando contenido con IA...")
                    model_intro = generate_model_intro(brand, m['name'], m['description'], specs)
                    if model_intro:
                        generated_content[model_cache_key] = model_intro
                        save_json(GENERATED_CONTENT_FILE, generated_content)
                        api_calls_made += 1
                        print(f"         [OK] Contenido generado (API calls: {api_calls_made})")
                        time.sleep(2)  # Rate limiting aumentado
                    else:
                        print(f"         [ERROR] No se pudo generar, usando fallback")
                        model_intro = f"<p class='lead'>Información sobre el modelo {m['name']}.</p>"
                else:
                    model_intro = generated_content[model_cache_key]
                    print(f"         [CACHE] Usando contenido cacheado")
                
                # Generar sección de repuestos
                spare_parts_section = generate_spare_parts_section(specs)
                
                # Contenido del modelo
                model_content = f'''
                <div class="prose prose-lg max-w-none">
                    {model_intro}
                </div>
                '''
                
                # Tabla de errores
                error_rows = ""
                for err in m.get('error_codes', []):
                    error_rows += f'''
                    <tr class="hover:bg-gray-50 transition-colors">
                        <td class="p-4 font-mono font-bold text-gray-800">{err['code']}</td>
                        <td class="p-4 text-gray-700">{err['desc']}</td>
                        <td class="p-4 text-gray-600">{err['sol']}</td>
                    </tr>
                    '''
                
                final_model = layout_template.replace('{{pageTitle}}', f'Calefón {brand} {m["name"]} - Especificaciones y Reparación')
                final_model = final_model.replace('{{pageDescription}}', f'Guía técnica completa del calefón {brand} {m["name"]}. Especificaciones, códigos de error, repuestos y mantenimiento.')
                final_model = final_model.replace('{{currentUrl}}', f'https://calefones-landing.pages.dev/{slug}/modelos/{m["id"]}.html')
                final_model = final_model.replace('{{h1Title}}', f'{brand} {m["name"]}')
                final_model = final_model.replace('{{subtitle}}', m['description'])
                final_model = final_model.replace('{{brandName}}', brand)
                final_model = final_model.replace('{{brandSlug}}', slug)
                final_model = final_model.replace('{{currentPageTitle}}', m['name'])
                final_model = final_model.replace('{{introContent}}', model_content)
                
                # Especificaciones
                final_model = final_model.replace('{{specResistencia}}', specs.get('resistencia', 'N/A'))
                final_model = final_model.replace('{{specTermostato}}', specs.get('termostato', 'N/A'))
                final_model = final_model.replace('{{specAnodo}}', specs.get('anodo', 'N/A'))
                tools_str = ", ".join(specs.get('herramientas', []))
                final_model = final_model.replace('{{specHerramientas}}', tools_str)
                
                # Tabla de errores
                final_model = final_model.replace('{{errorTableRows}}', error_rows)
                
                # Mantenimiento
                maint = m.get('maintenance', {})
                final_model = final_model.replace('{{maintAnodo}}', maint.get('anodo', 'Anualmente'))
                final_model = final_model.replace('{{maintLimpieza}}', maint.get('limpieza', 'Cada 2 años'))
                final_model = final_model.replace('{{maintValvula}}', maint.get('valvula', 'Semestralmente'))
                
                # Insertar secciones generadas personalizadas por modelo
                model_diagnosis = generate_diagnosis_cards(brand, specs)
                model_repairs = generate_repair_guides(specs.get('resistencia', ''))
                final_model = final_model.replace('{{diagnosisCards}}', model_diagnosis)
                final_model = final_model.replace('{{repairGuides}}', model_repairs)
                
                # Insertar sección de repuestos antes del mantenimiento
                final_model = final_model.replace('<!-- SECCIÓN 7: Plan de Mantenimiento', spare_parts_section + '\n\n        <!-- SECCIÓN 7: Plan de Mantenimiento')
                
                # Ocultar selector de modelos en página de modelo
                final_model = final_model.replace('id="modelos"', 'id="modelos" style="display:none;"')
                
                final_model = final_model.replace('{{modelListHtml}}', '')
                final_model = final_model.replace('{{extraHead}}', '')
                
                write_file(brand_dir / 'modelos' / f'{m["id"]}.html', final_model)
                print(f"         [OK] Pagina del modelo generada")
    
    print("\n[DONE] Lote completado exitosamente!")
    print(f"[*] Marcas procesadas: {start_from+1} a {end_at}")
    print(f"[*] API calls realizadas: {api_calls_made}")
    print(f"[*] Sitio generado en: {PUBLIC_DIR}")
    print(f"[*] Contenido cacheado en: {GENERATED_CONTENT_FILE}")
    
    if end_at < len(brands_list):
        print(f"\n[INFO] Quedan {len(brands_list) - end_at} marcas por procesar")
        print(f"[INFO] Para continuar, ejecuta: python scripts/build_with_ai.py --start {end_at}")
    else:
        print(f"\n[SUCCESS] Todas las {len(brands_list)} marcas han sido procesadas!")

if __name__ == "__main__":
    import sys
    
    # Parsear argumentos
    start_from = 0
    brands_per_batch = 5
    
    if "--start" in sys.argv:
        start_idx = sys.argv.index("--start")
        if start_idx + 1 < len(sys.argv):
            start_from = int(sys.argv[start_idx + 1])
    
    if "--batch" in sys.argv:
        batch_idx = sys.argv.index("--batch")
        if batch_idx + 1 < len(sys.argv):
            brands_per_batch = int(sys.argv[batch_idx + 1])
    
    build_site_with_ai(brands_per_batch=brands_per_batch, start_from=start_from)
