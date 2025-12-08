import os
from pathlib import Path

# Configuración
BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / 'public'

# Mapeo de enlaces incorrectos a correctos
LINK_FIXES = {
    './reparaciones/cambiar-termostato.html': './reparaciones/reemplazar-termostato.html',
    './reparaciones/mantenimiento-anodo.html': './reparaciones/cambiar-anodo.html',
}

def fix_links_in_file(filepath):
    """Corrige enlaces en un archivo HTML"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = 0
        
        for old_link, new_link in LINK_FIXES.items():
            if old_link in content:
                count = content.count(old_link)
                content = content.replace(old_link, new_link)
                fixes_applied += count
        
        if fixes_applied > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return fixes_applied
        
        return 0
    
    except Exception as e:
        print(f"[ERROR] {filepath}: {str(e)}")
        return 0

def fix_all_brand_pages():
    """Corrige enlaces en todas las páginas de marca"""
    print("[*] Corrigiendo enlaces de reparacion en paginas de marca...")
    print("=" * 60)
    
    total_files = 0
    total_fixes = 0
    
    # Buscar todos los index.html de marcas
    for brand_dir in PUBLIC_DIR.iterdir():
        if brand_dir.is_dir() and brand_dir.name not in ['modelos', 'reparaciones']:
            index_file = brand_dir / 'index.html'
            
            if index_file.exists():
                fixes = fix_links_in_file(index_file)
                if fixes > 0:
                    total_files += 1
                    total_fixes += fixes
                    print(f"[OK] {brand_dir.name:20s} >> {fixes} enlaces corregidos")
    
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"[*] Archivos modificados: {total_files}")
    print(f"[*] Enlaces corregidos: {total_fixes}")
    print("\n[DONE] Proceso completo!")

if __name__ == "__main__":
    fix_all_brand_pages()
