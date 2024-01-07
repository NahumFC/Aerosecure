import os
import face_recognition
import pymysql
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window

# Conexión a la base de datos MySQL
conn = pymysql.connect(host='127.0.0.1', user='root', password='root', database='reconocimiento_facial')

def iniciar_sesion(ruta_imagen_login):
    imagen_login = face_recognition.load_image_file(ruta_imagen_login)
    encodings_login = face_recognition.face_encodings(imagen_login)

    if len(encodings_login) > 0:
        encoding_login = encodings_login[0]

        cursor = conn.cursor()
        cursor.execute("SELECT nombre, apellido, nacionalidad, cargos, encoding FROM delincuentes")
        usuarios = cursor.fetchall()

        for nombre, apellido, nacionalidad, cargos, encoding_db in usuarios:
            encoding_db = np.frombuffer(encoding_db, dtype=np.float64)
            rostro_coincide = face_recognition.compare_faces([encoding_db], encoding_login)[0]

            if rostro_coincide:
                imagen_usuario = f"D:\Reconocimiento Facial-Aerosecure/images_INTERPOL/{nombre}_{apellido}.jpg"
                if not os.path.exists(imagen_usuario):
                    imagen_usuario = f"D:\Reconocimiento Facial-Aerosecure/images_INTERPOL/{nombre}_{apellido}.png"
                return (nombre, apellido, nacionalidad, cargos), True, imagen_usuario
        return "Usuario no encontrado", False, None
    else:
        return "No se pudo encontrar ningún rostro en la imagen.", False, None

def create_images_folder():
    if not os.path.exists('images'):
        os.makedirs('images')

class FacialRecognitionLoginApp(App):
    def build(self):
        Window.size = (1030, 550)        
        layout = BoxLayout(orientation='horizontal', padding=4)
        # Aumentar el tamaño de la cámara
        camera_container = BoxLayout(orientation='vertical', padding=3, size_hint_x=None, width=640)
        self.camera = Camera(play=True, resolution=(640, 480))
        camera_container.add_widget(self.camera)

        recognize_button = Button(text='Reconocer Rostro', size_hint_y=None, height=50)
        recognize_button.bind(on_press=self.on_recognize_pressed)
        camera_container.add_widget(recognize_button)
        
        layout.add_widget(camera_container)

        # Aumentar el ancho del contenedor de información para ajustar los elementos
        self.info_container = BoxLayout(orientation='vertical', padding=5, spacing=10, size_hint_x=None, width=400)
        self.nombre_label = Label(text='Nombre: ', size_hint_y=None, height=40)
        self.apellido_label = Label(text='Apellido: ', size_hint_y=None, height=40)
        self.nacionalidad_label = Label(text='Nacionalidad: ', size_hint_y=None, height=40)

        self.info_container.add_widget(self.nombre_label)
        self.info_container.add_widget(self.apellido_label)
        self.info_container.add_widget(self.nacionalidad_label)
        
        # Imagen del usuario reconocido, se mantiene a la izquierda de los datos
        self.user_image = Image(size_hint_y=None, height=240, allow_stretch=True)
        self.info_container.add_widget(self.user_image)
        
        layout.add_widget(self.info_container)

        # Aumentar el tamaño de la sección de los cargos
        self.cargos_scroll = ScrollView(size_hint=(1, None), size=(Window.width - 1024, 240), do_scroll_x=False)
        self.cargos_label = Label(size_hint_y=None, height=240, halign='left', valign='top')
        self.cargos_label.bind(size=self.cargos_label.setter('text_size'))  # Ajustar el texto al tamaño del label
        self.cargos_scroll.add_widget(self.cargos_label)
        self.info_container.add_widget(self.cargos_scroll)

        self.panic_button = Button(text='Llamar a la Policía', size_hint_y=None, height=50, opacity=0, disabled=True)
        self.panic_button.bind(on_press=self.on_panic_pressed)
        layout.add_widget(self.panic_button)

        return layout

    def on_recognize_pressed(self, instance):
        self.camera.export_to_png("images/captura.jpg")
        Clock.schedule_once(self.recognize_user_thread, 0.1)

    def recognize_user_thread(self, dt):
        usuario, rostro_encontrado, imagen_usuario = iniciar_sesion("images/captura.jpg")
        if rostro_encontrado:
            nombre, apellido, nacionalidad, cargos = usuario
            self.nombre_label.text = f'Nombre: {nombre}'
            self.apellido_label.text = f'Apellido: {apellido}'
            self.nacionalidad_label.text = f'Nacionalidad: {nacionalidad}'
            cargos_formato = cargos.replace('; ', '\n')
            self.cargos_label.text = f'Cargos:\n{cargos_formato}'
            self.user_image.source = imagen_usuario
            self.panic_button.opacity = 1
            self.panic_button.disabled = False
        else:
            self.nombre_label.text = 'Usuario no encontrado'
            self.apellido_label.text = ''
            self.nacionalidad_label.text = ''
            self.cargos_label.text = ''
            self.user_image.source = 'D:\Reconocimiento Facial-Aerosecure/images/default.png'
            self.panic_button.opacity = 0
            self.panic_button.disabled = True

    def on_panic_pressed(self, instance):
        print("Llamada a la policía activada.")

if __name__ == '__main__':
    create_images_folder()
    FacialRecognitionLoginApp().run()

