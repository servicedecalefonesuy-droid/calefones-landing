import os
import json
import time
import requests
from pathlib import Path
import re

# Configuración
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
TEMPLATES_DIR = BASE_DIR / 'templates'
PUBLIC_DIR = BASE_DIR / 'public'

BRANDS_FILE = DATA_DIR / 'brands.json'
REPAIR_CONTENT_FILE = DATA_DIR / 'repair_pages_content.json'

# API de Gemini
GEMINI_API_KEY = "AIzaSyAt6AiC-LSf9IMe3HGPz-pf-uSZLaTjI7I"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

# URLs de tienda
STORE_URL = "https://casadelcalefon.uy"

# Tipos de reparaciones a generar
REPAIR_TYPES = [
    {
        'id': 'cambiar-resistencia',
        'title': 'Cambiar Resistencia',
        'icon': 'fa-bolt',
        'color': 'blue',
        'store_link': f'{STORE_URL}/resistencias',
        'difficulty': 'Medio',
        'time': '30-45 min'
    },
    {
        'id': 'reemplazar-termostato',
        'title': 'Reemplazar Termostato',
        'icon': 'fa-thermometer-half',
        'color': 'green',
        'store_link': f'{STORE_URL}/termostatos',
        'difficulty': 'Fácil',
        'time': '20-30 min'
    },
    {
        'id': 'cambiar-anodo',
        'title': 'Cambiar Ánodo de Magnesio',
        'icon': 'fa-shield-alt',
        'color': 'purple',
        'store_link': f'{STORE_URL}/anodos',
        'difficulty': 'Fácil',
        'time': '15-25 min'
    },
    {
        'id': 'reparar-fuga-agua',
        'title': 'Reparar Fuga de Agua',
        'icon': 'fa-tint',
        'color': 'cyan',
        'store_link': f'{STORE_URL}/juntas-valvulas',
        'difficulty': 'Medio',
        'time': '20-40 min'
    },
    {
        'id': 'diagnostico-no-enciende',
        'title': 'Diagnóstico: No Enciende',
        'icon': 'fa-power-off',
        'color': 'red',
        'store_link': f'{STORE_URL}/repuestos',
        'difficulty': 'Medio',
        'time': '15-30 min'
    }
]

