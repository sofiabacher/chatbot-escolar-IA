import json   # Leer archivo intents.json
import random
import numpy as np   # Permite trabajar con vectores y matrices de números
import pickle   # Guarda estructuras de Python (diccionarios, listas) en archivos binarios
import tensorflow as tf   # Framework que arma y entrena la red neuronal

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dropout, Dense
from tensorflow.keras.optimizers import SGD


# 1. Cargamos la base de conocimiento
with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)    # Convertimos archivo a diccionario 

# 2. Tokenización (partir texto en unidades) y armado del vocabulario
words = []   # Vocabulario completo (palabras únicas que aparecen en todos los patterns)
classes = []   # Lista de tags únicos ("categorías")
documents = []   # Lista de pares (palabras, tag) que sirve como "examen resuelto" para entrenar la red
ignore_letters = ['?', '¿', '!', '¡', '.', ',', ';']

STOPWORDS ={  # Palabras vacías que no aportan significado en si y provocan falsos positivos
    'a', 'al', 'como', 'con', 'cual', 'cuales', 'de', 'del', 'donde', 'el', 'ella',
    'en', 'es', 'esta', 'este', 'esto', 'la', 'las', 'lo', 'los', 'me', 'mi', 'mis',
    'no', 'nuestra', 'nuestro', 'o', 'para', 'pero', 'por', 'porque', 'que', 'quien',
    'se', 'si', 'sin', 'sobre', 'su', 'sus', 'tengo', 'tiene', 'tu', 'un', 'una',
    'unos', 'unas', 'y', 'ya', 'yo'
}

for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = [w.lower().strip('?.¡!¿,;') for w in pattern.split()]   # Borra mayusculas, simbolos y hace tokenización
        words.extend(word_list)
        documents.append((word_list, intent['tag']))

        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# Eliminamos duplicados, signos, stopwords --> set() y ordenamos 
words = sorted(list(set([w for w in words if w not in ignore_letters and w not in STOPWORDS and w != ''])))
classes = sorted(list(set(classes)))

print(f"{len(documents)} patrones")
print(f"{len(classes)} clases: {classes}")
print(f"{len(words)} palabras únicas (vocabulario)")

# Guardamos estructuras para usar en el servidor
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# 3. Creamos el set de entrenamiento (Bag of Words --> convertir texto en números)
training = []
output_empty = [0] * len(classes)

for doc in documents:   # Para cada documento armamos dos vectores
    bag = []   # Vector de 1 y 0 que indica qué palabras del vocabulario están en la frase
    pattern_words = doc[0]

    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    output_row = list(output_empty)   # Label en formato one-hot, con 1 en la posición del tag correcto.
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

random.shuffle(training)   # Mezcla los datos para evitar un orden fijo

train_x = np.array([row[0] for row in training])  # Guarda bag --> preguntas
train_y = np.array([row[1] for row in training])  # Guarda output_row --> respuestas correctas

# 4. Armamos la red neuronal (MLP secuencial --> perceptrón multicapa organizado secuencialmente)
model = Sequential()

model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))   # 128 neuronas, entrada = vocabulario (bag), activación ReLU.
model.add(Dropout(0.5))     # Apaga el 50% de las neuronas para evitar el sobreajuste (evita que "memorice")

model.add(Dense(64, activation='relu'))    # 2° capa con 64 neuronas.
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))   # Crea una neurona por tag; softmax devuelve probabilidades que suman 1

sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)  # Ajustamos los pesos de la red según el learning_rate definido

model.compile(
    loss='categorical_crossentropy',  # Función que mide el error de la predicción 
    optimizer=sgd,
    metrics=['accuracy']    # Exactitud
)

# 5. Entrenamos y guardamos el modelo
history = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)   #batch_size: se esperan x ejemplos para ajustar pesos por promedio
model.save('chatbot_model.h5')

print("\nEntrenamiento finalizado")
print("Se generaron: chatbot_model.h5, words.pkl, classes.pkl")