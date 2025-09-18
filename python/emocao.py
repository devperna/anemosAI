import re
from .config import Config

class Anemos:
    """Gerencia o estado emocional e a personalidade da IA com base na configuração."""
    def __init__(self, config: Config):
        self.config = config
        self.nome = config.nome_ia
        self.personalidade = config.personalidade_base
        self.humor = config.humor_inicial
        self.mapa_emocional = config.mapa_emocional

    def avaliar_emocao(self, texto: str) -> str:
        """Avalia a emoção do texto e atualiza o humor da IA."""
        texto_normalizado = ' '.join(re.findall(r'\b\w+\b', texto.lower()))
        pontuacoes = {emocao: 0.0 for emocao in self.mapa_emocional}

        for emocao, data in self.mapa_emocional.items():
            palavras_chave = data.get("palavras_chave", {})
            for palavra, peso in palavras_chave.items():
                if palavra in texto_normalizado:
                    pontuacoes[emocao] += peso
        
        emocao_predominante = max(pontuacoes, key=pontuacoes.get, default='neutro')

        if pontuacoes.get(emocao_predominante, 0) > 0:
            self.humor = emocao_predominante
        else:
            self.humor = 'neutro'
                
        return self.humor
