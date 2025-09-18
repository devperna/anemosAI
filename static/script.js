document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const mouth = document.getElementById('mouth');
    const eyeLeft = document.getElementById('eye-left');
    const eyeRight = document.getElementById('eye-right');

    let talkingInterval = null;
    let currentHumor = 'neutro';

    // --- Animações do Rosto ---

    const atualizarExpressao = (humor) => {
        currentHumor = humor;
        switch (humor) {
            case 'alegre':
            case 'animado':
            case 'grato':
                mouth.setAttribute('d', 'M 8 14 Q 12 18 16 14'); // Sorriso
                break;
            case 'triste':
                mouth.setAttribute('d', 'M 8 16 Q 12 12 16 16'); // Triste
                break;
            case 'curioso':
            case 'confuso':
                mouth.setAttribute('d', 'M 10 13 A 2 2 0 1 1 14 13 A 2 2 0 1 1 10 13 Z'); // Boca 'O'
                break;
            case 'neutro':
            default:
                mouth.setAttribute('d', 'M 9 15 H 15'); // Linha reta
                break;
        }
    };

    const startTalking = () => {
        stopTalking();
        let scale = 1.0;
        talkingInterval = setInterval(() => {
            scale = scale === 1.0 ? 1.2 : 1.0;
            mouth.style.transform = `scaleY(${scale})`;
            mouth.style.transformOrigin = 'center';
        }, 200);
    };

    const stopTalking = () => {
        clearInterval(talkingInterval);
        talkingInterval = null;
        mouth.style.transform = 'scaleY(1.0)';
        atualizarExpressao(currentHumor);
    };

    const blink = () => {
        eyeLeft.setAttribute('height', '0.5');
        eyeRight.setAttribute('height', '0.5');
        setTimeout(() => {
            eyeLeft.setAttribute('height', '3');
            eyeRight.setAttribute('height', '3');
        }, 150);
    };

    // --- Lógica do Chat ---

    const addMessage = (sender, text, senderName) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);

        const textContainer = document.createElement('div');

        if (sender === 'bot') {
            const senderNameElement = document.createElement('div');
            senderNameElement.classList.add('sender');
            senderNameElement.textContent = senderName;
            textContainer.appendChild(senderNameElement);
        }
        
        const textElement = document.createElement('p');
        textElement.textContent = text;
        textContainer.appendChild(textElement);

        messageElement.appendChild(textContainer);
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const sendMessage = async () => {
        const messageText = chatInput.value.trim();
        if (messageText === '') return;

        // Desabilita o input para evitar múltiplas mensagens
        chatInput.disabled = true;
        sendButton.disabled = true;

        addMessage('user', messageText);
        chatInput.value = '';

        // Inicia a animação de fala imediatamente
        startTalking();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ mensagem: messageText }),
            });

            if (!response.ok) throw new Error('A resposta da rede não foi boa.');

            const data = await response.json();
            
            atualizarExpressao(data.humor);
            addMessage('bot', data.resposta, `${data.nome} (${data.humor})`);

            if (data.audio_data) {
                const audioSrc = `data:audio/mpeg;base64,${data.audio_data}`;
                const audio = new Audio(audioSrc);
                audio.play();
                // A animação de fala para quando o áudio terminar
                audio.onended = () => {
                    stopTalking();
                };
            } else {
                // Se não houver áudio, para a animação imediatamente
                stopTalking();
            }

        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            atualizarExpressao('confuso');
            stopTalking();
            addMessage('bot', 'Desculpe, ocorreu um erro ao me conectar.', 'System');
        } finally {
            // Reabilita o input e foca nele
            chatInput.disabled = false;
            sendButton.disabled = false;
            chatInput.focus();
        }
    };

    // --- Inicialização ---
    atualizarExpressao(currentHumor);
    setInterval(blink, 5000);
    chatInput.focus();

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});