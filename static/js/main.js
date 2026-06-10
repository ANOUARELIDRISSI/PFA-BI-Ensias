// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // Récupère les données du contexte (sidebar)
    function getContext() {
        return {
            ville: document.getElementById('ville').value,
            surface: document.getElementById('surface').value,
            type_bien: document.getElementById('type_bien').value
        };
    }

    // Ajoute un message dans l'interface
    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        
        const bubble = document.createElement('div');
        bubble.classList.add('bubble');
        bubble.innerHTML = text; // Permet d'injecter du HTML basique (retour à la ligne, gras)

        messageDiv.appendChild(bubble);
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        return messageDiv;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Affiche le message utilisateur
        appendMessage('user', message);
        userInput.value = '';

        // Affiche un indicateur de chargement
        const loadingMsg = appendMessage('bot', '<span class="loading">L\'agent réfléchit...</span>');

        try {
            // Requête vers le backend Flask
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    context: getContext()
                })
            });

            const data = await response.json();
            
            // Remplace le chargement par la réponse de l'IA
            loadingMsg.querySelector('.bubble').innerHTML = data.reply;
        } catch (error) {
            loadingMsg.querySelector('.bubble').innerHTML = "<em>Erreur de connexion avec le serveur.</em>";
        }
    }

    // Événements d'envoi
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});