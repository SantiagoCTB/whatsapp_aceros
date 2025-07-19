import json
from config import Config
from services.db import guardar_mensaje
import requests
import os

TOKEN = Config.META_TOKEN
PHONE_ID = Config.PHONE_NUMBER_ID

def enviar_mensaje(numero, mensaje, tipo='bot', tipo_respuesta='texto', opciones=None):
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    if tipo_respuesta == 'texto':
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": mensaje}
        }

    elif tipo_respuesta == 'lista':
        try:
            secciones = json.loads(opciones) if opciones else []
        except Exception as e:
            print(f"Error en JSON de opciones: {e}")
            secciones = []

        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "Menú"},
                "body": {"text": mensaje},
                "footer": {"text": "Selecciona una opción"},
                "action": {
                    "button": "Ver opciones",
                    "sections": secciones
                }
            }
        }
    elif tipo_respuesta == 'boton':
        try:
            botones = json.loads(opciones) if opciones else []
        except Exception as e:
            print(f"Error en JSON de botones: {e}")
            botones = []

        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": mensaje},
                "action": {
                    "buttons": botones  # debe ser una lista de máx. 3
                }
            }
        }

    else:
        # fallback por si se configura mal
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": mensaje}
        }

    resp = requests.post(url, headers=headers, json=data)
    print(f"[WA API] {resp.status_code} — {resp.text}")

    guardar_mensaje(numero, mensaje, tipo)

def obtener_url_media(media_id):
    token = os.getenv("META_TOKEN")
    url = f"https://graph.facebook.com/v19.0/{media_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json().get("url")
    return None