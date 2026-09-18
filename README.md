# Chatbot Escolar con IA — TP03

Asistente virtual que responde dudas sobre trámites administrativos y académicos (pasantías, talleres, mesas de examen documentación, horarios y wifi), usando una red neuronal (MLP) entrenada sobre una base de intenciones, expuesta como API REST
en Flask.

## Estructura del proyecto

```
chatbot-escolar-IA/
├── intents.json         # Base de conocimiento (intenciones, patrones y respuestas)
├── train.py             # Entrena la red neuronal y genera el modelo
├── app.py               # Backend Flask: expone POST /chat
├── requirements.txt     # Dependencias del proyecto
├── teoria.txt           # Notas teóricas del TP
├── front/
│   ├── index.html       # Estructura del chat
│   ├── style.css        # Estilos visuales
│   └── script.js        # Lógica: conecta el chat con la API
└── README.md
```

Al ejecutar `train.py` se generan además `chatbot_model.h5`, `words.pkl` y `classes.pkl` en la raíz del proyecto. No se versionan en Git (ya están en `.gitignore`) porque son reproducibles: cualquiera los recrea corriendo `train.py`.

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

Lee `intents.json`, entrena la red y guarda `chatbot_model.h5`, `words.pkl` y `classes.pkl` en la raíz del proyecto. **Volvé a correr este paso cada vez que modifiques `intents.json`** (si no, el servidor sigue usando el vocabulario y las respuestas viejas).

## 4. Levantar el servidor (API REST)

```bash
python app.py
```

El servidor queda escuchando en `http://127.0.0.1:5000`. Dejá esta termina abierta mientras uses el chat.

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

Si la pregunta no coincide con ningún trámite conocido, el bot devuelve un
mensaje de fallback en vez de arriesgar una respuesta incorrecta:

```json
{
  "respuesta": "No entendí tu consulta. ¿Podés reformularla o intentarlo de nuevo?",
  "intencion": "fallback",
  "confianza": 0.0
}
```

## 5. Abrir la interfaz de chat

Con el servidor de `app.py` corriendo, abrí `front/index.html` en el navegador. Si `fetch` te tira un error de CORS al abrirlo con doble clic, serví la carpeta `front/` con un mini servidor local en vez de abrir el archivo directo:

```bash
cd front
python -m http.server 5500
```

Y accedé desde `http://127.0.0.1:5500`.

Si tu backend corre en otro puerto o dominio, actualizá la constante `API_URL` al principio de `front/script.js`.

## Cómo funciona (resumen técnico)

1. **Preprocesamiento (Bag of Words):** cada pregunta se tokeniza por espacios, se pasa a minúsculas, se sacan signos de puntuación y *stopwords* (palabras sin significado como "de", "la", "el"), y se convierte en un vector binario según qué palabras del vocabulario aprendido aparecen en ella.
2. **Red neuronal (MLP):** una red secuencial Dense(128) → Dropout → Dense(64) → Dropout → Dense(softmax) clasifica ese vector en una de las intenciones (`tag`).
3. **Umbral de confianza (fallback):** si ninguna palabra de la pregunta está en el vocabulario conocido, o si la probabilidad máxima que devuelve la red es menor a 0.60, el backend no arriesga una respuesta: devuelve el mensaje genérico de fallback.
4. **API REST:** `POST /chat` recibe `{"message": "..."}` y devuelve `{"respuesta": "...", "intencion": "...", "confianza": 0.xx}`.
5. **Frontend:** `script.js` manda la pregunta por `fetch` al backend y pinta la respuesta en el chat, distinguiendo visualmente los mensajes de fallback (fondo amarillo) de las respuestas normales.

## Errores ya corregidos durante el desarrollo (por si vuelven a aparecer)

- **Botón "Enviar" no hacía nada:** el `onclick` en `index.html` llamaba a `enviarmensaje()` (minúscula) pero la función en `script.js` se llama `enviarMensaje()`. JavaScript distingue mayúsculas de minúsculas.
- **Los mensajes de fallback no se mostraban:** en `script.js`, `classList.add('message', tipo)` falla cuando `tipo` tiene más de una clase separada por espacio (ej. `'bot-message fallback'`), porque `classList.add` espera una clase por argumento. Se reemplazó por `div.className = ...`, que sí acepta varias clases en un solo string.

## Posibles mejoras (para ir más allá del mínimo)

- Reemplazar la tokenización manual por `nltk` o `spaCy` con stemming/lematización, para tolerar mejor errores ortográficos y variantes morfológicas.
- Guardar logs de preguntas que caen en fallback, para detectar temas faltantes en `intents.json`.
- Agregar tests automáticos (`pytest`) que verifiquen que cada `pattern` de `intents.json` predice su propio `tag`.