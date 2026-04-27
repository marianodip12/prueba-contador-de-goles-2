#!/usr/bin/env bash
set -e

echo "============================================"
echo "🚀 BUILD - Handball Goal Counter"
echo "============================================"

echo ""
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

echo ""
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "📥 Descargando modelo YOLOv8..."
if [ ! -f "yolov8n.pt" ]; then
    wget -q https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
    echo "✅ Modelo descargado"
else
    echo "✅ Modelo ya existe"
fi

echo ""
echo "============================================"
echo "✅ BUILD COMPLETADO"
echo "============================================"
