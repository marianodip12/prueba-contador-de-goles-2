# 🏐 Handball Goal Counter

Sistema simple de detección de goles desde videos de YouTube usando YOLOv8.

## 🚀 Deploy en Render - Pasos exactos

### 1️⃣ Crear repositorio NUEVO en GitHub

1. Ve a https://github.com/new
2. **Repository name**: `handball-counter` (o el nombre que quieras)
3. **Public** o **Private** (lo que prefieras)
4. **NO** inicializar con README
5. Click en **"Create repository"**

### 2️⃣ Subir TODOS los archivos del ZIP

En tu nuevo repo vacío:

1. Click en **"uploading an existing file"** (link en la página)
2. Descomprime `handball-app.zip` en tu PC
3. Selecciona TODOS los archivos y arrástralos a GitHub
   - `app.py`
   - `requirements.txt`
   - `runtime.txt`
   - `build.sh`
   - `.gitignore`
   - `README.md`
   - Carpeta `templates/`
4. Commit message: `Initial commit`
5. Click en **"Commit changes"**

### 3️⃣ Crear servicio NUEVO en Render

1. Ve a https://dashboard.render.com
2. Click en **"+ New"** (arriba a la derecha) → **"Web Service"**
3. Conecta tu repositorio recién creado
4. Configura **EXACTAMENTE ASÍ**:

| Campo | Valor |
|-------|-------|
| **Name** | `handball-counter` |
| **Region** | Oregon (USA) |
| **Branch** | `main` |
| **Root Directory** | (DEJAR VACÍO) |
| **Runtime** | `Python 3` |
| **Build Command** | `bash build.sh` |
| **Start Command** | `gunicorn app:app --timeout 600 --workers 1` |
| **Plan** | `Free` |

⚠️ **IMPORTANTE**: 
- **Root Directory debe estar VACÍO** (no `handball-goal-counter` ni nada)
- **Runtime debe ser Python 3**, NO Node.js

### 4️⃣ Click en "Create Web Service"

Render hará:
1. Clonar tu repo
2. Ejecutar `bash build.sh`
3. Instalar todas las dependencias Python
4. Descargar el modelo YOLOv8
5. Iniciar el servidor con gunicorn

**Tarda ~5-8 minutos la primera vez.**

### 5️⃣ Verificar que funciona

Cuando termine el deploy, abre estas URLs:

1. **Página principal**: `https://handball-counter.onrender.com/`
2. **Verificar dependencias**: `https://handball-counter.onrender.com/api/check`

El segundo te dirá si todo está bien instalado.

## 📋 Estructura del Proyecto

```
handball-app/
├── app.py              # Aplicación Flask completa (todo en un archivo)
├── requirements.txt    # Dependencias Python
├── runtime.txt         # Python 3.11.7
├── build.sh           # Script de build (instala todo + descarga YOLOv8)
├── templates/
│   └── index.html     # UI principal
└── README.md
```

**SIMPLE**: Todo el código Python está en `app.py`. Sin carpetas extras, sin Next.js, sin complicaciones.

## 🔧 Endpoints

- `GET /` - Página principal con UI
- `GET /health` - Health check
- `GET /api/check` - Verificar dependencias instaladas
- `POST /api/analyze` - Analizar video
  ```json
  { "url": "https://www.youtube.com/watch?v=..." }
  ```

## ⚠️ Plan Free de Render - Limitaciones

- Solo 512MB de RAM
- Se duerme tras 15 min sin uso
- Tarda ~30-50s en despertar
- Build inicial: ~5-8 minutos

Si tienes problemas de memoria, edita `app.py` y aumenta `FRAME_SKIP` a 20 o 30.
