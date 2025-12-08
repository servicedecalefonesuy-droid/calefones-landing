import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / 'public'
SITEMAP_FILE = PUBLIC_DIR / 'sitemap.xml'
BASE_URL = "https://arreglar-calefon-gratis-uruguay.pages.dev"

def generate_sitemap():
    """Genera sitemap.xml con todas las URLs del sitio"""
    print("[*] Generando sitemap.xml...")
    
    urls = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Recopilar todas las páginas HTML
    for html_file in PUBLIC_DIR.rglob('*.html'):
        # Calcular URL relativa
        rel_path = html_file.relative_to(PUBLIC_DIR)
        url_path = str(rel_path).replace('\\', '/')
        
        # Prioridad según tipo de página
        if url_path == 'index.html':
            priority = '1.0'
            changefreq = 'weekly'
        elif '/modelos/' in url_path:
            priority = '0.8'
            changefreq = 'monthly'
        elif '/reparaciones/' in url_path:
            priority = '0.7'
            changefreq = 'monthly'
        elif url_path.endswith('/index.html'):
            priority = '0.9'
            changefreq = 'weekly'
        else:
            priority = '0.6'
            changefreq = 'monthly'
        
        # Convertir a URL completa
        if url_path == 'index.html':
            full_url = BASE_URL + '/'
        elif url_path.endswith('/index.html'):
            full_url = BASE_URL + '/' + url_path.replace('/index.html', '/')
        else:
            full_url = BASE_URL + '/' + url_path
        
        urls.append({
            'loc': full_url,
            'lastmod': today,
            'changefreq': changefreq,
            'priority': priority
        })
    
    # Ordenar URLs (homepage primero, luego alfabéticamente)
    urls.sort(key=lambda x: (x['loc'] != BASE_URL + '/', x['loc']))
    
    # Generar XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        xml_content += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml_content += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += '  </url>\n'
    
    xml_content += '</urlset>'
    
    # Guardar sitemap
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"[OK] Sitemap generado: {SITEMAP_FILE}")
    print(f"[OK] Total de URLs: {len(urls)}")
    print("\nPrimeras 5 URLs:")
    for url in urls[:5]:
        print(f"  - {url['loc']} (prioridad: {url['priority']})")
    print("\nÚltimas 3 URLs:")
    for url in urls[-3:]:
        print(f"  - {url['loc']} (prioridad: {url['priority']})")

if __name__ == "__main__":
    generate_sitemap()
