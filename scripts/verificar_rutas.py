import os
import re
from pathlib import Path
import json

BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / 'public'
ERRORES_FILE = BASE_DIR / 'ERRORES_RUTAS.json'

def verificar_rutas():
    """Verifica todas las rutas y documenta errores"""
    print("[*] Analizando todas las rutas HTML...", flush=True)
    print("=" * 70, flush=True)
    
    errores = []
    total_enlaces = 0
    archivos_procesados = 0
    
    # Analizar cada archivo HTML
    for html_file in PUBLIC_DIR.rglob('*.html'):
        archivos_procesados += 1
        if archivos_procesados % 50 == 0:
            print(f"[INFO] Procesados {archivos_procesados} archivos...", flush=True)
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar todos los enlaces href
            enlaces = re.findall(r'href=["\']([^"\']*\.html)["\']', content)
            total_enlaces += len(enlaces)
            
            for enlace in enlaces:
                # Ignorar enlaces externos
                if enlace.startswith('http'):
                    continue
                
                # Resolver ruta del archivo destino
                if enlace.startswith('./'):
                    # Ruta relativa desde el archivo actual
                    archivo_destino = (html_file.parent / enlace[2:]).resolve()
                elif enlace.startswith('../'):
                    # Ruta relativa subiendo niveles
                    archivo_destino = (html_file.parent / enlace).resolve()
                elif enlace.startswith('/'):
                    # Ruta absoluta desde public/
                    archivo_destino = (PUBLIC_DIR / enlace[1:]).resolve()
                else:
                    # Ruta relativa simple
                    archivo_destino = (html_file.parent / enlace).resolve()
                
                # Verificar si el archivo existe
                if not archivo_destino.exists():
                    rel_origen = str(html_file.relative_to(PUBLIC_DIR))
                    
                    # Buscar archivos similares en el mismo directorio
                    directorio = archivo_destino.parent
                    nombre_esperado = archivo_destino.name
                    archivos_similares = []
                    
                    if directorio.exists():
                        for archivo in directorio.glob('*.html'):
                            if archivo.name != nombre_esperado:
                                # Calcular similitud (simple)
                                if nombre_esperado.replace('-', '') in archivo.name.replace('-', ''):
                                    archivos_similares.append(archivo.name)
                    
                    error = {
                        'archivo_origen': rel_origen,
                        'enlace_roto': enlace,
                        'ruta_esperada': str(archivo_destino.relative_to(PUBLIC_DIR)),
                        'archivos_similares': archivos_similares[:3]
                    }
                    
                    errores.append(error)
                    print(f"[ERROR] {rel_origen}")
                    print(f"  -> Enlace: {enlace}")
                    print(f"  -> Esperado: {error['ruta_esperada']}")
                    if archivos_similares:
                        print(f"  -> Similares: {', '.join(archivos_similares)}")
                    print()
        
        except Exception as e:
            print(f"[!] Error procesando {html_file}: {str(e)}")
    
    # Guardar errores en JSON
    with open(ERRORES_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'total_enlaces_analizados': total_enlaces,
            'total_errores': len(errores),
            'errores': errores
        }, f, ensure_ascii=False, indent=2)
    
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"[*] Enlaces analizados: {total_enlaces}")
    print(f"[*] Enlaces rotos encontrados: {len(errores)}")
    print(f"[*] Errores guardados en: {ERRORES_FILE}")
    print("\n[NEXT] Ejecuta 'python scripts/reparar_rutas.py' para corregir")
    
    return errores

if __name__ == "__main__":
    verificar_rutas()
