# Chatbot Escolar con IA -- TP03

Asistente virtual que responde dudas sobre trámites administrativos y académicos (pasantías, talleres, mesas de examen y documentación), usando una red neuronal (MLP) entrenada sobre una base de intenciones, expuesta como API REST en Flask

## Estructura del proyecto

```
chatbot_tp/
├── intents.json      # Base de conocimiento (intenciones, patrones y respuestas)
├── train.py          # Entrena la red neuronal y genera el modelo
├── app.py            # Backend Flask: expone POST /chat
├── index.html        # Interfaz de chat (frontend)
├── requirements.txt  # Dependencias del proyecto
└── README.md
```

Al ejecutar `train.py` se generan además: `chatbot_model.h5`, `words.pkl` y `classes.pkl` (no se versionan en Git; agregalos a `.gitignore`).

## 1. Crear entorno virtual

```bash
python -m venv venv
 
# Activar en Windows
venv\Scripts\activate
 
# Activar en Linux / Mac
source venv/bin/activate
```

## 2. Instalar dependencias
 
```bash
pip install -r requirements.txt
```
 
## 3. Entrenar el modelo
 
```bash
python train.py
```

Esto lee `intents.json`, entrena la red y guarda `chatbot_model.h5`, `words.pkl` y `classes.pkl`.
Volvé a correr este paso cada vez que modifiques `intents.json`.

## 4. Levantar el servidor (API REST)
 
```bash
python app.py
```
 
El servidor queda escuchando en `http://127.0.0.1:5000`.

### Probar el endpoint con curl
 
```bash
curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "necesito el certificado regular"}'
```
 
Respuesta esperada:
 
```json
{
  "respuesta": "La constancia de alumno regular y los analíticos se solicitan en Secretaría...",
  "intencion": "documentacion",
  "confianza": 0.87
}
```

## 5. Abrir la interfaz web
 
Abrí `index.html` directamente en el navegador (con el servidor de `app.py` corriendo en paralelo). Si vas a servirlo con otro puerto o dominio, actualizá la constante `API_URL` dentro del `<script>` de `index.html`.

