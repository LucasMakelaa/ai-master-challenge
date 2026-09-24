"""Triagem de um ticket: texto entra, categoria + confianca + decisao saem.

Uso:
  python triar.py "outlook not starting please help"
  python triar.py            (modo interativo: digite um ticket por linha, linha vazia sai)
"""
import sys
from pathlib import Path
import joblib
from politica import decidir, LIMIAR

M = joblib.load(Path(__file__).parent / "modelo" / "triagem.joblib")


def triar(texto: str):
    x = M["vec"].transform([texto])
    proba = M["modelo"].predict_proba(x)[0]
    ordem = proba.argsort()[::-1]
    cat, conf = M["classes"][ordem[0]], float(proba[ordem[0]])
    decisao, motivo = decidir(cat, conf)
    return cat, conf, decisao, motivo, [(M["classes"][i], float(proba[i])) for i in ordem[:3]]


def mostrar(texto: str):
    cat, conf, decisao, motivo, top3 = triar(texto)
    print(f"\nTicket: {texto[:110]}{'...' if len(texto) > 110 else ''}")
    print(f"  Categoria prevista: {cat}  (confianca {conf:.0%})")
    print("  Top 3: " + " | ".join(f"{c} {p:.0%}" for c, p in top3))
    print(f"  DECISAO: {decisao}  ->  {motivo}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mostrar(" ".join(sys.argv[1:]))
    else:
        print(f"Triagem de tickets (limiar de automacao {LIMIAR:.0%}). Linha vazia para sair.")
        while True:
            t = input("\nticket> ").strip()
            if not t:
                break
            mostrar(t)
