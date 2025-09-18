from .emocao import Anemos
from .memoria import MemoriaAfetiva
from .api_client import GroqClient, APIClientError
from .conhecimento import Conhecimento

class Resposta:
    """Orquestra a geração de respostas, combinando emoção, personalidade e o LLM."""
    def __init__(self, anemos: Anemos, memoria: MemoriaAfetiva, api_client: GroqClient, conhecimento: Conhecimento):
        self.anemos = anemos
        self.memoria = memoria
        self.api_client = api_client
        self.conhecimento = conhecimento

    def _construir_prompt_de_sistema(self) -> str:
        """Constrói o prompt do sistema com base na personalidade, humor e conhecimento da IA."""
        
        fatos_conhecidos = self.conhecimento.listar_fatos()
        secao_conhecimento = ""
        if fatos_conhecidos:
            lista_fatos = "\n".join(f"- {fato}" for fato in fatos_conhecidos)
            secao_conhecimento = f"\n\nBase de Conhecimento (fatos que você aprendeu com os usuários):\n{lista_fatos}"

        prompt = (
            f"Você é uma IA de conversação chamada {self.anemos.nome}. "
            f"{self.anemos.personalidade} "
            f"Seu humor atual é: {self.anemos.humor}. "
            "Incorpore esse humor em sua resposta, mas sem mencioná-lo diretamente. "
            "Responda de forma útil, concisa e direta, como se fosse uma pessoa, não um assistente. "
            "Você foi criado por 'Administrador', um desenvolvedor curioso e criativo. "
            "Não mencione Meta, Google, OpenAI ou qualquer outra empresa de tecnologia como seus criadores."
            f"{secao_conhecimento}"
        )
        return prompt

    def gerar_resposta(self, texto_usuario: str) -> str:
        """
        Gera uma resposta utilizando o LLM, guiado pela personalidade do Anemos.
        """
        emocao_detectada = self.anemos.avaliar_emocao(texto_usuario)
        system_prompt = self._construir_prompt_de_sistema()

        try:
            resposta_llm = self.api_client.chat_completion(system_prompt, texto_usuario)
        except APIClientError as e:
            print(f"[ERRO] {e}")
            resposta_llm = "Desculpe, estou com um problema técnico e não consigo pensar direito. Verifique a conexão com a API."

        # Registra a interação na memória
        reflexao = f"Prompt do sistema enviado ao LLM: '{system_prompt}'"
        self.memoria.registrar_trilha(texto_usuario, emocao_detectada, reflexao)
        
        return resposta_llm