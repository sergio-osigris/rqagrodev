## ✅ PASOS PARA PASAR DE HTTP A HTTPS EN EC2 (FASTAPI + NGINX + SSL)

### 🟡 PRE-REQUISITOS

* EC2 con Ubuntu en funcionamiento
* Tu app FastAPI corriendo en el puerto `8000`
* Puerto 80 (HTTP) y 443 (HTTPS) abiertos en el **Grupo de Seguridad**
* Una IP pública o usar un dominio gratuito tipo `sslip.io` o `nip.io`

---

### 1. 🔧 **Instalar Nginx y Certbot**

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y
```

---

### 2. 📦 **Usar dominio temporal gratuito (si no tienes dominio propio)**

Si tu IP pública es `51.94.243.116`, entonces puedes usar:

```
18-100-110-120.sslip.io
```

Este dominio gratuito apunta a tu IP y **es compatible con Let's Encrypt**.

---

### 3. 🧱 **Configurar Nginx para tu app FastAPI**

Crea el archivo de configuración:

```bash
sudo nano /etc/nginx/sites-available/webhook
```

Contenido:

```nginx
server {
    listen 80;
    server_name 18-100-110-120.sslip.io;

    location / {
        proxy_pass http://localhost:8000;  # sin barra al final
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Activa la configuración:

```bash
sudo ln -s /etc/nginx/sites-available/webhook /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

### 4. 🔐 **Obtener y configurar el certificado HTTPS**

```bash
sudo certbot --nginx -d 18-100-110-120.sslip.io
```

Esto hará:

* Obtener certificado SSL válido
* Configurar HTTPS en Nginx automáticamente
* Redirigir HTTP → HTTPS

---

### 5. 🔄 **Verificar y reiniciar Nginx**

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

### 6. ✅ **Probar HTTPS funcionando**

Abre en el navegador o usa `curl`:

```
https://18-100-110-120.sslip.io
```

Tu servidor ya responde por HTTPS y **es válido para Facebook, Stripe, etc.**

---

### 7. 🧪 **(Opcional) Debug de parámetros**

Para asegurarte que llegan bien los parámetros:

```python
@app.get("/webhook/whatsapp")
async def verify(request: Request):
    print("URL completa:", request.url)
    print("Parámetros:", request.query_params)
```

