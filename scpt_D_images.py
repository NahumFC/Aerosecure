import os
import face_recognition
import pymysql

# Conexión a la base de datos MySQL
conn = pymysql.connect(host='127.0.0.1', user='root', password='root', database='reconocimiento_facial')

def guardar_en_bd(datos_usuario, encoding):
    cursor = conn.cursor()
    # Asegúrate de actualizar el SQL según los cambios en la estructura de la base de datos
    sql = "INSERT INTO delincuentes (nombre, apellido, nacionalidad, cargos, encoding) VALUES (%s, %s, %s, %s, %s)"
    parametros = datos_usuario + [encoding.tobytes()]
    cursor.execute(sql, parametros)
    conn.commit()

def leer_datos_txt(ruta_archivo_txt):
    with open(ruta_archivo_txt, 'r', encoding='utf-8') as file:
        contenido = file.readlines()
        datos = [line.strip() for line in contenido if line.strip()]  # Elimina líneas vacías y espacios en blanco
        if len(datos) >= 3:  # Verifica que al menos estén presentes los primeros 3 datos esperados
            cargos = '; '.join(datos[3:]) if len(datos) > 3 else ''
            return datos[:3] + [cargos]  # Retorna los primeros 3 datos más la cadena de cargos
        else:
            return None

def procesar_imagenes(carpeta):
    for archivo in os.listdir(carpeta):
        nombre_base, extension = os.path.splitext(archivo)
        if extension in ['.jpg', '.png']:
            ruta_imagen = os.path.join(carpeta, archivo)
            ruta_txt = os.path.join(carpeta, f"{nombre_base}.txt")
            
            if os.path.isfile(ruta_txt):
                datos_usuario = leer_datos_txt(ruta_txt)
                if datos_usuario:
                    imagen = face_recognition.load_image_file(ruta_imagen)
                    encodings = face_recognition.face_encodings(imagen)
                    
                    if encodings:
                        guardar_en_bd(datos_usuario, encodings[0])
                    else:
                        print(f"No se encontraron encodings para {ruta_imagen}")
                else:
                    print(f"No se pudieron extraer datos válidos de {ruta_txt}")
            else:
                print(f"No se encontró el archivo de texto correspondiente para {nombre_base}")

if __name__ == '__main__':
    ruta_carpeta = 'D:\Reconocimiento Facial-Aerosecure/images_INTERPOL'
    procesar_imagenes(ruta_carpeta)
