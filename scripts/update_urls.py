import os
from pathlib import Path

# Configuración
BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / 'public'

OLD_URL = "https://calefones-landing.pages.dev"
NEW_URL = "https://arreglar-calefon-gratis-uruguay.pages.dev"

def update_urls_in_file(filepath):
    """Actualiza URLs en un archivo HTML"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if OLD_URL in content:
            content = content.replace(OLD_URL, NEW_URL)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"[ERROR] {filepath}: {str(e)}")
        return False

def update_all_html_files():
    """Actualiza URLs en todos los archivos HTML"""
    print(f"[*] Actualizando URLs de {OLD_URL} a {NEW_URL}")
    print("=" * 70)
    
    total_files = 0
    updated_files = 0
    
    # Buscar todos los archivos HTML
    for html_file in PUBLIC_DIR.rglob('*.html'):
        total_files += 1
        if update_urls_in_file(html_file):
            updated_files += 1
            rel_path = html_file.relative_to(PUBLIC_DIR)
            print(f"[OK] {rel_path}")
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"[*] Archivos procesados: {total_files}")
    print(f"[*] Archivos actualizados: {updated_files}")
    print("\n[DONE] Proceso completo!")

if __name__ == "__main__":
    update_all_html_files()
