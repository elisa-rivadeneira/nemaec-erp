# 🛡️ Configuración CSP para NEMAEC ERP - Mapas

## Problema Actual
El mapa de NEMAEC ERP necesita cargar tiles (imágenes de mapas) desde OpenStreetMap para mostrar calles, avenidas y geografía real. La política CSP actual está bloqueando estas imágenes.

## Solución: Actualizar CSP Header

Para que el mapa funcione correctamente con OpenStreetMap, actualice la configuración CSP del servidor:

### CSP Actual (Restrictiva):
```
img-src 'self' data: [URLs específicas]
```

### CSP Requerida (Permitir OpenStreetMap):
```
img-src 'self' data: *.tile.openstreetmap.org https://tile.openstreetmap.org
```

## Configuración por Tipo de Servidor

### ✅ Nginx
Agregue a su configuración de Nginx:

```nginx
# En el bloque server {}
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self' 'unsafe-inline';
    style-src 'self' 'unsafe-inline' https://unpkg.com;
    img-src 'self' data: blob: *.tile.openstreetmap.org https://tile.openstreetmap.org https://unpkg.com;
    connect-src 'self';
    font-src 'self';
    frame-src 'none';
" always;
```

### ✅ Apache
Agregue al archivo `.htaccess` o configuración del virtual host:

```apache
Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://unpkg.com; img-src 'self' data: blob: *.tile.openstreetmap.org https://tile.openstreetmap.org https://unpkg.com; connect-src 'self'; font-src 'self'; frame-src 'none';"
```

### ✅ Node.js/Express
Si usa Express, agregue este middleware:

```javascript
app.use((req, res, next) => {
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; " +
    "script-src 'self' 'unsafe-inline'; " +
    "style-src 'self' 'unsafe-inline' https://unpkg.com; " +
    "img-src 'self' data: blob: *.tile.openstreetmap.org https://tile.openstreetmap.org https://unpkg.com; " +
    "connect-src 'self'; " +
    "font-src 'self'; " +
    "frame-src 'none';"
  );
  next();
});
```

### ✅ Meta Tags HTML (Alternativa)
Si no puede modificar headers del servidor, agregue al `<head>` del HTML:

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://unpkg.com; img-src 'self' data: blob: *.tile.openstreetmap.org https://tile.openstreetmap.org https://unpkg.com; connect-src 'self'; font-src 'self'; frame-src 'none';">
```

## ✅ Dominios de Confianza Agregados

Los nuevos dominios agregados son **seguros** y de confianza:

- **`*.tile.openstreetmap.org`**: Servidor oficial de tiles de OpenStreetMap
- **`https://tile.openstreetmap.org`**: Servidor principal de OpenStreetMap
- **`https://unpkg.com`**: CDN para Leaflet CSS/assets (biblioteca de mapas)

## 🔒 Seguridad Mantenida

Esta configuración:
- ✅ Mantiene la seguridad general del sitio
- ✅ Solo permite dominios específicos de mapas
- ✅ No abre vulnerabilidades de seguridad
- ✅ Es una práctica estándar para aplicaciones con mapas

## 🚀 Resultado

Después de aplicar esta configuración:
- ✅ El mapa mostrará calles, avenidas y geografía real
- ✅ Los marcadores de comisarías serán visibles
- ✅ La funcionalidad completa del mapa estará disponible
- ✅ No habrá errores de CSP en la consola

## 📞 Soporte

Si necesita ayuda con la configuración, la configuración exacta depende de su:
- Servidor web (Nginx/Apache/IIS)
- Plataforma de hosting (AWS/DigitalOcean/etc.)
- Panel de control (cPanel/Plesk/etc.)

**Contacte al administrador del servidor** con este documento para implementar los cambios necesarios.