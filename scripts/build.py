import os
import json
from pathlib import Path

# Configuración
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
TEMPLATES_DIR = BASE_DIR / 'documentacion'
PUBLIC_DIR = BASE_DIR / 'public'

BRANDS_FILE = DATA_DIR / 'brands.json'
CATALOG_FILE = DATA_DIR / 'catalog.json'

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
        return []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

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

def build_site():
    """Genera el sitio completo"""
    print("🚀 Iniciando construcción del sitio...")
    
    # Cargar datos
    brands_list = load_json(BRANDS_FILE)
    catalog = load_json(CATALOG_FILE)
    
    # Indexar catálogo por marca
    catalog_map = {item['brand']: item for item in catalog}
    
    # Cargar plantilla maestra
    layout_template = read_template('plantilla_maestra.html')
    
    if not layout_template:
        print("❌ Error: No se encontró la plantilla maestra")
        return
    
    print(f"📦 Procesando {len(brands_list)} marcas...")
    
    for brand in brands_list:
        print(f"   └─ {brand}")
        slug = brand.replace(' ', '-').lower()
        brand_dir = PUBLIC_DIR / slug
        
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
        page_content = f'''
        <div class="prose prose-lg max-w-none">
            <p class="lead">Encuentra guías técnicas especializadas para la reparación y mantenimiento de calefones eléctricos <strong>{brand}</strong>.</p>
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
        final_html = final_html.replace('{{extraHead}}', '')
        
        # Ocultar secciones que no aplican en index
        final_html = final_html.replace('id="specs"', 'id="specs" style="display:none;"')
        final_html = final_html.replace('id="errores"', 'id="errores" style="display:none;"')
        final_html = final_html.replace('id="mantenimiento"', 'id="mantenimiento" style="display:none;"')
        
        write_file(brand_dir / 'index.html', final_html)
        
        # Generar páginas de modelos específicos
        if brand_data and brand_data.get('models'):
            for m in brand_data['models']:
                specs = m.get('specs', {})
                
                # Generar sección de repuestos
                spare_parts_section = generate_spare_parts_section(specs)
                
                # Contenido del modelo
                model_intro = f'''
                <div class="prose prose-lg max-w-none">
                    <p class="lead">{m['description']}</p>
                    <p>A continuación encontrarás las especificaciones técnicas completas y los repuestos compatibles para el modelo <strong>{m['name']}</strong> de {brand}.</p>
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
                final_model = final_model.replace('{{introContent}}', model_intro)
                
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
                
                # Insertar sección de repuestos antes del mantenimiento
                final_model = final_model.replace('<!-- SECCIÓN 7: Plan de Mantenimiento', spare_parts_section + '\n\n        <!-- SECCIÓN 7: Plan de Mantenimiento')
                
                # Ocultar selector de modelos en página de modelo
                final_model = final_model.replace('id="modelos"', 'id="modelos" style="display:none;"')
                
                final_model = final_model.replace('{{modelListHtml}}', '')
                final_model = final_model.replace('{{extraHead}}', '')
                
                write_file(brand_dir / 'modelos' / f'{m["id"]}.html', final_model)
    
    print("✅ Construcción completada exitosamente!")
    print(f"📁 Sitio generado en: {PUBLIC_DIR}")

if __name__ == "__main__":
    build_site()
