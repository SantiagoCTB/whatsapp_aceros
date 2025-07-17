Descripción del proyecto: Chatbot de WhatsApp con interfaz Flask
Estoy desarrollando una aplicación web en Flask conectada a la API de WhatsApp Cloud que automatiza la atención al cliente mediante respuestas preconfiguradas y mensajes interactivos como botones y listas desplegables. Este chatbot está orientado a gestionar cotizaciones, preguntas frecuentes y derivar al asesor humano si se requiere.

📦 Estructura modular actual
El proyecto está dividido en carpetas y archivos para mayor claridad y mantenibilidad:

bash
Copiar
Editar
/ (raíz)
│
├── app.py                         # Archivo principal que inicia Flask y registra blueprints
├── config.py                      # Configuración de tokens y constantes del sistema
├── .env                           # Variables de entorno sensibles (token, phone ID, etc.)
│
├── /routes/                       # Blueprints con rutas
│   ├── auth_routes.py             # Login, logout, sesión
│   ├── chat_routes.py             # Vista principal del chat, mensajes, listado de chats
│   ├── configuracion.py           # Gestión de reglas y botones del chatbot
│   └── webhook.py                 # Endpoint que recibe mensajes de WhatsApp y responde
│
├── /services/                     # Lógica de negocio reutilizable
│   ├── db.py                      # Conexión y funciones sobre la base de datos SQLite
│   ├── whatsapp_api.py            # Funciones para enviar mensajes con texto, botones y listas
│   └── utils.py                   # (Reservado para funciones auxiliares si es necesario)
│
├── /templates/                    # Archivos HTML (Jinja2)
│   ├── index.html                 # Vista del chat entre clientes y asesores
│   ├── login.html                 # Formulario de inicio de sesión
│   ├── configuracion.html         # Administración de reglas del chatbot
│   └── botones.html               # Administración de botones predefinidos
│
├── /static/                       # Archivos CSS/JS si los hay
│   └── style.css                  # Estilos generales
│
├── requirements.txt               # Librerías necesarias para correr el proyecto

🔄 Funcionalidades implementadas
Gestión de usuarios y autenticación (admin)

Recepción y procesamiento de mensajes entrantes de WhatsApp vía webhook

Flujo automático basado en reglas configurables (con pasos, respuestas, tipo de mensaje y opciones)

Envío de mensajes por parte del asesor desde la interfaz web

Interfaz tipo WhatsApp Web con:

Lista de clientes

Ventana de chat

Botones personalizables predefinidos

Recarga automática de mensajes

Importación de reglas y botones desde archivos .xlsx

Soporte para mensajes interactivos: texto, botones y listas desplegables

Detección de inactividad para cerrar sesión automática del cliente

🔧 Tecnologías utilizadas
Python 3 y Flask

WhatsApp Cloud API (v17+)

SQLite como base de datos ligera local

HTML + Jinja2 + JavaScript en el frontend

openpyxl para cargar reglas desde archivos Excel

dotenv para manejar tokens y credenciales

✅ Estado actual
La app ya está funcionando con:

Flujo conversacional basado en reglas almacenadas en base de datos

Administración visual de botones y reglas

Sistema de login y logout

División completa en módulos con Blueprints y servicios