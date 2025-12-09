import os
from pathlib import Path
import re

BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / 'public'

# Mapeo de enlaces incorrectos a correctos
LINK_FIXES = {
    'href="/contacto.html"': 'href="https://casadelcalefon.uy/contacto"',
    'href="/privacidad.html"': 'href="https://casadelcalefon.uy/privacidad"',
    'href="/terminos.html"': 'href="https://casadelcalefon.uy/terminos"',
}

def fix_links_in_file(file_path):
    """Corrige enlaces rotos en un archivo HTML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        for old_link, new_link in LINK_FIXES.items():
            if old_link in content:
                content = content.replace(old_link, new_link)
                changes_made += content.count(new_link) - original_content.count(new_link)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made
        
        return 0
    
    except Exception as e:
        print(f"[ERROR] {file_path}: {e}")
        return 0

def fix_all_links():
    """Corrige todos los enlaces en todas las páginas HTML"""
    print("[*] Corrigiendo enlaces rotos en todas las paginas...")
    print("=" * 60)
    
    total_files = 0
    total_fixes = 0
    
    # Recorrer todas las páginas HTML
    for html_file in PUBLIC_DIR.rglob('*.html'):
        fixes = fix_links_in_file(html_file)
        if fixes > 0:
            total_files += 1
            total_fixes += fixes
            print(f"[OK] {html_file.relative_to(PUBLIC_DIR)} - {fixes} enlaces corregidos")
    
    print("\n" + "=" * 60)
    print(f"[DONE] {total_files} archivos modificados")
    print(f"[DONE] {total_fixes} enlaces corregidos en total")

if __name__ == "__main__":
    fix_all_links()
