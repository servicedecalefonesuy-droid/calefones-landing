import os
import json
import shutil

# Configuración
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

BRANDS_FILE = os.path.join(DATA_DIR, 'brands.json')
CATALOG_FILE = os.path.join(DATA_DIR, 'catalog.json')

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def read_template(filename):
    path = os.path.join(TEMPLATES_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def build_site():
    print("Iniciando construcción del sitio con Python...")
    
    # Cargar datos
    brands_list = load_json(BRANDS_FILE)
    catalog = load_json(CATALOG_FILE)
    
    # Indexar catálogo por marca para acceso rápido
    catalog_map = {item['brand']: item for item in catalog}
    
    # Obtener lista de templates (excluyendo modelo.html que es especial)
    templates = []
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file == 'modelo.html':
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, TEMPLATES_DIR)
            templates.append(rel_path)
            
    model_template = read_template('modelo.html')

    for brand in brands_list:
        print(f"Procesando: {brand}")
        slug = brand.replace(' ', '-').lower()
        brand_dir = os.path.join(PUBLIC_DIR, slug)
        
        # Datos del catálogo para esta marca
        brand_data = catalog_map.get(brand)
        
        # Generar HTML de lista de modelos
        model_list_html = ""
        if brand_data and brand_data.get('models'):
            model_list_html = "<ul class='model-list'>"
            for m in brand_data['models']:
                model_list_html += f"<li><a href='./modelos/{m['id']}.html'><strong>{m['name']}</strong></a>: {m['description']}</li>"
            model_list_html += "</ul>"
        else:
            model_list_html = "<p>Selecciona la guía general a continuación.</p>"

        # 1. Generar páginas estándar (index, fallas, reparaciones)
        for tpl_rel_path in templates:
            tpl_content = read_template(tpl_rel_path)
            
            # Reemplazos
            output = tpl_content.replace('{{brand}}', brand)
            output = output.replace('{{modelListHtml}}', model_list_html)
            
            dest_path = os.path.join(brand_dir, tpl_rel_path)
            write_file(dest_path, output)

        # 2. Generar páginas de modelos específicos
        if brand_data and brand_data.get('models'):
            for m in brand_data['models']:
                m_content = model_template.replace('{{brand}}', brand)
                m_content = m_content.replace('{{modelName}}', m['name'])
                m_content = m_content.replace('{{modelDesc}}', m['description'])
                
                specs = m.get('specs', {})
                m_content = m_content.replace('{{specResistencia}}', specs.get('resistencia', 'N/A'))
                m_content = m_content.replace('{{specTermostato}}', specs.get('termostato', 'N/A'))
                m_content = m_content.replace('{{specAnodo}}', specs.get('anodo', 'N/A'))
                
                tools = specs.get('herramientas', [])
                tools_str = ", ".join(tools) if isinstance(tools, list) else str(tools)
                m_content = m_content.replace('{{specHerramientas}}', tools_str)
                
                # Nuevos campos enriquecidos
                # 1. Tabla de errores
                error_rows = ""
                for err in m.get('error_codes', []):
                    error_rows += f"<tr><td>{err['code']}</td><td>{err['desc']}</td><td>{err['sol']}</td></tr>"
                m_content = m_content.replace('{{errorTableRows}}', error_rows)

                # 2. Mantenimiento
                maint = m.get('maintenance', {})
                m_content = m_content.replace('{{maintAnodo}}', maint.get('anodo', 'Anualmente'))
                m_content = m_content.replace('{{maintLimpieza}}', maint.get('limpieza', 'Cada 2 años'))
                m_content = m_content.replace('{{maintValvula}}', maint.get('valvula', 'Semestralmente'))

                # 3. Video Keywords (URL encoded simple)
                vid_keys = m.get('video_keywords', f"reparacion calefon {brand}").replace(' ', '+')
                m_content = m_content.replace('{{videoKeywords}}', vid_keys)

                dest_path = os.path.join(brand_dir, 'modelos', f"{m['id']}.html")
                write_file(dest_path, m_content)

    print("Construcción completada exitosamente.")

if __name__ == "__main__":
    build_site()
