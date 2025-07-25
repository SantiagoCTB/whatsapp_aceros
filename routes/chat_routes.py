from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify
import sqlite3
from config import Config
from services.whatsapp_api import enviar_mensaje
from services.db import get_connection
import uuid
import os
from werkzeug.utils import secure_filename


chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
def index():
    # Autenticación
    if "user" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    c    = conn.cursor()

    # Lista de chats únicos
    c.execute("SELECT DISTINCT numero FROM mensajes")
    numeros = [row[0] for row in c.fetchall()]

    chats = []
    for numero in numeros:
        # Último mensaje para determinar si requiere asesor
        c.execute(
            "SELECT mensaje FROM mensajes WHERE numero = %s "
            "ORDER BY timestamp DESC LIMIT 1",
            (numero,)
        )
        fila = c.fetchone()
        ultimo = fila[0] if fila else ""
        requiere_asesor = "asesor" in ultimo.lower()

        chats.append((numero, requiere_asesor))

    # Botones configurados
    c.execute("SELECT id, mensaje FROM botones ORDER BY id")
    botones = c.fetchall()  # lista de tuplas (id, mensaje)

    conn.close()
    return render_template('index.html', chats=chats, botones=botones)

@chat_bp.route('/get_chat/<numero>')
def get_chat(numero):
    if "user" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    c    = conn.cursor()
    c.execute("""
      SELECT mensaje, tipo, media_url, timestamp
      FROM mensajes
      WHERE numero = %s
      ORDER BY timestamp
    """, (numero,))
    mensajes = c.fetchall()
    conn.close()
    return jsonify({'mensajes': mensajes})

@chat_bp.route('/send_message', methods=['POST'])
def send_message():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    data   = request.get_json()
    numero = data.get('numero')
    texto  = data.get('mensaje')

    # Envía por la API y guarda internamente
    enviar_mensaje(numero, texto, tipo='asesor')
    return jsonify({'status': 'success'}), 200

@chat_bp.route('/get_chat_list')
def get_chat_list():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    c    = conn.cursor()

    # Únicos números
    c.execute("SELECT DISTINCT numero FROM mensajes")
    numeros = [row[0] for row in c.fetchall()]

    chats = []
    for numero in numeros:
        # Alias
        c.execute("SELECT nombre FROM alias WHERE numero = %s", (numero,))
        fila = c.fetchone()
        alias = fila[0] if fila else None

        # Último mensaje para asesor
        c.execute(
            "SELECT mensaje FROM mensajes WHERE numero = %s "
            "ORDER BY timestamp DESC LIMIT 1",
            (numero,)
        )
        fila = c.fetchone()
        ultimo = fila[0] if fila else ""
        requiere_asesor = "asesor" in ultimo.lower()

        chats.append({
            "numero": numero,
            "alias":  alias,
            "asesor": requiere_asesor
        })

    conn.close()
    return jsonify(chats)

@chat_bp.route('/set_alias', methods=['POST'])
def set_alias():
    if "user" not in session:
        return jsonify({"error": "No autorizado"}), 401

    data   = request.get_json()
    numero = data.get('numero')
    nombre = data.get('nombre')

    conn = get_connection()
    c    = conn.cursor()
    # Inserta o actualiza alias
    c.execute(
        "INSERT INTO alias (numero, nombre) VALUES (%s, %s) "
        "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)",
        (numero, nombre)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"}), 200

@chat_bp.route('/send_image', methods=['POST'])
def send_image():
    print("▶▶▶ [DEBUG] Llegó petición a /send_image")  # log 🎯
    # Validación de sesión
    if 'user' not in session:
        print("↩️ [DEBUG] No autorizado")
        return jsonify({'error':'No autorizado'}), 401

    # Obtener campos
    numero  = request.form.get('numero')
    caption = request.form.get('caption','')
    img     = request.files.get('image')

    print(f"[DEBUG] numero={numero}, caption={caption}, img={img}")  # log 🎯

    if not numero or not img:
        print("[DEBUG] Faltan campos: numero o image")
        return jsonify({'error':'Falta número o imagen'}), 400

    # Guarda archivo en disco
    filename = secure_filename(img.filename)
    unique   = f"{uuid.uuid4().hex}_{filename}"
    upload_folder = Config.UPLOAD_FOLDER  # debe concordar con lo de config.py
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, unique)
    img.save(path)
    print(f"[DEBUG] Imagen guardada en {path}")  # log 🎯

    # URL pública
    image_url = url_for('static', filename=f'uploads/{unique}', _external=True)
    print(f"[DEBUG] image_url = {image_url}")  # log 🎯

    # Envía la imagen por la API
    enviar_mensaje(
        numero,
        caption,
        tipo='bot_image',
        tipo_respuesta='image',
        opciones=image_url
    )
    print("▶▶▶ [DEBUG] enviar_mensaje() invocado")  # log 🎯

    # Ya se guarda internamente dentro de enviar_mensaje()
    return jsonify({'status':'sent_image'}), 200