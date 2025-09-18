from groq import Groq

class APIClientError(Exception):
    """Exceção para erros do cliente da API."""
    pass

class GroqClient:
    """Cliente para interagir com a API da Groq."""
    def __init__(self, api_config: dict):
        if not api_config or 'model' not in api_config or 'api_key' not in api_config:
            raise APIClientError("Configuração da API inválida ou nome do modelo/chave da API não fornecido.")
        
        self.model_name = api_config['model']
        self.temperature = api_config.get('temperature', 0.7)
        self.max_new_tokens = api_config.get('max_new_tokens', 256)
        self.api_key = api_config['api_key']

        if not self.api_key or self.api_key == "SUA_CHAVE_DE_API_AQUI":
            raise APIClientError("A chave da API da Groq não foi definida no arquivo de configuração.")

        try:
            print("Inicializando o cliente da Groq...")
            self.client = Groq(api_key=self.api_key)
            print("Cliente da Groq inicializado com sucesso.")
        except Exception as e:
            raise APIClientError(f"Erro ao inicializar o cliente da Groq: {e}")

    def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Envia uma requisição de chat completion para o LLM via Groq."""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_new_tokens,
            )
            
            response_text = chat_completion.choices[0].message.content
            return response_text.strip()

        except Exception as e:
            raise APIClientError(f"Erro durante a geração de texto com a Groq: {e}")