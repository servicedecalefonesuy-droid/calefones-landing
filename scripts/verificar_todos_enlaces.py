import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / 'public'

def verificar_enlace_existe(archivo_origen, enlace):
    """Verifica si un enlace apunta a un archivo existente"""
    # Ignorar enlaces externos
    if enlace.startswith('http://') or enlace.startswith('https://'):
        return True, None
    
    # Ignorar anclas y JavaScript
    if enlace.startswith('#') or enlace.startswith('javascript:'):
        return True, None
    
    # Resolver la ruta del archivo destino
    directorio_origen = archivo_origen.parent
    
    try:
        if enlace.startswith('/'):
            # Ruta absoluta desde public/
            archivo_destino = PUBLIC_DIR / enlace.lstrip('/')
        elif enlace.startswith('./'):
            # Ruta relativa desde el archivo actual
            archivo_destino = (directorio_origen / enlace[2:]).resolve()
        elif enlace.startswith('../'):
            # Ruta relativa subiendo niveles
            archivo_destino = (directorio_origen / enlace).resolve()
        else:
            # Ruta relativa simple
            archivo_destino = (directorio_origen / enlace).resolve()
        
        # Verificar si existe
        if archivo_destino.exists():
            return True, None
        else:
            return False, str(archivo_destino.relative_to(PUBLIC_DIR))
    
    except Exception as e:
        return False, f"Error: {str(e)}"

def analizar_archivo(html_file):
    """Analiza un archivo HTML en busca de enlaces rotos"""
    errores = []
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar todos los enlaces href
        patron = r'href=["\'](.*?)["\']'
        enlaces = re.findall(patron, content)
        
        for enlace in enlaces:
            # Solo verificar enlaces .html
            if '.html' in enlace:
                existe, ruta_esperada = verificar_enlace_existe(html_file, enlace)
                
                if not existe:
                    errores.append({
                        'enlace': enlace,
                        'esperado': ruta_esperada
                    })
    
    except Exception as e:
        print(f"[ERROR] No se pudo leer {html_file}: {str(e)}")
    
    return errores

def verificar_todos_archivos():
    """Verifica todos los archivos HTML"""
    print("[*] Verificando TODOS los archivos HTML del sitio")
    print("=" * 70)
    
    total_archivos = 0
    archivos_con_errores = 0
    total_errores = 0
    errores_detallados = {}
    
    # Analizar todos los archivos HTML
    for html_file in sorted(PUBLIC_DIR.rglob('*.html')):
        total_archivos += 1
        
        errores = analizar_archivo(html_file)
        
        if errores:
            archivos_con_errores += 1
            total_errores += len(errores)
            
            rel_path = str(html_file.relative_to(PUBLIC_DIR))
            errores_detallados[rel_path] = errores
            
            print(f"\n[!] {rel_path}")
            for error in errores[:3]:  # Mostrar solo primeros 3 por archivo
                print(f"    ❌ {error['enlace']}")
                if error['esperado']:
                    print(f"       Esperado: {error['esperado']}")
            
            if len(errores) > 3:
                print(f"    ... y {len(errores) - 3} errores más")
    
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print(f"[*] Total archivos analizados: {total_archivos}")
    print(f"[*] Archivos con errores: {archivos_con_errores}")
    print(f"[*] Total enlaces rotos: {total_errores}")
    
    if archivos_con_errores == 0:
        print("\n✅ ¡NO SE ENCONTRARON ENLACES ROTOS!")
        print("✅ Todos los enlaces apuntan a archivos existentes")
    else:
        print("\n⚠️  Se encontraron enlaces rotos que necesitan corrección")
        
        # Agrupar por tipo de error
        errores_por_tipo = {}
        for archivo, errores in errores_detallados.items():
            for error in errores:
                enlace = error['enlace']
                if enlace not in errores_por_tipo:
                    errores_por_tipo[enlace] = []
                errores_por_tipo[enlace].append(archivo)
        
        print("\nENLACES MÁS COMUNES:")
        for enlace, archivos in sorted(errores_por_tipo.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"  • {enlace}")
            print(f"    Aparece en {len(archivos)} archivo(s)")
    
    return total_errores

if __name__ == "__main__":
    verificar_todos_archivos()
