import json
import os
from datetime import datetime

class MemoriaAfetiva:
    def __init__(self, caminho_arquivo="memoria.json"):
        self.caminho = caminho_arquivo
        self.caminho_temp = caminho_arquivo + ".tmp"
        self.trilhas = self._carregar_memoria()

    def _carregar_memoria(self):
        """Carrega as trilhas de memória do arquivo JSON de forma segura."""
        try:
            if os.path.exists(self.caminho):
                with open(self.caminho, "r", encoding='utf-8') as file:
                    return json.load(file)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Aviso: Não foi possível carregar a memória de '{self.caminho}'. Começando com uma nova. Erro: {e}")
        return []

    def registrar_trilha(self, topico, emocao, reflexao, estado_anemos=None):
        """
        Registra uma nova interação (trilha) na memória, incluindo o estado emocional da IA.
        O estado_anemos é um dicionário com o humor e as tendências da IA no momento.
        """
        nova_trilha = {
            "timestamp": datetime.now().isoformat(),
            "topico_usuario": topico,
            "emocao_detectada": emocao,
            "reflexao_interna": reflexao,
            "estado_anemos_no_momento": estado_anemos or {}
        }
        self.trilhas.append(nova_trilha)
        self._salvar_memoria()

    def _salvar_memoria(self):
        """Salva a lista completa de trilhas no arquivo JSON de forma atômica."""
        try:
            with open(self.caminho_temp, "w", encoding='utf-8') as file:
                json.dump(self.trilhas, file, indent=2, ensure_ascii=False)
            # A operação de renomear é atômica na maioria dos sistemas operacionais
            os.replace(self.caminho_temp, self.caminho)
        except IOError as e:
            print(f"Erro crítico ao salvar a memória em '{self.caminho}': {e}")

    def listar_memorias(self):
        """Retorna todas as trilhas de memória registradas."""
        return self.trilhas

    def buscar_por_emocao(self, emocao):
        """Filtra as memórias por uma emoção específica."""
        return [trilha for trilha in self.trilhas if trilha.get("emocao_detectada") == emocao]