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
CATALOG_FILE = DATA_DIR / 'catalog.json'
SECTIONS_CONTENT_FILE = DATA_DIR / 'sections_content.json'

# API de Gemini
GEMINI_API_KEY = "AIzaSyAt6AiC-LSf9IMe3HGPz-pf-uSZLaTjI7I"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

# URLs de tienda
STORE_URL = "https://casadelcalefon.uy"

def load_json(filepath):
    """Carga un archivo JSON"""
    if not filepath.exists():
        return {} if 'sections' in filepath.name else []
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
    content = re.sub(r'<div class="container[^"]*"[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</div>\s*$', '', content.strip())
    
    return content.strip()

def generate_section(section_type, brand, model_data=None):
    """Genera una sección específica usando IA"""
    
    if section_type == "brand_intro":
        prompt = f"""Eres técnico experto en calefones eléctricos en Uruguay.

Genera SOLO el contenido HTML para la introducción de la marca **{brand}**.

ESTRUCTURA EXACTA:

<p class="lead">Historia de {brand} en Uruguay, modelos comunes (30-100L), reputación.</p>

<p>Características técnicas:</p>
<ul class="space-y-2">
    <li><i class="fas fa-check text-primary mr-2"></i>Resistencias disponibles</li>
    <li><i class="fas fa-check text-primary mr-2"></i>Termostatos</li>
    <li><i class="fas fa-check text-primary mr-2"></i>Durabilidad</li>
    <li><i class="fas fa-check text-primary mr-2"></i>Repuestos</li>
</ul>

<p>Fallas comunes y reparaciones típicas.</p>

REGLAS: Sin ```html, sin etiquetas de estructura, solo fragmento HTML. 200-250 palabras."""
    
    elif section_type == "diagnosis_cards":
        prompt = f"""Genera 3 tarjetas HTML de diagnóstico para calefones **{brand}**.

CÓDIGO EXACTO:

<div class="grid md:grid-cols-3 gap-6">
    <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
        <h3 class="text-xl font-bold text-red-700 mb-3"><i class="fas fa-power-off mr-2"></i>No Enciende</h3>
        <p class="text-gray-700 mb-4">... causas específicas para {brand} ...</p>
        <ul class="text-sm space-y-2">
            <li><i class="fas fa-wrench text-red-500 mr-2"></i>Verificar conexión eléctrica</li>
            <li><i class="fas fa-wrench text-red-500 mr-2"></i>Testear termostato</li>
            <li><i class="fas fa-wrench text-red-500 mr-2"></i>Revisar resistencia</li>
        </ul>
    </div>
    
    <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-orange-500">
        <h3 class="text-xl font-bold text-orange-700 mb-3"><i class="fas fa-temperature-low mr-2"></i>No Calienta</h3>
        <p class="text-gray-700 mb-4">... problema común {brand} ...</p>
        <ul class="text-sm space-y-2">
            <li><i class="fas fa-wrench text-orange-500 mr-2"></i>Calcificación resistencia</li>
            <li><i class="fas fa-wrench text-orange-500 mr-2"></i>Termostato descalibrado</li>
            <li><i class="fas fa-wrench text-orange-500 mr-2"></i>Potencia insuficiente</li>
        </ul>
    </div>
    
    <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
        <h3 class="text-xl font-bold text-blue-700 mb-3"><i class="fas fa-tint mr-2"></i>Pierde Agua</h3>
        <p class="text-gray-700 mb-4">... puntos de fuga {brand} ...</p>
        <ul class="text-sm space-y-2">
            <li><i class="fas fa-wrench text-blue-500 mr-2"></i>Válvula seguridad</li>
            <li><i class="fas fa-wrench text-blue-500 mr-2"></i>Junta brida deteriorada</li>
            <li><i class="fas fa-wrench text-blue-500 mr-2"></i>Corrosión tanque</li>
        </ul>
    </div>
</div>

REGLAS: Solo HTML, sin markdown."""
    
    elif section_type == "repair_guides":
        prompt = f"""Genera 3 guías de reparación para calefones **{brand}**.

CÓDIGO EXACTO:

<div class="grid md:grid-cols-3 gap-6">
    <div class="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg shadow-md">
        <div class="flex items-center mb-4">
            <i class="fas fa-bolt text-3xl text-blue-600 mr-3"></i>
            <h3 class="text-xl font-bold text-gray-800">Cambio de Resistencia</h3>
        </div>
        <p class="text-gray-700 mb-4">Procedimiento para reemplazar resistencia en {brand}.</p>
        <div class="flex justify-between text-sm mb-3">
            <span class="bg-blue-200 px-3 py-1 rounded-full"><i class="far fa-clock mr-1"></i>30-45 min</span>
            <span class="bg-yellow-200 px-3 py-1 rounded-full"><i class="fas fa-signal mr-1"></i>Medio</span>
        </div>
        <a href="{STORE_URL}/resistencias" class="block text-center bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition">Ver Resistencias</a>
    </div>
    
    <div class="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg shadow-md">
        <div class="flex items-center mb-4">
            <i class="fas fa-thermometer-half text-3xl text-green-600 mr-3"></i>
            <h3 class="text-xl font-bold text-gray-800">Reemplazo Termostato</h3>
        </div>
        <p class="text-gray-700 mb-4">Sustitución de termostato defectuoso {brand}.</p>
        <div class="flex justify-between text-sm mb-3">
            <span class="bg-green-200 px-3 py-1 rounded-full"><i class="far fa-clock mr-1"></i>20-30 min</span>
            <span class="bg-green-200 px-3 py-1 rounded-full"><i class="fas fa-signal mr-1"></i>Fácil</span>
        </div>
        <a href="{STORE_URL}/termostatos" class="block text-center bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition">Ver Termostatos</a>
    </div>
    
    <div class="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg shadow-md">
        <div class="flex items-center mb-4">
            <i class="fas fa-shield-alt text-3xl text-purple-600 mr-3"></i>
            <h3 class="text-xl font-bold text-gray-800">Cambio de Ánodo</h3>
        </div>
        <p class="text-gray-700 mb-4">Mantenimiento preventivo ánodo {brand}.</p>
        <div class="flex justify-between text-sm mb-3">
            <span class="bg-purple-200 px-3 py-1 rounded-full"><i class="far fa-clock mr-1"></i>15-25 min</span>
            <span class="bg-green-200 px-3 py-1 rounded-full"><i class="fas fa-signal mr-1"></i>Fácil</span>
        </div>
        <a href="{STORE_URL}/anodos" class="block text-center bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition">Ver Ánodos</a>
    </div>
</div>

REGLAS: Solo HTML, sin markdown."""
    
    elif section_type == "model_intro" and model_data:
        specs = model_data.get('specifications', {})
        prompt = f"""Genera introducción del modelo **{brand} {model_data['name']}**.

DATOS:
- Descripción: {model_data['description']}
- Resistencia: {specs.get('resistencia', 'N/A')}
- Termostato: {specs.get('termostato', 'N/A')}

CÓDIGO:

<p class="lead">Posicionamiento del {model_data['name']}, capacidad, tecnología destacada.</p>

<h3 class="text-xl font-bold mt-6 mb-4 text-gray-800">Ventajas Técnicas</h3>
<ul class="space-y-3">
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Resistencia:</strong> {specs.get('resistencia', '')}</span></li>
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Termostato:</strong> Precisión</span></li>
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Eficiencia:</strong> Bajo consumo</span></li>
    <li class="flex items-start"><i class="fas fa-check-circle text-green-600 mr-2 mt-1"></i><span><strong>Mantenimiento:</strong> Accesible</span></li>
</ul>

<p class="mt-6">Facilidad de reparación y herramientas necesarias.</p>

REGLAS: Sin markdown, 180-220 palabras."""
    
    else:
        return None
    
    content = call_gemini_api(prompt)
    return clean_html(content) if content else None

