import json
import os

class ConhecimentoError(Exception):
    """Exceção para erros relacionados à base de conhecimento."""
    pass

class Conhecimento:
    """Gerencia a base de conhecimento do Anemos a partir de um arquivo JSON."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.fatos = self._carregar_conhecimento()

    def _carregar_conhecimento(self) -> list:
        """Carrega os fatos do arquivo JSON."""
        if not os.path.exists(self.filepath):
            # Cria o arquivo se ele não existir
            with open(self.filepath, 'w', encoding='utf-8') as file:
                json.dump({"fatos": []}, file, ensure_ascii=False, indent=2)
            return []
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if "fatos" not in data or not isinstance(data["fatos"], list):
                    raise ConhecimentoError("O arquivo de conhecimento está mal formatado. A chave 'fatos' não foi encontrada ou não é uma lista.")
                return data["fatos"]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ConhecimentoError(f"Erro ao carregar o arquivo de conhecimento: {e}")

    def adicionar_fato(self, novo_fato: str):
        """Adiciona um novo fato à base de conhecimento e salva o arquivo."""
        if not isinstance(novo_fato, str) or not novo_fato.strip():
            return # Não adiciona fatos vazios

        self.fatos.append(novo_fato.strip())
        self._salvar_conhecimento()

    def _salvar_conhecimento(self):
        """Salva a lista de fatos de volta no arquivo JSON."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as file:
                json.dump({"fatos": self.fatos}, file, ensure_ascii=False, indent=2)
        except IOError as e:
            raise ConhecimentoError(f"Erro ao salvar o arquivo de conhecimento: {e}")

    def listar_fatos(self) -> list:
        """Retorna a lista de todos os fatos conhecidos."""
        return self.fatos
