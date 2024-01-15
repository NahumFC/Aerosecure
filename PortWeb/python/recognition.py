from flask import Flask, request, jsonify
from flask import send_from_directory
from flask_cors import CORS
import pymysql
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)

conn = pymysql.connect(host='127.0.0.1', user='root', password='root', database='reconocimiento_facial')

@app.route('/recognition', methods=['POST'])
def recognition():
    data = request.json
    imagen_base64 = data.get('imagen_facial')

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, apellido, nacionalidad, cargos, encoding FROM delincuentes")
        users = cursor.fetchall()
        for user in users:
            nombre_usuario, apellido_usuario, nacionalidad, cargos, user_encoding = user

            if validate_face(imagen_base64, user_encoding):
                return jsonify({
                    "status": "success", 
                    "message": f"Persona reconocida: {nombre_usuario} {apellido_usuario}",
                    "data": {
                        "nombre": nombre_usuario,
                        "apellido": apellido_usuario,
                        "nacionalidad": nacionalidad,
                        "cargos": cargos
                    }
                })
        
        return jsonify({"status": "error", "message": "Reconocimiento facial no coincide con ningún usuario registrado"})
    except Exception as e:
        print(f"Error en el servidor: {e}")
        return jsonify({"status": "error", "message": "Error en el servidor"})


@app.route('/getDelincuentesInfo', methods=['GET'])
def get_delincuentes_info():
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)  # DictCursor es para obtener los resultados como diccionarios
        cursor.execute("SELECT nombre, apellido, nacionalidad, cargos FROM delincuentes")
        delincuentes = cursor.fetchall()  # Cada fila es un diccionario

        return jsonify(delincuentes)  # Convierte la lista de diccionarios en JSON
    except Exception as e:
        print(f"Error al obtener información de delincuentes: {e}")
        return jsonify({"status": "error", "message": "Error al obtener información"})

@app.route('/images_INTERPOL/<filename>')
def send_image(filename):
    return send_from_directory('D:/Reconocimiento Facial-Aerosecure/images_INTERPOL', filename)


def validate_face(imagen_base64, user_encoding):
    try:
        im_bytes = base64.b64decode(imagen_base64)   
        im_file = BytesIO(im_bytes)  
        img = Image.open(im_file)

        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        known_encoding = np.frombuffer(user_encoding, dtype=np.float64)

        face_encodings = face_recognition.face_encodings(img_array)
        if face_encodings:
            face_distances = face_recognition.face_distance([known_encoding], face_encodings[0])
            best_match_index = np.argmin(face_distances)

            if face_distances[best_match_index] < 0.6:  # Ese es el umbral para la rigurosidad del reconocimiento facial, yo lo dejé ahí pero se puede ajustar 
                return True
        return False
    except Exception as e:
        print(f"Error en la validación facial: {e}")
        return False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
