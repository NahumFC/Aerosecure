var video = document.getElementById('video');
var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');
var registerForm = document.getElementById('registerForm');

// Solicitar acceso a la cámara
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
        video.srcObject = stream;
        video.play();
    }).catch(function(error) {
        console.log("Error al acceder a la cámara: ", error);
    });
}

registerForm.addEventListener('submit', function(event) {
    event.preventDefault();

    // Captura la foto
    context.drawImage(video, 0, 0, 640, 480);

    // Convertir la imagen del canvas a Blob y luego enviarla
    canvas.toBlob(function(blob) {
        var formData = new FormData(registerForm);
        formData.append('imagen_facial', blob, 'captura.png');

        fetch('http://localhost:5001/register', {
            method: 'POST',
            body: formData
        }).then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                document.getElementById('mensajeExito').textContent = "Se registró " + formData.get('nombre') + " correctamente";
            } else {
                document.getElementById('mensajeExito').textContent = "Error en el registro: " + data.message;
            }
        })
        .catch(error => {
            console.error(error);
            document.getElementById('mensajeExito').textContent = "Error en el registro.";
        });
    }, 'image/png');
});