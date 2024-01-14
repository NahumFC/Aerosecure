document.addEventListener("DOMContentLoaded", function(event) {
    var video = document.getElementById('video');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (err) {
            console.log("An error occurred: " + err);
        });

    var recognitionForm = document.getElementById('recognitionForm');
    recognitionForm.addEventListener('submit', function(event) {
        event.preventDefault();

        var canvas = document.getElementById('canvas');
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        var imageDataURL = canvas.toDataURL('image/png');

        fetch('http://localhost:5000/recognition', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                imagen_facial: imageDataURL.split(',')[1]
            })
        }).then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("Reconocimiento facial exitoso: " + data.message);
                displayDelincuenteInfo(data.data);
            } else {
                alert("Reconocimiento facial fallido: " + data.message);
            }
        })
        .catch(error => {
            console.error(error);
            alert("Error en la comunicación con el servidor.");
        });
    });

    function displayDelincuenteInfo(delincuente) {
        const infoDiv = document.getElementById('delincuentesInfo');
        infoDiv.style.display = 'block'; 
    
        const cargosConSaltosDeLinea = delincuente.cargos.replace(/;/g, '<br>');
        const nombreArchivo = `${delincuente.nombre}_${delincuente.apellido}.png`;
        const imagePath = `http://localhost:5000/images_INTERPOL/${nombreArchivo}`;
    
        infoDiv.innerHTML = `<img src="${imagePath}" alt="Fotografía de ${delincuente.nombre} ${delincuente.apellido}" style="width:200px;height:auto;">
                             <p>Nombre: ${delincuente.nombre} ${delincuente.apellido}</p>
                             <p>Nacionalidad: ${delincuente.nacionalidad}</p>
                             <p>Cargos:<br>${cargosConSaltosDeLinea}</p>
                             <button id="callPoliceButton">Llamar a la policía</button>`;
    }
    
    
});
