"""
Handball Goal Counter
Aplicación Flask para detectar goles desde videos de YouTube
"""

import os
import sys
import json
import tempfile
import shutil
import logging
import traceback
from flask import Flask, render_template, request, jsonify

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
log = logging.getLogger(__name__)

app = Flask(__name__)


# ==================== RUTAS ====================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check para Render"""
    return jsonify({"status": "ok"})


@app.route('/api/check')
def check_dependencies():
    """Verificar que todas las dependencias funcionen"""
    result = {
        "python_version": sys.version,
        "checks": {}
    }
    
    # Check OpenCV
    try:
        import cv2
        result["checks"]["opencv"] = {
            "installed": True,
            "version": cv2.__version__
        }
    except ImportError as e:
        result["checks"]["opencv"] = {"installed": False, "error": str(e)}
    
    # Check NumPy
    try:
        import numpy as np
        result["checks"]["numpy"] = {
            "installed": True,
            "version": np.__version__
        }
    except ImportError as e:
        result["checks"]["numpy"] = {"installed": False, "error": str(e)}
    
    # Check yt-dlp
    try:
        import yt_dlp
        result["checks"]["yt_dlp"] = {
            "installed": True,
            "version": yt_dlp.version.__version__
        }
    except ImportError as e:
        result["checks"]["yt_dlp"] = {"installed": False, "error": str(e)}
    
    # Check Ultralytics (YOLOv8)
    try:
        from ultralytics import YOLO
        result["checks"]["ultralytics"] = {"installed": True}
    except ImportError as e:
        result["checks"]["ultralytics"] = {"installed": False, "error": str(e)}
    
    # Check modelo
    model_path = "yolov8n.pt"
    result["checks"]["model"] = {
        "exists": os.path.exists(model_path),
        "path": os.path.abspath(model_path) if os.path.exists(model_path) else None
    }
    
    return jsonify(result)


