import os
import face_recognition
import pymysql
import bcrypt
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder


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

def registrar_usuario(nombre_usuario, ruta_imagen, password, numero_trabajador):
    imagen = face_recognition.load_image_file(ruta_imagen)
    encodings = face_recognition.face_encodings(imagen)

    if len(encodings) > 0:
        encoding = encodings[0]
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, encoding, password, numero_trabajador) VALUES (%s, %s, %s, %s)", 
                       (nombre_usuario, encoding.tobytes(), password_hash, numero_trabajador))
        conn.commit()
        return True
    else:
        print("No se pudo encontrar ningún rostro en la imagen.")
        return False

def create_images_folder():
    if not os.path.exists('images'):
        os.makedirs('images')

class CustomButton(Button):
    pass

class CustomTextInput(TextInput):
    pass

class FacialRecognitionRegisterApp(App):
    def build(self):
        # Ajustar el tamaño de la ventana al tamaño de la cámara
        camera_size = (640, 480)
        Window.size = (camera_size[0], camera_size[1] + 150)  

        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Configurar cámara
        self.camera = Camera(play=True, resolution=camera_size)
        layout.add_widget(self.camera)

        # Inputs y botones 
        self.name_input = CustomTextInput(hint_text='Ingrese su nombre', size_hint_y=None, height=40)
        self.worker_number_input = CustomTextInput(hint_text='Ingrese su número de trabajador', size_hint_y=None, height=40)
        self.password_input = CustomTextInput(hint_text='Ingrese su contraseña', password=True, size_hint_y=None, height=40)
        register_button = CustomButton(text='Registrar Usuario', size_hint_y=None, height=40)
        self.status_label = Label(text='', size_hint_y=None, height=30)

        # Agregar widgets al layout principal
        layout.add_widget(self.name_input)
        layout.add_widget(self.worker_number_input)
        layout.add_widget(self.password_input)
        layout.add_widget(register_button)
        layout.add_widget(self.status_label)

        # Vincular evento del botón
        register_button.bind(on_press=self.on_register_pressed)

        return layout

    def on_register_pressed(self, instance):
        self.camera.export_to_png("images/captura.jpg")
        Clock.schedule_once(self.register_user_thread, 0.1)

    def register_user_thread(self, *args):
        user_name = self.name_input.text
        password = self.password_input.text
        worker_number = self.worker_number_input.text
        if user_name and worker_number:
            resultado = registrar_usuario(user_name, "images/captura.jpg", password, worker_number)
            if resultado:
                self.status_label.text = f'Usuario {user_name} registrado con éxito.'
            else:
                self.status_label.text = 'Error en el registro. Intente de nuevo.'
        else:
            self.status_label.text = 'Nombre y número de trabajador requeridos.'

if __name__ == '__main__':
    create_images_folder()
    FacialRecognitionRegisterApp().run()