def load_json(filepath):
    """Carga un archivo JSON"""
    if not filepath.exists():
        return {} if 'repair' in filepath.name else []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def save_json(filepath, data):
    """Guarda datos en un archivo JSON"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def write_file(path, content):
    """Escribe contenido en un archivo"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def call_gemini_api(prompt, max_retries=3):
    """Llama a la API de Gemini con reintentos"""
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
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
                print(f"      [!] API Error {response.status_code}")
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        except Exception as e:
            print(f"      [!] Exception: {str(e)[:50]}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    return None

def clean_html(content):
    """Limpia contenido HTML de la IA"""
    if not content:
        return ""
    
    content = content.replace('```html', '').replace('```', '').strip()
    content = re.sub(r'<!DOCTYPE[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</?html[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<head>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'</?body[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</?main[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</?section[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    return content.strip()

def generate_repair_guide(brand, repair_type):
    """Genera una guía de reparación detallada"""
    
    prompt = f"""Eres un técnico experto en reparación de calefones eléctricos {brand} en Uruguay.

Genera una guía PASO A PASO detallada para: **{repair_type['title']}** en calefones {brand}.

ESTRUCTURA HTML REQUERIDA:

<!-- Introducción -->
<div class="bg-gradient-to-r from-{repair_type['color']}-50 to-{repair_type['color']}-100 p-6 rounded-lg mb-8">
    <h2 class="text-2xl font-bold text-gray-800 mb-4"><i class="fas {repair_type['icon']} text-{repair_type['color']}-600 mr-3"></i>{repair_type['title']} - {brand}</h2>
    <p class="text-gray-700 mb-3">... Descripción del problema común en {brand}, por qué es importante esta reparación ...</p>
    <div class="flex gap-4 mt-4">
        <span class="bg-white px-4 py-2 rounded-full text-sm"><i class="far fa-clock mr-2"></i><strong>Tiempo:</strong> {repair_type['time']}</span>
        <span class="bg-white px-4 py-2 rounded-full text-sm"><i class="fas fa-signal mr-2"></i><strong>Dificultad:</strong> {repair_type['difficulty']}</span>
        <span class="bg-white px-4 py-2 rounded-full text-sm"><i class="fas fa-dollar-sign mr-2"></i><strong>Costo:</strong> Moderado</span>
    </div>
</div>

<!-- Herramientas Necesarias -->
<div class="bg-white p-6 rounded-lg shadow-md mb-8">
    <h3 class="text-xl font-bold text-gray-800 mb-4"><i class="fas fa-toolbox text-orange-600 mr-2"></i>Herramientas y Materiales</h3>
    <div class="grid md:grid-cols-2 gap-4">
        <ul class="space-y-2">
            <li><i class="fas fa-check text-green-600 mr-2"></i>Herramienta 1 específica</li>
            <li><i class="fas fa-check text-green-600 mr-2"></i>Herramienta 2</li>
            <li><i class="fas fa-check text-green-600 mr-2"></i>Herramienta 3</li>
        </ul>
        <ul class="space-y-2">
            <li><i class="fas fa-check text-green-600 mr-2"></i>Material 1</li>
            <li><i class="fas fa-check text-green-600 mr-2"></i>Material 2</li>
            <li><i class="fas fa-check text-green-600 mr-2"></i>Equipo de seguridad</li>
        </ul>
    </div>
</div>

<!-- Medidas de Seguridad -->
<div class="bg-red-50 border-l-4 border-red-500 p-6 mb-8">
    <h3 class="text-xl font-bold text-red-800 mb-3"><i class="fas fa-exclamation-triangle mr-2"></i>Medidas de Seguridad</h3>
    <ul class="space-y-2 text-gray-700">
        <li><i class="fas fa-bolt text-red-600 mr-2"></i><strong>Cortar corriente eléctrica:</strong> Desconectar en tablero principal</li>
        <li><i class="fas fa-tint text-blue-600 mr-2"></i><strong>Cerrar llave de agua:</strong> Evitar derrames</li>
        <li><i class="fas fa-fire text-orange-600 mr-2"></i><strong>Esperar enfriamiento:</strong> Agua puede estar a 80°C</li>
        <li><i class="fas fa-hard-hat text-yellow-600 mr-2"></i><strong>Equipo de protección:</strong> Guantes y gafas</li>
    </ul>
</div>

<!-- Procedimiento Paso a Paso -->
<div class="bg-white p-6 rounded-lg shadow-md mb-8">
    <h3 class="text-xl font-bold text-gray-800 mb-6"><i class="fas fa-list-ol text-{repair_type['color']}-600 mr-2"></i>Procedimiento Paso a Paso</h3>
    
    <div class="space-y-6">
        <!-- Paso 1 -->
        <div class="border-l-4 border-{repair_type['color']}-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-{repair_type['color']}-600 text-white px-3 py-1 rounded-full mr-2">1</span>Título del Paso 1</h4>
            <p class="text-gray-700 mb-2">... Instrucciones detalladas específicas para {brand} ...</p>
            <div class="bg-blue-50 p-3 rounded mt-2">
                <p class="text-sm text-blue-800"><i class="fas fa-lightbulb mr-2"></i><strong>Consejo:</strong> Tip específico para {brand}</p>
            </div>
        </div>
        
        <!-- Paso 2 -->
        <div class="border-l-4 border-{repair_type['color']}-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-{repair_type['color']}-600 text-white px-3 py-1 rounded-full mr-2">2</span>Título del Paso 2</h4>
            <p class="text-gray-700">... Instrucciones detalladas ...</p>
        </div>
        
        <!-- Paso 3 -->
        <div class="border-l-4 border-{repair_type['color']}-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-{repair_type['color']}-600 text-white px-3 py-1 rounded-full mr-2">3</span>Título del Paso 3</h4>
            <p class="text-gray-700">... Instrucciones detalladas ...</p>
        </div>
        
        <!-- Paso 4 -->
        <div class="border-l-4 border-{repair_type['color']}-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-{repair_type['color']}-600 text-white px-3 py-1 rounded-full mr-2">4</span>Título del Paso 4</h4>
            <p class="text-gray-700">... Instrucciones detalladas ...</p>
        </div>
        
        <!-- Pasos adicionales según la reparación (5-8 pasos típicamente) -->
    </div>
</div>

<!-- Problemas Comunes -->
<div class="bg-yellow-50 p-6 rounded-lg mb-8">
    <h3 class="text-xl font-bold text-gray-800 mb-4"><i class="fas fa-wrench text-yellow-600 mr-2"></i>Problemas Comunes y Soluciones</h3>
    <div class="space-y-4">
        <div>
            <h4 class="font-bold text-gray-800 mb-1"><i class="fas fa-exclamation-circle text-yellow-600 mr-2"></i>Problema 1 específico en {brand}</h4>
            <p class="text-gray-700 pl-6">Solución detallada...</p>
        </div>
        <div>
            <h4 class="font-bold text-gray-800 mb-1"><i class="fas fa-exclamation-circle text-yellow-600 mr-2"></i>Problema 2</h4>
            <p class="text-gray-700 pl-6">Solución...</p>
        </div>
        <div>
            <h4 class="font-bold text-gray-800 mb-1"><i class="fas fa-exclamation-circle text-yellow-600 mr-2"></i>Problema 3</h4>
            <p class="text-gray-700 pl-6">Solución...</p>
        </div>
    </div>
</div>

<!-- Verificación Final -->
<div class="bg-green-50 p-6 rounded-lg mb-8">
    <h3 class="text-xl font-bold text-gray-800 mb-4"><i class="fas fa-check-double text-green-600 mr-2"></i>Verificación Final</h3>
    <ul class="space-y-2">
        <li><i class="fas fa-check-square text-green-600 mr-2"></i>Paso de verificación 1</li>
        <li><i class="fas fa-check-square text-green-600 mr-2"></i>Paso de verificación 2</li>
        <li><i class="fas fa-check-square text-green-600 mr-2"></i>Paso de verificación 3</li>
        <li><i class="fas fa-check-square text-green-600 mr-2"></i>Prueba de funcionamiento</li>
    </ul>
</div>

<!-- CTA Comprar Repuesto -->
<div class="bg-gradient-to-r from-{repair_type['color']}-600 to-{repair_type['color']}-700 text-white p-8 rounded-lg text-center">
    <h3 class="text-2xl font-bold mb-3">¿Necesitás el Repuesto?</h3>
    <p class="text-{repair_type['color']}-100 mb-6">Comprá repuestos originales para {brand} con envío a todo Uruguay</p>
    <a href="{repair_type['store_link']}" class="inline-block bg-white text-{repair_type['color']}-700 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition text-lg">
        <i class="fas fa-shopping-cart mr-2"></i>Ver Repuestos en Tienda
    </a>
</div>

IMPORTANTE:
- Genera 6-8 pasos detallados en el procedimiento
- Incluye consejos específicos para modelos {brand}
- Menciona particularidades técnicas de la marca
- Lenguaje claro para usuario uruguayo
- NO incluyas etiquetas de estructura (html, body, head)
- Solo fragmentos HTML directos
- Longitud: 800-1000 palabras"""

    content = call_gemini_api(prompt)
    return clean_html(content) if content else None

def create_repair_page_html(brand, slug, repair_type, content):
    """Crea el HTML completo de una página de reparación"""
    
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{repair_type['title']} - Calefón {brand} | Guía Paso a Paso</title>
    <meta name="description" content="Guía completa paso a paso para {repair_type['title'].lower()} en calefones {brand}. Herramientas, medidas de seguridad y procedimiento detallado.">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://calefones-landing.pages.dev/{slug}/reparaciones/{repair_type['id']}.html">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        primary: '#0066CC',
                    }}
                }}
            }}
        }}
    </script>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
    </style>