def build_all_content():
    """Genera todo el contenido seccionando las peticiones a la IA"""
    print("[*] Generador de Contenido por Secciones")
    print("[*] Estrategia: 1 seccion -> 1 peticion API -> pausa")
    print()
    
    # Cargar datos
    brands_list = load_json(BRANDS_FILE)
    catalog = load_json(CATALOG_FILE)
    sections_cache = load_json(SECTIONS_CONTENT_FILE)
    
    # Indexar catálogo
    catalog_map = {item['brand']: item for item in catalog}
    
    # Plantilla
    layout_template = read_template('plantilla_maestra.html')
    if not layout_template:
        print("[ERROR] No se encontro plantilla_maestra.html")
        return
    
    total_sections = 0
    api_calls = 0
    
    # FASE 1: Generar todas las secciones de introducción de marca
    print("=" * 60)
    print("FASE 1: Introducciones de Marca (42 marcas)")
    print("=" * 60)
    
    for idx, brand in enumerate(brands_list, 1):
        slug = brand.replace(' ', '-').lower()
        cache_key = f"brand_intro_{slug}"
        
        if cache_key in sections_cache:
            print(f"[{idx}/42] {brand:20s} >> [CACHE]")
            continue
        
        print(f"[{idx}/42] {brand:20s} >> ", end='', flush=True)
        content = generate_section("brand_intro", brand)
        
        if content:
            sections_cache[cache_key] = content
            save_json(SECTIONS_CONTENT_FILE, sections_cache)
            api_calls += 1
            print(f"[OK] API call #{api_calls}")
            time.sleep(1.5)  # Rate limiting
        else:
            print("[FAIL]")
    
    total_sections += len(brands_list)
    
    # FASE 2: Generar tarjetas de diagnóstico
    print("\n" + "=" * 60)
    print("FASE 2: Tarjetas de Diagnostico (42 marcas)")
    print("=" * 60)
    
    for idx, brand in enumerate(brands_list, 1):
        slug = brand.replace(' ', '-').lower()
        cache_key = f"diagnosis_{slug}"
        
        if cache_key in sections_cache:
            print(f"[{idx}/42] {brand:20s} >> [CACHE]")
            continue
        
        print(f"[{idx}/42] {brand:20s} >> ", end='', flush=True)
        content = generate_section("diagnosis_cards", brand)
        
        if content:
            sections_cache[cache_key] = content
            save_json(SECTIONS_CONTENT_FILE, sections_cache)
            api_calls += 1
            print(f"[OK] API call #{api_calls}")
            time.sleep(1.5)
        else:
            print("[FAIL]")
    
    total_sections += len(brands_list)
    
    # FASE 3: Generar guías de reparación
    print("\n" + "=" * 60)
    print("FASE 3: Guias de Reparacion (42 marcas)")
    print("=" * 60)
    
    for idx, brand in enumerate(brands_list, 1):
        slug = brand.replace(' ', '-').lower()
        cache_key = f"repair_guides_{slug}"
        
        if cache_key in sections_cache:
            print(f"[{idx}/42] {brand:20s} >> [CACHE]")
            continue
        
        print(f"[{idx}/42] {brand:20s} >> ", end='', flush=True)
        content = generate_section("repair_guides", brand)
        
        if content:
            sections_cache[cache_key] = content
            save_json(SECTIONS_CONTENT_FILE, sections_cache)
            api_calls += 1
            print(f"[OK] API call #{api_calls}")
            time.sleep(1.5)
        else:
            print("[FAIL]")
    
    total_sections += len(brands_list)
    
    # FASE 4: Generar contenido de modelos
    print("\n" + "=" * 60)
    print("FASE 4: Descripciones de Modelos (10 modelos)")
    print("=" * 60)
    
    models_count = 0
    for item in catalog:
        brand = item['brand']
        slug = brand.replace(' ', '-').lower()
        model = item['model']
        cache_key = f"model_intro_{slug}_{model['id']}"
        
        if cache_key in sections_cache:
            models_count += 1
            print(f"[{models_count}/10] {brand} {model['name']:15s} >> [CACHE]")
            continue
        
        models_count += 1
        print(f"[{models_count}/10] {brand} {model['name']:15s} >> ", end='', flush=True)
        content = generate_section("model_intro", brand, model)
        
        if content:
            sections_cache[cache_key] = content
            save_json(SECTIONS_CONTENT_FILE, sections_cache)
            api_calls += 1
            print(f"[OK] API call #{api_calls}")
            time.sleep(1.5)
        else:
            print("[FAIL]")
    
    total_sections += len(catalog)
    
    # FASE 5: Ensamblar todas las páginas HTML
    print("\n" + "=" * 60)
    print("FASE 5: Ensamblando Paginas HTML")
    print("=" * 60)
    
    pages_created = 0
    
    for brand in brands_list:
        slug = brand.replace(' ', '-').lower()
        brand_dir = PUBLIC_DIR / slug
        
        # Obtener contenido de secciones
        intro_content = sections_cache.get(f"brand_intro_{slug}", f"<p>Información sobre {brand}.</p>")
        diagnosis_cards = sections_cache.get(f"diagnosis_{slug}", "")
        repair_guides = sections_cache.get(f"repair_guides_{slug}", "")
        
        # Lista de modelos si existen
        model_list_html = ""
        if brand in catalog_map:
            model = catalog_map[brand]['model']
            model_list_html = f'''
            <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition">
                <h3 class="text-xl font-bold text-gray-800 mb-2">{model['name']}</h3>
                <p class="text-gray-600 mb-4">{model['description']}</p>
                <a href="/{ slug}/modelos/{model['id']}.html" class="inline-block bg-primary text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">Ver Especificaciones</a>
            </div>
            '''
        
        # Ensamblar página de marca
        page_html = layout_template
        page_html = page_html.replace('{{pageTitle}}', f'Calefones {brand} - Reparación y Repuestos en Uruguay')
        page_html = page_html.replace('{{pageDescription}}', f'Guía completa de reparación de calefones {brand}. Repuestos, diagnóstico y mantenimiento.')
        page_html = page_html.replace('{{currentUrl}}', f'https://calefones-landing.pages.dev/{slug}/')
        page_html = page_html.replace('{{h1Title}}', f'Calefones {brand}')
        page_html = page_html.replace('{{subtitle}}', 'Reparación, Repuestos y Mantenimiento')
        page_html = page_html.replace('{{brandName}}', brand)
        page_html = page_html.replace('{{brandSlug}}', slug)
        page_html = page_html.replace('{{currentPageTitle}}', brand)
        page_html = page_html.replace('{{introContent}}', intro_content)
        page_html = page_html.replace('{{modelListHtml}}', model_list_html)
        page_html = page_html.replace('{{diagnosisCards}}', diagnosis_cards)
        page_html = page_html.replace('{{repairGuides}}', repair_guides)
        page_html = page_html.replace('{{extraHead}}', '')
        
        # Especificaciones genéricas para páginas de marca
        page_html = page_html.replace('{{specResistencia}}', 'Varía según modelo')
        page_html = page_html.replace('{{specTermostato}}', 'Varía según modelo')
        page_html = page_html.replace('{{specAnodo}}', 'Magnesio estándar')
        page_html = page_html.replace('{{specHerramientas}}', 'Destornillador, Multímetro, Llaves')
        page_html = page_html.replace('{{errorTableRows}}', '')
        page_html = page_html.replace('{{maintAnodo}}', 'Anualmente')
        page_html = page_html.replace('{{maintLimpieza}}', 'Cada 2 años')
        page_html = page_html.replace('{{maintValvula}}', 'Semestralmente')
        
        write_file(brand_dir / 'index.html', page_html)
        pages_created += 1
        
        # Crear página de modelo si existe
        if brand in catalog_map:
            model = catalog_map[brand]['model']
            model_intro = sections_cache.get(f"model_intro_{slug}_{model['id']}", "")
            specs = model.get('specifications', {})
            errors = model.get('error_codes', [])
            maint = model.get('maintenance', {})
            
            # Tabla de errores
            error_rows = ""
            for err in errors:
                error_rows += f'''
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="p-4 font-mono font-bold text-gray-800">{err['code']}</td>
                    <td class="p-4 text-gray-700">{err['desc']}</td>
                    <td class="p-4 text-gray-600">{err['sol']}</td>
                </tr>
                '''
            
            model_html = layout_template
            model_html = model_html.replace('{{pageTitle}}', f'{brand} {model["name"]} - Especificaciones y Reparación')
            model_html = model_html.replace('{{pageDescription}}', f'Guía técnica completa del {brand} {model["name"]}.')
            model_html = model_html.replace('{{currentUrl}}', f'https://calefones-landing.pages.dev/{slug}/modelos/{model["id"]}.html')
            model_html = model_html.replace('{{h1Title}}', f'{brand} {model["name"]}')
            model_html = model_html.replace('{{subtitle}}', model['description'])
            model_html = model_html.replace('{{brandName}}', brand)
            model_html = model_html.replace('{{brandSlug}}', slug)
            model_html = model_html.replace('{{currentPageTitle}}', model['name'])
            model_html = model_html.replace('{{introContent}}', model_intro)
            model_html = model_html.replace('{{modelListHtml}}', '')
            model_html = model_html.replace('{{diagnosisCards}}', diagnosis_cards)
            model_html = model_html.replace('{{repairGuides}}', repair_guides)
            model_html = model_html.replace('{{specResistencia}}', specs.get('resistencia', 'N/A'))
            model_html = model_html.replace('{{specTermostato}}', specs.get('termostato', 'N/A'))
            model_html = model_html.replace('{{specAnodo}}', specs.get('anodo', 'N/A'))
            model_html = model_html.replace('{{specHerramientas}}', ', '.join(specs.get('herramientas', [])))
            model_html = model_html.replace('{{errorTableRows}}', error_rows)
            model_html = model_html.replace('{{maintAnodo}}', maint.get('anodo', 'Anualmente'))
            model_html = model_html.replace('{{maintLimpieza}}', maint.get('limpieza', 'Cada 2 años'))
            model_html = model_html.replace('{{maintValvula}}', maint.get('valvula', 'Semestralmente'))
            model_html = model_html.replace('{{extraHead}}', '')
            model_html = model_html.replace('id="modelos"', 'id="modelos" style="display:none;"')
            
            write_file(brand_dir / 'modelos' / f'{model["id"]}.html', model_html)
            pages_created += 1
    
    print(f"\n[OK] {pages_created} paginas HTML creadas")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    print(f"[*] Total secciones generadas: {total_sections}")
    print(f"[*] API calls realizadas: {api_calls}")
    print(f"[*] Contenido cacheado en: {SECTIONS_CONTENT_FILE}")
    print(f"[*] Paginas HTML: {pages_created} archivos en {PUBLIC_DIR}")
    print("\n[DONE] Generacion completa!")

if __name__ == "__main__":
    build_all_content()
