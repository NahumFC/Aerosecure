document.addEventListener("DOMContentLoaded", function(event) {
    // Acceder a la cámara y mostrarla en el elemento 'video'
    var video = document.getElementById('video');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (err) {
            console.log("An error occurred: " + err);
        });

    var loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Captura la imagen 
        var canvas = document.getElementById('canvas');
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        var imageDataURL = canvas.toDataURL('image/png');

        var numeroTrabajador = document.getElementById('numero_trabajador').value;
        var password = document.getElementById('password').value;

        // Envia los datos al servidor
        fetch('http://localhost:5000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                numero_trabajador: numeroTrabajador,
                password: password,
                imagen_facial: imageDataURL.split(',')[1] // Envia solo los datos de la imagen
            })
        }).then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("Bienvenido: " + data.message);
                setTimeout(function() {
                    window.location.href = '../html/recognition.html'; // Redirecciona después de 3 segundos
                }, 3000);
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch(error => {
            console.error(error);
            alert("Error en la comunicación con el servidor.");
        });
    });
});
