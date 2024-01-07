import os
from kivy.uix.image import Image
import face_recognition
import pymysql
import numpy as np
import bcrypt
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.lang import Builder
import subprocess


Builder.load_string("""
<CustomButton>:
    background_normal: 'atlas://data/images/defaulttheme/button'  # Imagen transparente para el fondo normal
    background_down: 'atlas://data/images/defaulttheme/button_pressed'  # Imagen transparente para el fondo presionado
    color: 1, 1, 1, 1  # Texto blanco
    font_size: '20sp'
    size_hint_y: None
    height: '40dp'
    # Dibuja el fondo gris y el borde verde oscuro redondeado
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1  # Color del borde verde oscuro
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
        Color:
            rgba: 0.1, 0.1, 0.1, 1  # Color de fondo gris oscuro
        RoundedRectangle:
            pos: self.pos[0] + 1, self.pos[1] + 1  # Desplaza ligeramente para el efecto de borde
            size: self.size[0] - 2, self.size[1] - 2
            radius: [9,]  # Radio ligeramente menor para mantener el efecto de borde

<CustomTextInput>:
    background_color: 0.1, 0.1, 0.1, 1  # Gris muy oscuro
    foreground_color: 1, 1, 1, 1  # Texto blanco
    size_hint_y: None
    height: '40dp'
              
""")

# Conexión a la base de datos MySQL
conn = pymysql.connect(host='127.0.0.1', user='root', password='root', database='reconocimiento_facial')

def iniciar_sesion(ruta_imagen_login, password):
    imagen_login = face_recognition.load_image_file(ruta_imagen_login)
    encodings_login = face_recognition.face_encodings(imagen_login)

    if len(encodings_login) > 0:
        encoding_login = encodings_login[0]

        cursor = conn.cursor()
        cursor.execute("SELECT nombre, encoding, password FROM usuarios")
        usuarios = cursor.fetchall()

        for nombre, encoding_db, password_hash in usuarios:
            encoding_db = np.frombuffer(encoding_db, dtype=np.float64)
            rostro_coincide = face_recognition.compare_faces([encoding_db], encoding_login)[0]
            password_coincide = bcrypt.checkpw(password.encode(), password_hash)

            if rostro_coincide and password_coincide:
                return nombre, True
            elif rostro_coincide:
                return nombre, False
        return "Usuario no encontrado", None
    else:
        return "No se pudo encontrar ningún rostro en la imagen.", None

def create_images_folder():
    if not os.path.exists('images'):
        os.makedirs('images')

class CustomButton(Button):
    pass

class CustomTextInput(TextInput):
    pass

class LoadingScreen(Popup):
    def __init__(self, usuario, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (400, 200)
        self.auto_dismiss = False
        self.title = 'Bienvenido'

    
        content = BoxLayout(orientation='vertical')
        content.add_widget(Image(source='D:\Reconocimiento Facial-Aerosecure/images/Logo.png'))
        content.add_widget(Label(text=f"Bienvenido {usuario}"))

        self.content = content
        self.open()

        # Programa el cierre de la ventana emergente y la apertura del otro programa
        Clock.schedule_once(self.start_other_program, 7)

    def start_other_program(self, dt):
        self.dismiss()
        # Lanza el otro programa
        subprocess.Popen(['python', 'D:\Reconocimiento Facial-Aerosecure/reconocimiento.py'], shell=True)
        # Cierra la aplicación actual
        App.get_running_app().stop()


class FacialRecognitionLoginApp(App):
    def build(self):
        # Ajustar el tamaño de la ventana al tamaño de la cámara
        camera_size = (640, 480)
        Window.size = (camera_size[0], camera_size[1] + 150)  

        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Configurar cámara
        self.camera = Camera(play=True, resolution=camera_size)
        layout.add_widget(self.camera)

        # Inputs y botones (tamaño por defecto)
        self.name_input = CustomTextInput(hint_text='Ingrese su nombre', size_hint_y=None, height=40)
        self.password_input = CustomTextInput(hint_text='Ingrese su contraseña', password=True, size_hint_y=None, height=40)
        login_button = CustomButton(text='Iniciar Sesión', size_hint_y=None, height=40)
        self.status_label = Label(text='', size_hint_y=None, height=30)

        # Agregar widgets al layout principal
        layout.add_widget(self.name_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_button)
        layout.add_widget(self.status_label)

        # Vincular evento del botón
        login_button.bind(on_press=self.on_login_pressed)

        return layout

    def on_login_pressed(self, instance):
        self.camera.export_to_png("images/captura.jpg")
        Clock.schedule_once(self.login_user_thread, 0.1)

    def login_user_thread(self, dt):
        nombre_usuario, login_exitoso = iniciar_sesion("images/captura.jpg", self.password_input.text)
        if login_exitoso:
            self.status_label.text = f'Bienvenido {nombre_usuario}.'
            # Mostrar la pantalla de carga y luego ejecutar el otro programa
            LoadingScreen(nombre_usuario)
        elif login_exitoso is False:
            self.status_label.text = f'Rostro reconocido, pero contraseña incorrecta para {nombre_usuario}.'
        else:
            self.status_label.text = nombre_usuario

if __name__ == '__main__':
    create_images_folder()
    FacialRecognitionLoginApp().run()
