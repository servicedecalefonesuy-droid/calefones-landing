import os
import json
import time
import requests
from pathlib import Path
import re

# Configuración
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
PUBLIC_DIR = BASE_DIR / 'public'
BRANDS_FILE = DATA_DIR / 'brands.json'
VALVULA_CONTENT_FILE = DATA_DIR / 'valvula_content.json'

# API de Gemini
GEMINI_API_KEY = "AIzaSyAt6AiC-LSf9IMe3HGPz-pf-uSZLaTjI7I"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

# URLs de tienda
STORE_URL = "https://casadelcalefon.uy"

def load_json(filepath):
    """Carga un archivo JSON"""
    if not filepath.exists():
        return {} if 'valvula' in filepath.name else []
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

def generate_valvula_content(brand):
    """Genera contenido para cambio de válvula"""
    
    prompt = f"""Eres un técnico experto en reparación de calefones eléctricos {brand} en Uruguay.

Genera una guía PASO A PASO detallada para: **Cambiar Válvula de Seguridad** en calefones {brand}.

ESTRUCTURA HTML REQUERIDA:

<!-- Introducción -->
<div class="bg-gradient-to-r from-orange-50 to-orange-100 p-6 rounded-lg mb-8">
    <h2 class="text-2xl font-bold text-gray-800 mb-4"><i class="fas fa-shield-alt text-orange-600 mr-3"></i>Cambiar Válvula de Seguridad - {brand}</h2>
    <p class="text-gray-700 mb-3">La válvula de seguridad es un componente crítico que protege tu calefón {brand} contra sobrepresión. Su reemplazo periódico previene fugas y daños mayores.</p>
    <div class="flex gap-4 mt-4">
        <span class="bg-white px-4 py-2 rounded-full text-sm"><i class="far fa-clock mr-2"></i><strong>Tiempo:</strong> 15-20 min</span>
        <span class="bg-white px-4 py-2 rounded-full text-sm"><i class="fas fa-signal mr-2"></i><strong>Dificultad:</strong> Fácil</span>
        <span class="bg-white px-4 py-2 rounded-full text-sm"><i class="fas fa-dollar-sign mr-2"></i><strong>Costo:</strong> Bajo</span>
    </div>
</div>

<!-- Herramientas Necesarias -->
<div class="bg-white p-6 rounded-lg shadow-md mb-8">
    <h3 class="text-xl font-bold text-gray-800 mb-4"><i class="fas fa-toolbox text-orange-600 mr-2"></i>Herramientas y Materiales</h3>
    <div class="grid md:grid-cols-2 gap-4">
        <ul class="space-y-2">
            <li><i class="fas fa-check text-green-600 mr-2"></i>Llave inglesa o francesa</li>
            <li><i class="fas fa-check text-green-600 mr-2"></i>Cinta teflón (PTFE)</li>
            <li><i class="fas fa-check text-green-600 mr-2"></i>Trapo o toalla</li>
        </ul>
        <ul class="space-y-2">
            <li><i class="fas fa-check text-green-600 mr-2"></i>Válvula nueva 3/4" o 1/2"</li>
            <li><i class="fas fa-check text-green-600 mr-2"></i>Balde (para agua residual)</li>
            <li><i class="fas fa-check text-green-600 mr-2"></i>Guantes de trabajo</li>
        </ul>
    </div>
</div>

<!-- Medidas de Seguridad -->
<div class="bg-red-50 border-l-4 border-red-500 p-6 mb-8">
    <h3 class="text-xl font-bold text-red-800 mb-3"><i class="fas fa-exclamation-triangle mr-2"></i>Medidas de Seguridad</h3>
    <ul class="space-y-2 text-gray-700">
        <li><i class="fas fa-tint text-blue-600 mr-2"></i><strong>Cerrar llave de paso:</strong> Cortar suministro de agua fría</li>
        <li><i class="fas fa-bolt text-red-600 mr-2"></i><strong>Desconectar electricidad:</strong> Por seguridad adicional</li>
        <li><i class="fas fa-fire text-orange-600 mr-2"></i><strong>Esperar enfriamiento:</strong> Dejar enfriar al menos 2 horas</li>
        <li><i class="fas fa-hard-hat text-yellow-600 mr-2"></i><strong>Guantes:</strong> Proteger manos de agua caliente residual</li>
    </ul>
</div>

<!-- Procedimiento Paso a Paso -->
<div class="bg-white p-6 rounded-lg shadow-md mb-8">
    <h3 class="text-xl font-bold text-gray-800 mb-6"><i class="fas fa-list-ol text-orange-600 mr-2"></i>Procedimiento Paso a Paso</h3>
    
    <div class="space-y-6">
        <!-- Paso 1 -->
        <div class="border-l-4 border-orange-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-orange-600 text-white px-3 py-1 rounded-full mr-2">1</span>Cerrar Suministro de Agua</h4>
            <p class="text-gray-700 mb-2">Cierra completamente la llave de paso de agua fría que alimenta el calefón {brand}. Abre una canilla de agua caliente para despresurizar el sistema.</p>
            <div class="bg-blue-50 p-3 rounded mt-2">
                <p class="text-sm text-blue-800"><i class="fas fa-lightbulb mr-2"></i><strong>Consejo:</strong> Coloca un balde debajo de la válvula para recoger agua residual.</p>
            </div>
        </div>
        
        <!-- Paso 2 -->
        <div class="border-l-4 border-orange-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-orange-600 text-white px-3 py-1 rounded-full mr-2">2</span>Drenar Agua del Calefón</h4>
            <p class="text-gray-700">Abre la válvula de drenaje (si tiene) o levanta la palanca de la válvula de seguridad actual para vaciar parte del agua. Esto reducirá el caudal al desarmar.</p>
        </div>
        
        <!-- Paso 3 -->
        <div class="border-l-4 border-orange-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-orange-600 text-white px-3 py-1 rounded-full mr-2">3</span>Desenroscar Válvula Vieja</h4>
            <p class="text-gray-700">Usando la llave inglesa, desenrosca la válvula de seguridad antigua en sentido antihorario. Ten el balde listo para agua que pueda salir. Si está muy dura, aplica aceite penetrante y espera 10 minutos.</p>
        </div>
        
        <!-- Paso 4 -->
        <div class="border-l-4 border-orange-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-orange-600 text-white px-3 py-1 rounded-full mr-2">4</span>Limpiar la Rosca</h4>
            <p class="text-gray-700">Limpia la rosca del calefón con un trapo, eliminando restos de teflón viejo, óxido o sedimentos. Una rosca limpia asegura un sellado perfecto.</p>
        </div>
        
        <!-- Paso 5 -->
        <div class="border-l-4 border-orange-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-orange-600 text-white px-3 py-1 rounded-full mr-2">5</span>Aplicar Teflón a Válvula Nueva</h4>
            <p class="text-gray-700">Envuelve la rosca de la válvula nueva con cinta teflón, dando 8-10 vueltas en sentido horario. Asegúrate de no cubrir el primer hilo de rosca.</p>
            <div class="bg-blue-50 p-3 rounded mt-2">
                <p class="text-sm text-blue-800"><i class="fas fa-lightbulb mr-2"></i><strong>Tip:</strong> El teflón debe aplicarse en la misma dirección del enroscado para evitar que se despegue.</p>
            </div>
        </div>
        
        <!-- Paso 6 -->
        <div class="border-l-4 border-orange-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-orange-600 text-white px-3 py-1 rounded-full mr-2">6</span>Instalar Válvula Nueva</h4>
            <p class="text-gray-700">Enrosca manualmente la válvula nueva hasta donde sea posible. Luego, con la llave inglesa, aprieta firmemente (sin excederte para no dañar la rosca). La válvula debe quedar orientada con la salida hacia abajo.</p>
        </div>
        
        <!-- Paso 7 -->
        <div class="border-l-4 border-orange-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-orange-600 text-white px-3 py-1 rounded-full mr-2">7</span>Abrir Agua Gradualmente</h4>
            <p class="text-gray-700">Abre lentamente la llave de paso principal. Observa la válvula nueva mientras se llena el calefón. Busca posibles fugas alrededor de la rosca.</p>
        </div>
        
        <!-- Paso 8 -->
        <div class="border-l-4 border-orange-500 pl-6">
            <h4 class="text-lg font-bold text-gray-800 mb-2"><span class="bg-orange-600 text-white px-3 py-1 rounded-full mr-2">8</span>Verificar Funcionamiento</h4>
            <p class="text-gray-700">Levanta la palanca de la válvula para probar que drena correctamente. Debe salir agua por el desagüe. Conecta la electricidad y calienta agua. La válvula puede gotear levemente al calentar (es normal).</p>
        </div>
    </div>
</div>

<!-- Problemas Comunes -->
<div class="bg-yellow-50 p-6 rounded-lg mb-8">
    <h3 class="text-xl font-bold text-gray-800 mb-4"><i class="fas fa-wrench text-yellow-600 mr-2"></i>Problemas Comunes y Soluciones</h3>
    <div class="space-y-4">
        <div>
            <h4 class="font-bold text-gray-800 mb-1"><i class="fas fa-exclamation-circle text-yellow-600 mr-2"></i>La válvula gotea después de instalar</h4>
            <p class="text-gray-700 pl-6">Desenrosca, agrega más teflón (12-15 vueltas) y vuelve a instalar apretando más firmemente.</p>
        </div>
        <div>
            <h4 class="font-bold text-gray-800 mb-1"><i class="fas fa-exclamation-circle text-yellow-600 mr-2"></i>No puedo sacar la válvula vieja</h4>
            <p class="text-gray-700 pl-6">Aplica WD-40 o aflojatodo, espera 15 minutos y usa una llave de mayor palanca. Si está muy oxidada, considera llamar a un técnico.</p>
        </div>
        <div>
            <h4 class="font-bold text-gray-800 mb-1"><i class="fas fa-exclamation-circle text-yellow-600 mr-2"></i>La válvula drena constantemente</h4>
            <p class="text-gray-700 pl-6">Es probable que la presión de red sea muy alta. Instala un regulador de presión (máx 4 bar recomendado para {brand}).</p>
        </div>
    </div>
</div>

<!-- Verificación Final -->
<div class="bg-green-50 p-6 rounded-lg mb-8">
    <h3 class="text-xl font-bold text-gray-800 mb-4"><i class="fas fa-check-double text-green-600 mr-2"></i>Verificación Final</h3>
    <ul class="space-y-2">
        <li><i class="fas fa-check-square text-green-600 mr-2"></i>No hay fugas visibles alrededor de la válvula</li>
        <li><i class="fas fa-check-square text-green-600 mr-2"></i>La palanca de alivio funciona correctamente</li>
        <li><i class="fas fa-check-square text-green-600 mr-2"></i>El agua sale caliente después de 15-20 minutos</li>
        <li><i class="fas fa-check-square text-green-600 mr-2"></i>La válvula drena al levantar la palanca y cierra al soltarla</li>
    </ul>
</div>

<!-- CTA Comprar Repuesto -->
<div class="bg-gradient-to-r from-orange-600 to-orange-700 text-white p-8 rounded-lg text-center">
    <h3 class="text-2xl font-bold mb-3">¿Necesitás una Válvula Nueva?</h3>
    <p class="text-orange-100 mb-6">Comprá válvulas de seguridad originales para {brand} con envío a todo Uruguay</p>
    <a href="{STORE_URL}/valvulas-seguridad" class="inline-block bg-white text-orange-700 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition text-lg">
        <i class="fas fa-shopping-cart mr-2"></i>Ver Válvulas en Tienda
    </a>
</div>

IMPORTANTE:
- 8 pasos detallados específicos para {brand}
- Mencionar precauciones específicas de modelos {brand}
- Lenguaje claro para usuario uruguayo
- NO incluyas etiquetas de estructura (html, body, head)
- Solo fragmentos HTML directos
- Longitud: 700-900 palabras"""

    content = call_gemini_api(prompt)
    return clean_html(content) if content else None

