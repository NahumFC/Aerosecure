from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import bcrypt
import face_recognition

app = Flask(__name__)
CORS(app)

conn = pymysql.connect(host='127.0.0.1', user='root', password='root', database='reconocimiento_facial')

def registrar_usuario(nombre_usuario, password_hash, numero_trabajador, encoding):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, password, numero_trabajador, encoding) VALUES (%s, %s, %s, %s)", 
                   (nombre_usuario, password_hash, numero_trabajador, encoding))
    conn.commit()

@app.route('/register', methods=['POST'])
def register():
    imagen_facial = request.files.get('imagen_facial')
    if imagen_facial:
        ruta_imagen = 'captura.png'
        imagen_facial.save(ruta_imagen)

        imagen = face_recognition.load_image_file(ruta_imagen)
        encodings = face_recognition.face_encodings(imagen)
        if len(encodings) > 0:
            encoding = encodings[0]
        else:
            return jsonify({"status": "error", "message": "No se pudo encontrar ningún rostro en la imagen."})
    else:
        return jsonify({"status": "error", "message": "No se proporcionó una imagen facial."})

    nombre_usuario = request.form['nombre']
    password = request.form['password']
    numero_trabajador = request.form['numero_trabajador']
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    registrar_usuario(nombre_usuario, password_hash, numero_trabajador, encoding.tobytes())

    return jsonify({"status": "success", "message": "Usuario registrado con éxito"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