</head>
<body class="bg-gray-50">
    
    <!-- Header -->
    <header class="bg-white shadow-md sticky top-0 z-50">
        <div class="container mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <div>
                    <a href="/{slug}/" class="text-2xl font-bold text-primary hover:text-blue-700 transition">
                        <i class="fas fa-fire mr-2"></i>Calefones {brand}
                    </a>
                </div>
                <nav class="hidden md:flex space-x-6">
                    <a href="/{slug}/" class="text-gray-700 hover:text-primary transition">Inicio</a>
                    <a href="/{slug}/#diagnostico" class="text-gray-700 hover:text-primary transition">Diagnóstico</a>
                    <a href="/{slug}/#reparaciones" class="text-gray-700 hover:text-primary transition">Reparaciones</a>
                    <a href="{STORE_URL}" target="_blank" class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                        <i class="fas fa-shopping-cart mr-2"></i>Tienda
                    </a>
                </nav>
            </div>
        </div>
    </header>
    
    <!-- Breadcrumb -->
    <div class="bg-gray-100 py-3">
        <div class="container mx-auto px-4">
            <nav class="text-sm">
                <a href="/" class="text-primary hover:underline">Inicio</a>
                <span class="mx-2 text-gray-500">/</span>
                <a href="/{slug}/" class="text-primary hover:underline">{brand}</a>
                <span class="mx-2 text-gray-500">/</span>
                <a href="/{slug}/#reparaciones" class="text-primary hover:underline">Reparaciones</a>
                <span class="mx-2 text-gray-500">/</span>
                <span class="text-gray-700">{repair_type['title']}</span>
            </nav>
        </div>
    </div>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-12 max-w-4xl">
        
        {content if content else f'<p>Contenido de {repair_type["title"]} para {brand} en desarrollo.</p>'}
        
        <!-- Otras Reparaciones -->
        <div class="mt-12 bg-white p-6 rounded-lg shadow-md">
            <h3 class="text-xl font-bold text-gray-800 mb-4">Otras Reparaciones de {brand}</h3>
            <div class="grid md:grid-cols-2 gap-4">
                {''.join([f'''
                <a href="/{slug}/reparaciones/{rt['id']}.html" class="block p-4 border border-gray-200 rounded-lg hover:border-{rt['color']}-500 hover:shadow-md transition">
                    <i class="fas {rt['icon']} text-{rt['color']}-600 mr-2"></i><span class="font-semibold">{rt['title']}</span>
                </a>
                ''' for rt in REPAIR_TYPES if rt['id'] != repair_type['id']])}
            </div>
        </div>
        
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-12">
        <div class="container mx-auto px-4 text-center">
            <p class="mb-2"><i class="fas fa-phone mr-2"></i>Servicio Técnico Especializado en Uruguay</p>
            <p class="text-gray-400 text-sm">Guías de reparación para calefones {brand} - © 2025</p>
            <div class="mt-4">
                <a href="{STORE_URL}" target="_blank" class="text-primary hover:text-blue-400 transition">
                    <i class="fas fa-store mr-2"></i>Visitá Nuestra Tienda de Repuestos
                </a>
            </div>
        </div>
    </footer>
    
