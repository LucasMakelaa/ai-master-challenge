"""Politica de triagem: quando a IA roteia sozinha e quando o ticket vai para um humano.

Regras (decisoes de negocio, nao de modelo):
- Confianca abaixo do limiar: humano.
- Categorias que nunca sao roteadas sozinhas, mesmo com confianca alta:
    * Administrative rights: o modelo so recupera 71% dos casos e o assunto e permissao de acesso,
      onde erro tem custo de seguranca.
    * Miscellaneous: e a caixa de 'nao sei'. Rotear sozinho para um balde sem dono nao ajuda ninguem.
"""
LIMIAR = 0.90
SEMPRE_HUMANO = {"Administrative rights", "Miscellaneous"}


def decidir(categoria: str, confianca: float, limiar: float = LIMIAR) -> tuple[str, str]:
    if categoria in SEMPRE_HUMANO:
        return "HUMANO", f"categoria '{categoria}' nunca e roteada sozinha"
    if confianca < limiar:
        return "HUMANO", f"confianca {confianca:.0%} abaixo do limiar {limiar:.0%}"
    return "AUTOMATICO", f"confianca {confianca:.0%} e categoria segura"
