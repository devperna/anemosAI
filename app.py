import io
import base64
from openai import OpenAI
import os
import sys
from flask import Flask, render_template, request, jsonify

# --- Configuração das Chaves de API ---
# ATENÇÃO: Manter chaves de API no código é uma má prática de segurança.
# O ideal é usar variáveis de ambiente.
os.environ['GROQ_API_KEY'] = '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'
os.environ['OPENAI_API_KEY'] = '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'

# Adiciona o diretório do projeto ao path para permitir importações relativas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from python.config import Config, ConfigError
from python.emocao import Anemos
from python.memoria import MemoriaAfetiva
from python.api_client import GroqClient, APIClientError
from python.conhecimento import Conhecimento, ConhecimentoError
from python.resposta import Resposta

app = Flask(__name__)

# --- Inicialização do Chatbot ---
PROJETO_DIR = os.path.dirname(os.path.abspath(__file__))
gerador_resposta = None
anemos = None

def inicializar_chatbot():
    """Carrega todas as configurações e componentes do chatbot."""
    global gerador_resposta, anemos
    try:
        config_path = os.path.join(PROJETO_DIR, 'config', 'config.yaml')
        config = Config(config_path)

        conhecimento_path = os.path.join(PROJETO_DIR, 'conhecimento_usuario.json')
        conhecimento = Conhecimento(conhecimento_path)

        anemos = Anemos(config)
        memoria = MemoriaAfetiva(os.path.join(PROJETO_DIR, 'memoria.json'))
        api_client = GroqClient(config.api_config)
        gerador_resposta = Resposta(anemos, memoria, api_client, conhecimento)

        print("Chatbot inicializado com sucesso!")

    except (ConfigError, APIClientError, ConhecimentoError) as e:
        print(f"Erro Crítico na Inicialização: {e}", file=sys.stderr)
        sys.exit(1)

# --- Rotas da Aplicação ---

@app.route('/')
def index():
    """Serve a página principal da interface de chat."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Recebe a mensagem do usuário, gera uma resposta e a retorna com áudio em Base64."""
    if not gerador_resposta or not anemos:
        return jsonify({'erro': 'Chatbot não foi inicializado corretamente.'}), 500

    texto_usuario = request.json.get('mensagem')
    if not texto_usuario:
        return jsonify({'erro': 'Nenhuma mensagem recebida.'}), 400

    # Lógica de aprendizado
    texto_lower = texto_usuario.lower().strip()
    if texto_lower.startswith("anemos, aprenda que"):
        novo_fato = texto_usuario[len("anemos, aprenda que"):].strip()
        if novo_fato:
            gerador_resposta.conhecimento.adicionar_fato(novo_fato)
            resposta_ia = f"Entendido! Aprendi que: '{novo_fato}'"
        else:
            resposta_ia = "O que você quer que eu aprenda? Diga 'Anemos, aprenda que...' seguido do fato."
    else:
        # Geração de resposta normal
        resposta_ia = gerador_resposta.gerar_resposta(texto_usuario)

    # --- Geração do Áudio com OpenAI ---
    audio_data = None
    try:
        if resposta_ia:
            client = OpenAI()
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=resposta_ia
            )
            mp3_bytes = response.read()
            audio_data = base64.b64encode(mp3_bytes).decode('utf-8')
    except Exception as e:
        print(f"Erro ao gerar áudio com OpenAI: {e}", file=sys.stderr)

    return jsonify({
        'nome': anemos.nome,
        'humor': anemos.humor,
        'resposta': resposta_ia,
        'audio_data': audio_data
    })

if __name__ == '__main__':
    inicializar_chatbot()
    app.run(debug=True, port=5000)