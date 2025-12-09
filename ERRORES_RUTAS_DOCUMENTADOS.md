# Documentación de Errores de Rutas Encontrados

## Problema Principal

**Inconsistencia en nombres de archivos de reparación de termostato:**

- **Enlace en las páginas**: `cambiar-termostato.html`
- **Archivo real**: `reemplazar-termostato.html`

### Archivos Afectados

**Todas las 42 marcas** tienen este problema en:
1. Páginas principales de marca (`/[marca]/index.html`)
2. Páginas de modelos (`/[marca]/modelos/*.html`)
3. Páginas de otras reparaciones (enlaces cruzados)

### Ejemplos Específicos

```
❌ Enlace roto: /bronx/reparaciones/cambiar-termostato.html
✅ Archivo real: /bronx/reparaciones/reemplazar-termostato.html

❌ Enlace roto: /atlantic/reparaciones/cambiar-termostato.html  
✅ Archivo real: /atlantic/reparaciones/reemplazar-termostato.html

❌ Enlace roto: /james/reparaciones/cambiar-termostato.html
✅ Archivo real: /james/reparaciones/reemplazar-termostato.html
```

### Impacto

- **Total de enlaces rotos estimados**: ~250-300
  - 42 marcas × ~6 referencias por marca = 252+
  - Páginas de modelos también afectadas

### Solución Requerida

Opción 1: Renombrar archivos `reemplazar-termostato.html` → `cambiar-termostato.html`
Opción 2: Actualizar enlaces `cambiar-termostato.html` → `reemplazar-termostato.html`

**Recomendación**: Opción 2 (actualizar enlaces) porque "reemplazar" es más técnicamente preciso.
