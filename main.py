import os
import sys

# Adiciona o diretório do projeto ao path para permitir importações relativas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from python.config import Config, ConfigError
from python.emocao import Anemos
from python.memoria import MemoriaAfetiva
from python.api_client import GroqClient, APIClientError
from python.conhecimento import Conhecimento, ConhecimentoError
from python.resposta import Resposta

PROJETO_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    """Função principal que inicializa e executa o chatbot Anemos."""
    try:
        # 1. Carrega a configuração
        config_path = os.path.join(PROJETO_DIR, 'config', 'config.yaml')
        config = Config(config_path)

        # 2. Inicializa a base de conhecimento
        conhecimento_path = os.path.join(PROJETO_DIR, 'conhecimento_usuario.json')
        conhecimento = Conhecimento(conhecimento_path)

        # 3. Inicializa os outros componentes da IA
        anemos = Anemos(config)
        memoria = MemoriaAfetiva(os.path.join(PROJETO_DIR, 'memoria.json'))
        api_client = GroqClient(config.api_config)
        gerador_resposta = Resposta(anemos, memoria, api_client, conhecimento)

    except (ConfigError, APIClientError, ConhecimentoError) as e:
        print(f"Erro Crítico na Inicialização: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Definições dos Rostos ASCII ---
    FACES = {
        "neutro": """
    .-------.
   |  o o  |
   |   -   |
   '-------'
""",
        "feliz": """
    .-------.
   |  o o  |
   |   ^   |
   '-- U --'
""",
        "triste": """
    .-------.
   |  o o  |
   |   v   |
   '-- n --'
""",
        "curioso": """
    .-------.
   |  o o  |
   |   ?   |
   '-------'
""",
        "falando": """ # Rosto genérico para quando está processando/falando
    .-------.
   |  o o  |
   |   O   |
   '-------'
"""
    }

    def get_face(humor_atual, estado_falando=False):
        if estado_falando:
            return FACES["falando"]
        return FACES.get(humor_atual, FACES["neutro"]) # Retorna neutro se o humor não for mapeado

    # --- Loop Principal da Conversa ---
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"--- {anemos.nome} --- A IA com Personalidade ---")
    print(f"{anemos.personalidade}")
    print("-------------------------------------------")
    print(f"Olá! Eu sou {anemos.nome}. Como posso ajudar hoje? (digite 'sair' para terminar)")
    print("Para me ensinar algo, digite: Anemos, aprenda que...")
    
    try:
        while True:
            print(IDLE_FACE)
            texto_usuario = input("Você: ")
            if not texto_usuario.strip():
                continue

            texto_lower = texto_usuario.lower().strip()

            if texto_lower == "sair":
                print("Até mais! Foi um prazer conversar com você.")
                break
            
            print(TALKING_FACE)

            # Comando de aprendizado
            if texto_lower.startswith("anemos, aprenda que"):
                novo_fato = texto_usuario[len("anemos, aprenda que"):].strip()
                if novo_fato:
                    conhecimento.adicionar_fato(novo_fato)
                    print(f"{anemos.nome}: Entendido! Aprendi que: '{novo_fato}'")
                else:
                    print(f"{anemos.nome}: O que você quer que eu aprenda? Diga 'Anemos, aprenda que...' seguido do fato.")
            else:
                # Geração de resposta normal
                resposta_ia = gerador_resposta.gerar_resposta(texto_usuario)
                print(f"{anemos.nome} ({anemos.humor}): {resposta_ia}")
            
            print("-" * 20) # Separador

    except KeyboardInterrupt:
        print("\nConversa interrompida. Até a próxima!")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado durante a execução: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