def create_valvula_page_html(brand, slug, content):
    """Crea el HTML completo de la página de cambio de válvula"""
    
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cambiar Válvula de Seguridad - Calefón {brand} | Guía Paso a Paso</title>
    <meta name="description" content="Guía completa paso a paso para cambiar la válvula de seguridad en calefones {brand}. Herramientas, medidas de seguridad y procedimiento detallado.">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://calefones-landing.pages.dev/{slug}/reparaciones/cambiar-valvula.html">
    
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
                <span class="text-gray-700">Cambiar Válvula</span>
            </nav>
        </div>
    </div>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-12 max-w-4xl">
        
        {content if content else '<p>Contenido de cambio de válvula para {brand} en desarrollo.</p>'}
        
        <!-- Otras Reparaciones -->
        <div class="mt-12 bg-white p-6 rounded-lg shadow-md">
            <h3 class="text-xl font-bold text-gray-800 mb-4">Otras Reparaciones de {brand}</h3>
            <div class="grid md:grid-cols-2 gap-4">
                <a href="/{slug}/reparaciones/cambiar-resistencia.html" class="block p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition">
                    <i class="fas fa-bolt text-blue-600 mr-2"></i><span class="font-semibold">Cambiar Resistencia</span>
                </a>
                <a href="/{slug}/reparaciones/reemplazar-termostato.html" class="block p-4 border border-gray-200 rounded-lg hover:border-green-500 hover:shadow-md transition">
                    <i class="fas fa-thermometer-half text-green-600 mr-2"></i><span class="font-semibold">Reemplazar Termostato</span>
                </a>
                <a href="/{slug}/reparaciones/cambiar-anodo.html" class="block p-4 border border-gray-200 rounded-lg hover:border-purple-500 hover:shadow-md transition">
                    <i class="fas fa-shield-alt text-purple-600 mr-2"></i><span class="font-semibold">Cambiar Ánodo</span>
                </a>
                <a href="/{slug}/reparaciones/reparar-fuga-agua.html" class="block p-4 border border-gray-200 rounded-lg hover:border-cyan-500 hover:shadow-md transition">
                    <i class="fas fa-tint text-cyan-600 mr-2"></i><span class="font-semibold">Reparar Fuga de Agua</span>
                </a>
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

