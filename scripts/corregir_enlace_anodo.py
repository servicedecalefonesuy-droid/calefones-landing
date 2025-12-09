import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / 'public'

def corregir_enlaces_anodo():
    """Corrige enlaces a mantenimiento-anodo por cambiar-anodo"""
    print("[*] Corrigiendo enlaces: mantenimiento-anodo -> cambiar-anodo")
    print("=" * 70)
    
    archivos_corregidos = 0
    total_cambios = 0
    
    # Buscar en todos los archivos HTML
    for html_file in PUBLIC_DIR.rglob('*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar el enlace incorrecto
            if 'mantenimiento-anodo.html' in content:
                # Contar ocurrencias
                cambios = content.count('mantenimiento-anodo.html')
                
                # Reemplazar
                content = content.replace('mantenimiento-anodo.html', 'cambiar-anodo.html')
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                archivos_corregidos += 1
                total_cambios += cambios
                
                rel_path = html_file.relative_to(PUBLIC_DIR)
                print(f"[OK] {rel_path} - {cambios} enlace(s) corregido(s)")
        
        except Exception as e:
            print(f"[ERROR] {html_file}: {str(e)}")
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"[*] Archivos corregidos: {archivos_corregidos}")
    print(f"[*] Enlaces reparados: {total_cambios}")
    print(f"[*] Corrección: mantenimiento-anodo.html -> cambiar-anodo.html")
    print("\n[DONE] Reparación completa!")

if __name__ == "__main__":
    corregir_enlaces_anodo()
