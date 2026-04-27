# 🏐 Handball Goal Counter

Sistema simple de detección de goles desde videos de YouTube usando YOLOv8.

## 🚀 Deploy en Render - Pasos exactos

### 1️⃣ Crear repositorio NUEVO en GitHub

1. Ve a https://github.com/new
2. **Repository name**: `handball-counter` (o el nombre que quieras)
3. **Public** o **Private** 
4. **NO** inicializar con README
5. Click en **"Create repository"**

### 2️⃣ Subir archivos al nuevo repo

En tu nuevo repo vacío:

1. Click en **"uploading an existing file"**
2. Descomprime `handball-app.zip` en tu PC
3. **IMPORTANTE**: Selecciona TODOS estos archivos:
   - `app.py`
   - `requirements.txt`
   - `runtime.txt`
   - `.gitignore`
   - `README.md`
   - Carpeta `templates/` (con `index.html` dentro)
4. Arrástralos a GitHub
5. En **"Commit changes"** escribe: `Initial commit`
6. Click en **"Commit changes"**

### 3️⃣ Crear servicio NUEVO en Render

1. Ve a https://dashboard.render.com
2. Click en **"+ New"** → **"Web Service"**
3. Selecciona tu repo `handball-counter`
4. Configura **EXACTAMENTE ASÍ**:

| Campo | Valor |
|-------|-------|
| **Name** | `handball-counter` |
| **Region** | Oregon (USA) |
| **Branch** | `main` |
| **Root Directory** | (VACÍO) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --timeout 600 --workers 1` |
| **Plan** | Free |

⚠️ **IMPORTANTE**:
- **Root Directory VACÍO** (no escribas nada)
- **Runtime: Python 3** (NO Node.js)
- **Build Command: `pip install -r requirements.txt`** (SIN build.sh)

### 4️⃣ Click "Create Web Service"

Render hará automáticamente:
1. Clonar tu repo
2. Instalar dependencias de `requirements.txt`
3. Descargar el modelo YOLOv8 (cuando se inicie la app)
4. Iniciar el servidor

⏰ Tarda ~5-8 minutos.

### 5️⃣ Verificar que funciona

Cuando termine, abre:
```
https://handball-counter.onrender.com/api/check
```

Debería mostrar:
```json
{
  "checks": {
    "opencv": { "installed": true },
    "numpy": { "installed": true },
    "yt_dlp": { "installed": true },
    "ultralytics": { "installed": true },
    "model": { "exists": true }
  }
}
```

## 📋 Estructura

```
handball-app/
├── app.py              # Aplicación Flask completa
├── requirements.txt    # Dependencias
├── runtime.txt         # Python 3.11.7
├── .gitignore
├── README.md
└── templates/
    └── index.html
```

## 🔧 Endpoints

- `GET /` - UI principal
- `GET /health` - Health check
- `GET /api/check` - Verificar dependencias
- `POST /api/analyze` - Analizar video
  ```json
  { "url": "https://www.youtube.com/watch?v=..." }
  ```

## ⏰ Primera vez

El modelo YOLOv8 (~6MB) se descarga automáticamente cuando haces el primer análisis. Tarda ~1-2 minutos la primera vez.
