import json
import os

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
BRANDS_FILE = os.path.join(DATA_DIR, 'brands.json')
CATALOG_FILE = os.path.join(DATA_DIR, 'catalog.json')

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    # Usar utf-8-sig para manejar BOM si existe (común en PowerShell/Windows)
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def enrich_catalog():
    brands = load_json(BRANDS_FILE)
    catalog = load_json(CATALOG_FILE)
    
    # Crear un set de marcas que ya existen en el catálogo para búsqueda rápida
    existing_brands = {item['brand'] for item in catalog}
    
    print(f"Marcas totales: {len(brands)}")
    print(f"Marcas ya en catálogo: {len(existing_brands)}")
    
    new_entries = 0
    
    for brand in brands:
        # Buscar si la marca ya existe en el catálogo
        brand_entry = next((item for item in catalog if item['brand'] == brand), None)
        
        if not brand_entry:
            print(f"Generando datos base para nueva marca: {brand}")
            brand_entry = {
                "brand": brand,
                "models": [
                    {
                        "id": "estandar-electrico",
                        "name": "Línea Estándar / Clásica",
                        "description": f"Termotanque eléctrico convencional de {brand}, disponible en 30, 60 y 80 litros.",
                        "specs": {
                            "resistencia": "Blindada (Tipo Rosca 1 1/4\" o Brida según año)",
                            "termostato": "De Varilla (Tipo Italiano)",
                            "anodo": "Barra de Magnesio (Rosca M6/M8)",
                            "herramientas": ["Llave de tubo", "Destornillador", "Multímetro"]
                        }
                    }
                ]
            }
            catalog.append(brand_entry)
            new_entries += 1
        
        # Enriquecer modelos existentes con nuevos campos si faltan
        for model in brand_entry['models']:
            updated = False
            
            # 1. Códigos de Error (Genéricos si no existen)
            if 'error_codes' not in model:
                model['error_codes'] = [
                    {"code": "Luz Apagada", "desc": "Falta de energía o termostato cortado", "sol": "Revisar enchufe y botón de reset"},
                    {"code": "Goteo Inferior", "desc": "Pinchadura o brida floja", "sol": "Cambiar junta o ánodo"},
                    {"code": "Agua Tibia", "desc": "Resistencia con sarro o falla parcial", "sol": "Limpiar o cambiar resistencia"}
                ]
                updated = True
            
            # 2. Intervalo de Mantenimiento
            if 'maintenance' not in model:
                model['maintenance'] = {
                    "anodo": "Cada 12-18 meses",
                    "limpieza": "Cada 2 años",
                    "valvula": "Verificar cada 6 meses"
                }
                updated = True

            # 3. Keywords para video (para búsqueda futura)
            if 'video_keywords' not in model:
                model['video_keywords'] = f"reparar calefon {brand} {model['name']}"
                updated = True

            if updated:
                print(f"  -> Enriqueciendo modelo {model['id']} de {brand}")
                new_entries += 1 # Contamos actualizaciones también

    if new_entries > 0:
        save_json(CATALOG_FILE, catalog)
        print(f"\n¡Éxito! Se actualizaron/crearon {new_entries} entradas.")
    else:
        print("\nEl catálogo ya estaba completo y actualizado.")

if __name__ == "__main__":
    enrich_catalog()
