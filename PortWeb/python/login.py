from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import bcrypt
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)

conn = pymysql.connect(host='127.0.0.1', user='root', password='root', database='reconocimiento_facial')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    numero_trabajador = data.get('numero_trabajador')
    password = data.get('password')
    imagen_base64 = data.get('imagen_facial')

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, password, encoding FROM usuarios WHERE numero_trabajador = %s", (numero_trabajador,))
        user = cursor.fetchone()
        if user:
            nombre_usuario, password_hash, user_encoding = user

            # Verifica la contraseña
            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                # Llamada a la función de reconocimiento facial
                if validate_face(imagen_base64, user_encoding):
                    return jsonify({"status": "success", "message": f"Inicio de sesión exitoso, bienvenido {nombre_usuario}"})
                else:
                    return jsonify({"status": "error", "message": "Reconocimiento facial no coincide"})
            else:
                return jsonify({"status": "error", "message": "Contraseña incorrecta"})
        else:
            return jsonify({"status": "error", "message": "Número de trabajador no encontrado"})
    except Exception as e:
        print(f"Error en el servidor: {e}")
        return jsonify({"status": "error", "message": "Error en el servidor"})


def validate_face(imagen_base64, user_encoding):
    try:
        # Decodifica la imagen
        im_bytes = base64.b64decode(imagen_base64)   
        im_file = BytesIO(im_bytes)  
        img = Image.open(im_file)

        # Convertir la imagen a RGB 
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)

        # Cargar el encoding del rostro
        known_encoding = np.frombuffer(user_encoding, dtype=np.float64)

        # Obtener el encoding del rostro en la imagen recibida
        face_encodings = face_recognition.face_encodings(img_array)
        if face_encodings:
            # Compara los encodings
            matches = face_recognition.compare_faces([known_encoding], face_encodings[0])
            return matches[0]
        return False
    except Exception as e:
        print(f"Error en la validación facial: {e}")
        return False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