</body>
</html>"""

def build_repair_pages():
    """Genera todas las páginas de reparación"""
    print("[*] Generador de Paginas de Reparacion")
    print(f"[*] {len(REPAIR_TYPES)} tipos de reparacion por marca")
    print()
    
    brands_list = load_json(BRANDS_FILE)
    repair_cache = load_json(REPAIR_CONTENT_FILE)
    
    total_pages = len(brands_list) * len(REPAIR_TYPES)
    api_calls = 0
    pages_created = 0
    
    print(f"[*] Total de paginas a generar: {total_pages}")
    print(f"[*] {len(brands_list)} marcas × {len(REPAIR_TYPES)} reparaciones")
    print("=" * 60)
    
    for brand_idx, brand in enumerate(brands_list, 1):
        slug = brand.replace(' ', '-').lower()
        repair_dir = PUBLIC_DIR / slug / 'reparaciones'
        
        print(f"\n[{brand_idx}/{len(brands_list)}] {brand}")
        print("-" * 60)
        
        for repair_idx, repair_type in enumerate(REPAIR_TYPES, 1):
            cache_key = f"{slug}_{repair_type['id']}"
            
            # Generar contenido si no existe en caché
            if cache_key not in repair_cache:
                print(f"  [{repair_idx}/{len(REPAIR_TYPES)}] {repair_type['title']:30s} >> ", end='', flush=True)
                content = generate_repair_guide(brand, repair_type)
                
                if content:
                    repair_cache[cache_key] = content
                    save_json(REPAIR_CONTENT_FILE, repair_cache)
                    api_calls += 1
                    print(f"[OK] API #{api_calls}")
                    time.sleep(1.5)  # Rate limiting
                else:
                    print("[FAIL]")
                    content = f"<p>Guía de {repair_type['title']} para {brand} en desarrollo.</p>"
            else:
                content = repair_cache[cache_key]
                print(f"  [{repair_idx}/{len(REPAIR_TYPES)}] {repair_type['title']:30s} >> [CACHE]")
            
            # Crear página HTML
            page_html = create_repair_page_html(brand, slug, repair_type, content)
            write_file(repair_dir / f"{repair_type['id']}.html", page_html)
            pages_created += 1
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    print(f"[*] Paginas creadas: {pages_created}/{total_pages}")
    print(f"[*] API calls realizadas: {api_calls}")
    print(f"[*] Contenido cacheado en: {REPAIR_CONTENT_FILE}")
    print(f"[*] Paginas en: {PUBLIC_DIR}/[marca]/reparaciones/")
    print("\n[DONE] Generacion completa!")

if __name__ == "__main__":
    build_repair_pages()