def build_valvula_pages():
    """Genera todas las páginas de cambio de válvula"""
    print("[*] Generador de Paginas: Cambiar Valvula de Seguridad")
    print("[*] Total: 42 marcas")
    print("=" * 60)
    
    brands_list = load_json(BRANDS_FILE)
    valvula_cache = load_json(VALVULA_CONTENT_FILE)
    
    api_calls = 0
    pages_created = 0
    
    for brand_idx, brand in enumerate(brands_list, 1):
        slug = brand.replace(' ', '-').lower()
        cache_key = f"{slug}_cambiar_valvula"
        
        # Generar contenido si no existe en caché
        if cache_key not in valvula_cache:
            print(f"[{brand_idx}/42] {brand:20s} >> ", end='', flush=True)
            content = generate_valvula_content(brand)
            
            if content:
                valvula_cache[cache_key] = content
                save_json(VALVULA_CONTENT_FILE, valvula_cache)
                api_calls += 1
                print(f"[OK] API #{api_calls}")
                time.sleep(1.5)  # Rate limiting
            else:
                print("[FAIL]")
                content = f"<p>Guía de cambio de válvula para {brand} en desarrollo.</p>"
        else:
            content = valvula_cache[cache_key]
            print(f"[{brand_idx}/42] {brand:20s} >> [CACHE]")
        
        # Crear página HTML
        repair_dir = PUBLIC_DIR / slug / 'reparaciones'
        page_html = create_valvula_page_html(brand, slug, content)
        write_file(repair_dir / "cambiar-valvula.html", page_html)
        pages_created += 1
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    print(f"[*] Paginas creadas: {pages_created}/42")
    print(f"[*] API calls realizadas: {api_calls}")
    print(f"[*] Contenido cacheado en: {VALVULA_CONTENT_FILE}")
    print(f"[*] Paginas en: {PUBLIC_DIR}/[marca]/reparaciones/cambiar-valvula.html")
    print("\n[DONE] Generacion completa!")

if __name__ == "__main__":
    build_valvula_pages()
