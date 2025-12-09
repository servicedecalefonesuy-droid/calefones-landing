import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / 'public'

def corregir_enlaces_modelos():
    """Corrige enlaces relativos en páginas de modelos"""
    print("[*] Corrigiendo enlaces en páginas de modelos")
    print("=" * 70)
    
    archivos_corregidos = 0
    total_cambios = 0
    
    # Buscar todos los archivos en carpetas modelos/
    for html_file in PUBLIC_DIR.rglob('modelos/*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Contar cambios a realizar
            cambios = content.count('href="./reparaciones/')
            
            if cambios > 0:
                # Corregir: ./reparaciones/ -> ../reparaciones/
                content = content.replace('href="./reparaciones/', 'href="../reparaciones/')
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                archivos_corregidos += 1
                total_cambios += cambios
                
                rel_path = html_file.relative_to(PUBLIC_DIR)
                print(f"[OK] {rel_path} - {cambios} enlaces corregidos")
        
        except Exception as e:
            print(f"[ERROR] {html_file}: {str(e)}")
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"[*] Archivos corregidos: {archivos_corregidos}")
    print(f"[*] Enlaces reparados: {total_cambios}")
    print(f"[*] Correccion: ./reparaciones/ -> ../reparaciones/")
    print("\n[DONE] Reparacion completa!")

if __name__ == "__main__":
    corregir_enlaces_modelos()
