// Secuencia del código Konami
const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
let konamiIndex = 0;

// Función para obtener el token CSRF
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

// Función para activar el modo moderador
async function activateModeratorMode() {
    try {
        const response = await fetch('/activate-konami/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            window.location.reload();
        }
    } catch (error) {
        console.error('Error activating moderator mode:', error);
    }
}

// Evento para detectar las teclas presionadas
document.addEventListener('keydown', function(e) {
    // Verificar si la tecla presionada coincide con la secuencia
    if (e.key === konamiCode[konamiIndex]) {
        konamiIndex++;
        
        // Si se completó la secuencia
        if (konamiIndex === konamiCode.length) {
            // Mostrar el mensaje de confirmación
            const result = confirm('¿Quieres activar el modo moderador?');
            if (result) {
                activateModeratorMode();
            }
            konamiIndex = 0;
        }
    } else {
        konamiIndex = 0;
    }
}); 