@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    """Endpoint principal: analizar video de YouTube"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"success": False, "error": "Falta el parámetro 'url'"}), 400
        
        youtube_url = data['url'].strip()
        log.info(f"📥 Solicitud recibida: {youtube_url}")
        
        # Validar URL
        if not ('youtube.com' in youtube_url or 'youtu.be' in youtube_url):
            return jsonify({"success": False, "error": "URL de YouTube inválida"}), 400
        
        # Procesar video
        result = process_video(youtube_url)
        
        return jsonify({"success": True, "data": result})
    
    except Exception as e:
        log.error(f"❌ Error: {e}")
        log.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }), 500


# ==================== LÓGICA DE PROCESAMIENTO ====================

def process_video(youtube_url):
    """Descarga y procesa un video de YouTube"""
    import time
    start_time = time.time()
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp(prefix="handball_")
    log.info(f"📁 Directorio temporal: {temp_dir}")
    
    try:
        # 1. Descargar video
        log.info("📥 Descargando video...")
        video_path = download_video(youtube_url, temp_dir)
        
        if not video_path:
            raise Exception("No se pudo descargar el video")
        
        log.info(f"✅ Video descargado: {video_path}")
        
        # 2. Procesar video
        log.info("🎬 Analizando frames...")
        goals_data = analyze_frames(video_path)
        
        elapsed = time.time() - start_time
        
        return {
            "url": youtube_url,
            "goals_detected": len(goals_data["goals"]),
            "goal_timestamps": [g["timestamp"] for g in goals_data["goals"]],
            "team_scores": goals_data["team_scores"],
            "total_frames": goals_data["total_frames"],
            "processed_frames": goals_data["processed_frames"],
            "processing_time": round(elapsed, 2),
            "video_duration": goals_data["duration"]
        }
    
    finally:
        # Limpiar archivos temporales
        try:
            shutil.rmtree(temp_dir)
            log.info("🧹 Limpieza completada")
        except Exception as e:
            log.warning(f"⚠️ Error en limpieza: {e}")


def download_video(url, output_dir):
    """Descarga video usando yt-dlp"""
    import yt_dlp
    
    output_template = os.path.join(output_dir, "video.%(ext)s")
    
    options = {
        'format': 'worst[ext=mp4]/worst',
        'outtmpl': output_template,
        'noplaylist': True,
        'max_filesize': 100 * 1024 * 1024,  # 100MB
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
    }
    
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)
        duration = info.get('duration', 0)
        
        if duration > 600:  # Máximo 10 minutos
            raise Exception(f"Video muy largo: {duration}s. Máximo 600s.")
        
        ydl.download([url])
    
    # Buscar archivo descargado
    for f in os.listdir(output_dir):
        if f.startswith("video."):
            return os.path.join(output_dir, f)
    
    return None


def analyze_frames(video_path):
    """Analiza frames del video con YOLOv8"""
    import cv2
    from ultralytics import YOLO
    
    # Cargar modelo
    log.info("🤖 Cargando YOLOv8...")
    model = YOLO("yolov8n.pt")
    
    # Abrir video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("No se pudo abrir el video")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    log.info(f"📹 Video: {total_frames} frames, {fps} fps, {duration:.1f}s")
    
    # Configuración
    FRAME_SKIP = 10  # Procesar 1 de cada 10 frames
    BALL_CLASS = 32  # sports_ball en COCO
    PERSON_CLASS = 0  # person en COCO
    CONFIDENCE = 0.4
    
    # Zonas de portería (ajustables)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    left_goal = (0, height * 0.3, width * 0.15, height * 0.7)  # x1, y1, x2, y2
    right_goal = (width * 0.85, height * 0.3, width, height * 0.7)
    
    goals = []
    last_goal_frame = -100  # Cooldown
    frame_count = 0
    processed = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Skip frames
        if frame_count % FRAME_SKIP != 0:
            frame_count += 1
            continue
        
        # Detectar objetos
        results = model(frame, verbose=False, conf=CONFIDENCE)[0]
        
        # Buscar pelota
        ball_position = None
        for box in results.boxes:
            class_id = int(box.cls[0])
            if class_id == BALL_CLASS:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                ball_position = ((x1 + x2) / 2, (y1 + y2) / 2)
                break
        
        # Detectar gol (con cooldown)
        if ball_position and (frame_count - last_goal_frame) > 60:
            x, y = ball_position
            timestamp = frame_count / fps
            
            # Pelota en portería izquierda
            if left_goal[0] <= x <= left_goal[2] and left_goal[1] <= y <= left_goal[3]:
                goals.append({
                    "timestamp": round(timestamp, 2),
                    "team": "team_b",
                    "zone": "left_goal"
                })
                last_goal_frame = frame_count
                log.info(f"⚽ GOL detectado en {timestamp:.2f}s (portería izquierda)")
            
            # Pelota en portería derecha
            elif right_goal[0] <= x <= right_goal[2] and right_goal[1] <= y <= right_goal[3]:
                goals.append({
                    "timestamp": round(timestamp, 2),
                    "team": "team_a",
                    "zone": "right_goal"
                })
                last_goal_frame = frame_count
                log.info(f"⚽ GOL detectado en {timestamp:.2f}s (portería derecha)")
        
        processed += 1
        if processed % 30 == 0:
            log.info(f"⏳ Procesados {processed} frames de ~{total_frames // FRAME_SKIP}")
        
        frame_count += 1
    
    cap.release()
    
    # Calcular puntajes
    team_scores = {"team_a": 0, "team_b": 0}
    for goal in goals:
        team_scores[goal["team"]] += 1
    
    return {
        "goals": goals,
        "team_scores": team_scores,
        "total_frames": total_frames,
        "processed_frames": processed,
        "duration": round(duration, 2)
    }


# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    log.info(f"🚀 Servidor iniciando en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
