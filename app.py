import json
import random
import pickle
import numpy as np

from flask import Flask, request, jsonify   # Framework que crea server web (API REST)
from flask_cors import CORS
from tensorflow.keras.models import load_model   # Permite cargar archivo .h5


# Constantes de configuración
UMBRAL_CONFIANZA = 0.60
CORREO_INSTITUCIONAL = "secretariaet36@gmail.com"

STOPWORDS ={  # Coincide con la lista de train.py para asegurar consistencia
    'a', 'al', 'como', 'con', 'cual', 'cuales', 'de', 'del', 'donde', 'el', 'ella',
    'en', 'es', 'esta', 'este', 'esto', 'la', 'las', 'lo', 'los', 'me', 'mi', 'mis',
    'no', 'nuestra', 'nuestro', 'o', 'para', 'pero', 'por', 'porque', 'que', 'quien',
    'se', 'si', 'sin', 'sobre', 'su', 'sus', 'tengo', 'tiene', 'tu', 'un', 'una',
    'unos', 'unas', 'y', 'ya', 'yo'
}


app = Flask(__name__)
CORS(app)  # Permite que cualquier dominio consuma la API sin bloqueos del navegador

# 1. Cargamos lo que entrenó train.py
try:
    with open('intents.json', 'r', encoding='utf-8') as f:
        intents = json.load(f)
    
    words = pickle.load(open('words.pkl', 'rb'))
    classes = pickle.load(open('classes.pkl', 'rb'))
    model = load_model('chatbot_model.h5')

except FileNotFoundError:
    raise SystemExit(
        "No se encontraron los archivos del modelo."
        "Ejecutá primero 'python train.py' para generarlos"
    )

# 2. Preprocesamiento de la pregunta igual que en train.py
def limpiar_texto(texto):
    palabras = [w.lower().strip('?.¡!¿,;') for w in texto.split()]
    return [w for w in palabras if w not in STOPWORDS and w != '']

def bag_of_words(texto):   # Crea un vector con 1 en las palabras que aparecen en la pregunta.
    palabras_usuario = limpiar_texto(texto)
    bag = [0] * len(words)

    for palabra in palabras_usuario:
        for i, w in enumerate(words):
            if w == palabra:
                bag[i] = 1

    return np.array(bag)

# 3. Predecimos intención con el umbral de confianza
def predecir_intencion(texto):
    bow = bag_of_words(texto)

    if bow.sum() == 0:  # Si no hay palabras conocidas → fallback con confianza 0
        return "fallback", 0.0

    resultado = model.predict(np.array([bow]), verbose=0)[0]   # Obtiene las probabilidades para cada tag

    indice_max = int(np.argmax(resultado))  # Obtiene el índice de la probabilidad más alta
    confianza = float(resultado[indice_max])   # Busca el tag correspondiente al índice
    tag_predicho = classes[indice_max]   # Devuelve el tag y su confianza

    return tag_predicho, confianza

def obtener_respuesta(tag):   # Busca el tag en intents y elige una respuesta al azar
    for intent in intents['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    return None

# 4. Creamos endpoint /chat (POST, JSON)
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)  # Si el JSON es inválido devuelve None

    if not data or 'message' not in data or not str(data['message']).strip():
        return jsonify({
            "error": "El cuerpo de la petición debe ser un JSON con un campo 'message' no vacío"
        }), 400

    mensaje_usuario = str(data['message'])

    try:
        tag, confianza = predecir_intencion(mensaje_usuario)
    except Exception as e:   
        app.logger.error(f"Error al predecir la intención: {e}")

        return jsonify({    # Evitamos que el server se caiga por una entrada inesperada
            "respuesta": "Tuvimos un problema procesando tu consulta"
                          f"Escribinos a {CORREO_INSTITUCIONAL}",
            "intencion": "error_interno",
            "confianza": 0.0
        }), 200

    if confianza < UMBRAL_CONFIANZA:
        return jsonify({
            "respuesta": (
                "No estoy seguro de haber entendido tu consulta."
                f"Te recomiendo escribir a {CORREO_INSTITUCIONAL} o"
                "a preceptoría para que te ayuden personalmente"
            ),
            "intencion": "fallback",
            "confianza": round(confianza, 2)
        }), 200

    respuesta = obtener_respuesta(tag)
    return jsonify({
        "respuesta": respuesta,
        "intencion": tag,
        "confianza": round(confianza, 2)
    }), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "ok", "mensaje": "API del Chatbot Escolar activa. Usa POST /chat"})


if __name__ == '__main__':   # Arrancamos el servidor
    app.run(host='0.0.0.0', port=5000, debug=False)