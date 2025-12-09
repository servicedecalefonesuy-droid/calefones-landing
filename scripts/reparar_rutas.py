import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / 'public'

# El problema: los enlaces apuntan a "cambiar-termostato.html"
# pero el archivo real es "reemplazar-termostato.html"

ENLACES_INCORRECTOS = [
    # Rutas relativas
    ('./reparaciones/cambiar-termostato.html', './reparaciones/reemplazar-termostato.html'),
    # Rutas absolutas
    ('/reparaciones/cambiar-termostato.html', '/reparaciones/reemplazar-termostato.html'),
]

# Generar correcciones para todas las marcas
MARCAS = [
    'ariston', 'atlantic', 'beusa', 'bosch', 'brilliant', 'bronx', 'collerati',
    'cyprium', 'delne', 'dikler', 'eldom', 'enxuta', 'fagor', 'ganim', 'geloso',
    'hyundai', 'ideal', 'ima', 'james', 'joya', 'kroser', 'midea', 'orion',
    'pacific', 'panavox', 'peabody', 'punktal', 'queen', 'rotel', 'sevan',
    'sirium', 'smartlife', 'steigleder', 'telefunken', 'tem', 'thermor',
    'thompson', 'ufesa', 'warners', 'wnr', 'xion', 'zero-watt'
]

def reparar_enlaces_archivo(filepath):
    """Repara enlaces rotos en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cambios = 0
        original = content
        
        # Reparar enlaces relativos
        if './reparaciones/cambiar-termostato.html' in content:
            content = content.replace(
                './reparaciones/cambiar-termostato.html',
                './reparaciones/reemplazar-termostato.html'
            )
            cambios += 1
        
        # Reparar enlaces absolutos para cada marca
        for marca in MARCAS:
            enlace_malo = f'/{marca}/reparaciones/cambiar-termostato.html'
            enlace_bueno = f'/{marca}/reparaciones/reemplazar-termostato.html'
            
            if enlace_malo in content:
                content = content.replace(enlace_malo, enlace_bueno)
                cambios += 1
        
        if cambios > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return cambios
        
        return 0
    
    except Exception as e:
        print(f"[ERROR] {filepath}: {str(e)}")
        return 0

def reparar_todas_rutas():
    """Repara todas las rutas incorrectas"""
    print("[*] Reparando enlaces rotos: cambiar-termostato -> reemplazar-termostato")
    print("=" * 70)
    
    total_archivos = 0
    total_cambios = 0
    
    # Procesar todos los archivos HTML
    for html_file in PUBLIC_DIR.rglob('*.html'):
        cambios = reparar_enlaces_archivo(html_file)
        
        if cambios > 0:
            total_archivos += 1
            total_cambios += cambios
            rel_path = html_file.relative_to(PUBLIC_DIR)
            print(f"[OK] {rel_path} - {cambios} enlaces corregidos")
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"[*] Archivos modificados: {total_archivos}")
    print(f"[*] Enlaces corregidos: {total_cambios}")
    print("\n[DONE] Reparacion completa!")
    print("\nAhora ejecuta:")
    print("  git add .")
    print("  git commit -m 'Corregidos enlaces cambiar-termostato -> reemplazar-termostato'")
    print("  git push origin main")
    print("  npx wrangler pages deploy public --project-name=arreglar-calefon-gratis-uruguay")

if __name__ == "__main__":
    reparar_todas_rutas()
