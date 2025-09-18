document.addEventListener('DOMContentLoaded', () => {
    // --- Seleção de Elementos DOM ---
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const thinkingIndicator = document.querySelector('.thinking-indicator-container');
    
    // Elementos do Rosto (SVG)
    const pixelFace = document.getElementById('pixel-face');
    const faceColumn = document.getElementById('face-column');
    const eyeLeft = document.getElementById('eye-left');
    const eyeRight = document.getElementById('eye-right');
    const mouth = document.getElementById('mouth');

    // --- Estado da Animação ---
    let talkingInterval = null;
    let blinkInterval = null;
    let currentHumor = 'neutro';

    // --- Constantes de Animação ---
    const EYE_SHAPES = {
        neutral: 'M 0 0 H 3 V 3 H 0 Z',
        happy:   'M 0 1 Q 1.5 0 3 1 V 3 H 0 Z',
        sad:     'M 0 2 Q 1.5 3 3 2 V 0 H 0 Z',
        blink:   'M 0 1.5 H 3'
    };

    // --- Funções de Animação do Rosto ---

    /**
     * Atualiza a expressão facial do Anemos com base no humor.
     * Usa morphing de SVG (mudando o atributo 'd') para animações mais ricas.
     */
    const atualizarExpressao = (humor) => {
        currentHumor = humor;

        // Reseta transformações para evitar acúmulo
        eyeLeft.style.transform = '';
        eyeRight.style.transform = '';

        let leftEyeShape = EYE_SHAPES.neutral;
        let rightEyeShape = EYE_SHAPES.neutral;
        let mouthShape = 'M 9 15 H 15'; // Neutro

        switch (humor) {
            case 'alegre':
            case 'animado':
            case 'grato':
                leftEyeShape = EYE_SHAPES.happy;
                rightEyeShape = EYE_SHAPES.happy;
                mouthShape = 'M 8 14 Q 12 18 16 14'; // Sorriso
                break;
            case 'triste':
                leftEyeShape = EYE_SHAPES.sad;
                rightEyeShape = EYE_SHAPES.sad;
                mouthShape = 'M 8 16 Q 12 12 16 16'; // Triste
                break;
            case 'curioso':
            case 'confuso':
                leftEyeShape = EYE_SHAPES.neutral;
                rightEyeShape = EYE_SHAPES.happy; // Um olho "levanta"
                mouthShape = 'M 10 13 A 2 2 0 1 1 14 13 A 2 2 0 1 1 10 13 Z'; // Boca 'O'
                break;
        }

        // Aplica as formas com uma pequena transição no CSS
        eyeLeft.setAttribute('d', leftEyeShape);
        eyeRight.setAttribute('d', rightEyeShape);
        mouth.setAttribute('d', mouthShape);
    };

    /**
     * Inicia a animação de "fala" (boca mexendo).
     */
    const startTalking = () => {
        stopBlinking(); // Para de piscar enquanto fala
        pixelFace.classList.remove('idle'); // Para a animação de respirar
        let scale = 1.0;
        talkingInterval = setInterval(() => {
            scale = scale === 1.0 ? 1.2 : 1.0;
            mouth.style.transform = `scaleY(${scale})`;
            mouth.style.transformOrigin = 'center';
        }, 200);
    };

    /**
     * Para a animação de "fala" e restaura a expressão e animações ociosas.
     */
    const stopTalking = () => {
        clearInterval(talkingInterval);
        talkingInterval = null;
        mouth.style.transform = 'scaleY(1.0)';
        atualizarExpressao(currentHumor);
        pixelFace.classList.add('idle');
        startBlinking(); // Volta a piscar
    };

    /**
     * Animação de piscar usando morphing de path.
     */
    const blink = () => {
        const originalLeft = eyeLeft.getAttribute('d');
        const originalRight = eyeRight.getAttribute('d');

        // Fecha os olhos
        eyeLeft.setAttribute('d', EYE_SHAPES.blink);
        eyeRight.setAttribute('d', EYE_SHAPES.blink);

        // Volta ao normal depois de um tempo
        setTimeout(() => {
            eyeLeft.setAttribute('d', originalLeft);
            eyeRight.setAttribute('d', originalRight);
        }, 150);
    };

    const startBlinking = () => {
        stopBlinking();
        blinkInterval = setInterval(blink, 5000);
    };

    const stopBlinking = () => {
        clearInterval(blinkInterval);
    };

    /**
     * Animação de rastreamento dos olhos com o mouse.
     */
    const handleMouseMove = (e) => {
        const faceRect = faceColumn.getBoundingClientRect();
        const faceCenterX = faceRect.left + faceRect.width / 2;
        const faceCenterY = faceRect.top + faceRect.height / 2;

        const mouseX = e.clientX;
        const mouseY = e.clientY;

        const deltaX = mouseX - faceCenterX;
        const deltaY = mouseY - faceCenterY;

        const moveX = deltaX / 40;
        const moveY = deltaY / 40;

        const limitedMoveX = Math.max(-1.5, Math.min(1.5, moveX));
        const limitedMoveY = Math.max(-1, Math.min(1, moveY));

        // Aplica a transformação ao grupo dos olhos
        document.getElementById('eyes-group').style.transform = `translate(${limitedMoveX}px, ${limitedMoveY}px)`;
    };

    // --- Lógica do Chat (sem alterações) ---

    const saveMessage = (message) => {
        let history = JSON.parse(localStorage.getItem('chatHistory')) || [];
        history.push(message);
        localStorage.setItem('chatHistory', JSON.stringify(history));
    };

    const loadHistory = () => {
        let history = JSON.parse(localStorage.getItem('chatHistory')) || [];
        history.forEach(message => {
            addMessage(message.sender, message.text, message.senderName, false);
        });
    };

    const addMessage = (sender, text, senderName, shouldSave = true) => {
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
        if (shouldSave) {
            saveMessage({ sender, text, senderName });
        }
    };

    const sendMessage = async () => {
        const messageText = chatInput.value.trim();
        if (messageText === '') return;

        chatInput.disabled = true;
        sendButton.disabled = true;
        thinkingIndicator.style.display = 'flex';

        addMessage('user', messageText, 'Você');
        chatInput.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensagem: messageText }),
            });

            if (!response.ok) throw new Error('A resposta da rede não foi boa.');

            const data = await response.json();
            
            addMessage('bot', data.resposta, `${data.nome} (${data.humor})`);

            // --- Nova Lógica de Animação ---
            
            // 1. Mostra a reação emocional imediatamente
            atualizarExpressao(data.humor);
            stopBlinking(); // Para de piscar durante a reação

            // 2. Define um timer para voltar ao neutro e começar a falar
            setTimeout(() => {
                atualizarExpressao('neutro'); // Volta para a expressão neutra
                
                if (data.audio_data) {
                    const audioSrc = `data:audio/mpeg;base64,${data.audio_data}`;
                    const audio = new Audio(audioSrc);
                    startTalking(); // Começa a animar a boca SÓ AGORA
                    audio.play();
                    audio.onended = () => stopTalking();
                } else {
                    stopTalking(); // Se não tiver áudio, apenas para tudo e volta ao normal
                }

            }, 1000); // Duração da expressão em milissegundos

        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            atualizarExpressao('confuso');
            addMessage('bot', 'Desculpe, ocorreu um erro ao me conectar.', 'System');
            // Garante que as animações parem em caso de erro
            setTimeout(stopTalking, 1000); 
        } finally {
            // A lógica de reabilitar o input fica, mas a de parar de falar foi movida
            chatInput.disabled = false;
            sendButton.disabled = false;
            thinkingIndicator.style.display = 'none';
            chatInput.focus();
        }
    };

    // --- Inicialização ---
    loadHistory();
    atualizarExpressao(currentHumor);
    pixelFace.classList.add('idle');
    startBlinking();
    chatInput.focus();

    faceColumn.addEventListener('mousemove', handleMouseMove);

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
