import yaml
import os

class ConfigError(Exception):
    """Exceção para erros de configuração."""
    pass

class Config:
    """Carrega e fornece acesso às configurações do projeto a partir de um arquivo YAML."""
    def __init__(self, config_path="config.yaml"):
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
            if not isinstance(self._config, dict):
                raise ConfigError("O arquivo de configuração não é um dicionário válido.")
        except FileNotFoundError:
            raise ConfigError(f"Arquivo de configuração não encontrado em: {config_path}")
        except yaml.YAMLError as e:
            raise ConfigError(f"Erro ao decodificar o arquivo YAML: {e}")

        # Carrega a chave da API a partir da variável de ambiente
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            raise ConfigError("A variável de ambiente GROQ_API_KEY não foi definida. Por favor, defina-a com sua chave da API da Groq.")
        
        # Garante que a seção 'api' exista e injeta a chave
        if 'api' not in self._config:
            self._config['api'] = {}
        self._config['api']['api_key'] = api_key

    @property
    def nome_ia(self):
        return self._config.get("nome", "Anemos")

    @property
    def personalidade_base(self):
        return self.get_nested("personalidade_base", "")

    @property
    def api_config(self):
        return self.get_nested("api", required=True)

    @property
    def humor_inicial(self):
        return self.get_nested("humor_inicial", "neutro")

    @property
    def mapa_emocional(self):
        return self.get_nested("mapa_emocional", required=True)

    def get_nested(self, key, default=None, required=False):
        """Acessa chaves aninhadas na configuração de forma segura."""
        if required and key not in self._config:
            raise ConfigError(f"A chave de configuração obrigatória '{key}' não foi encontrada.")
        return self._config.get(key, default)
