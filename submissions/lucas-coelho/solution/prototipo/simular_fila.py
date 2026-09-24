"""Simula a fila: passa o conjunto de TESTE (tickets que o modelo nunca viu) pela politica de triagem
e mede o que seria automatizado, quanto erra, e a economia sob premissas explicitas.

Uso: python simular_fila.py <pasta_dos_dados>
"""
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from politica import decidir, LIMIAR, SEMPRE_HUMANO

AQUI = Path(__file__).parent
M = joblib.load(AQUI / "modelo" / "triagem.joblib")

df = pd.read_csv(Path(sys.argv[1]) / "all_tickets_processed_improved_v3.csv")
df["doc"] = df["Document"].astype(str)
df = df[df["doc"].str.split().str.len() >= 3].reset_index(drop=True)
_, X_te, _, y_te = train_test_split(df["doc"], df["Topic_group"], test_size=0.2, stratify=df["Topic_group"], random_state=42)

proba = M["modelo"].predict_proba(M["vec"].transform(X_te))
classes = np.array(M["classes"])
pred = classes[proba.argmax(1)]
conf = proba.max(1)
dec = np.array([decidir(c, p)[0] for c, p in zip(pred, conf)])
auto = dec == "AUTOMATICO"
acerto = pred == y_te.values

n = len(y_te)
print(f"FILA SIMULADA: {n} tickets nunca vistos pelo modelo. Limiar {LIMIAR:.0%}; sempre humano: {sorted(SEMPRE_HUMANO)}")
print(f"  roteados sozinhos: {auto.sum()} ({auto.mean():.1%})")
print(f"  acerto no que foi automatico: {acerto[auto].mean():.1%}  -> {int((~acerto[auto]).sum())} tickets mal roteados")
print(f"  foram pra humano: {(~auto).sum()} ({(~auto).mean():.1%})")
print(f"  acerto do modelo no que foi pra humano (ele ajuda com uma sugestao): {acerto[~auto].mean():.1%}")

print("\nDe onde vem o 'humano':")
for c in sorted(set(classes)):
    m = (y_te.values == c)
    print(f"  {c:22s} {m.sum():5d} tickets, {(auto & m).sum()/m.sum():5.1%} roteados sozinhos")

# economia sob premissas EXPLICITAS. Substituir pelos numeros reais da operacao.
print("\nECONOMIA (premissas, nao medicao). Volume = 30.000 tickets/ano, como no enunciado.")
vol = 30000
cobertura = float(auto.mean())
erro_auto = float((~acerto[auto]).mean())
linhas = []
for min_triagem in (1, 2, 3):
    horas_poupadas = vol * cobertura * min_triagem / 60
    # cada erro de roteamento custa retrabalho: premissa de 10 min para reencaminhar
    horas_retrabalho = vol * cobertura * erro_auto * 10 / 60
    liquido = horas_poupadas - horas_retrabalho
    linhas.append({"min_triagem_manual": min_triagem, "horas_poupadas_ano": round(horas_poupadas),
                   "horas_retrabalho_ano": round(horas_retrabalho), "liquido_horas_ano": round(liquido),
                   "equivale_meses_de_1_pessoa(160h)": round(liquido / 160, 1)})
    print(f"  triagem manual de {min_triagem} min/ticket: poupa {horas_poupadas:,.0f} h/ano, "
          f"retrabalho dos erros (10 min cada) {horas_retrabalho:,.0f} h -> liquido {liquido:,.0f} h/ano "
          f"(~{liquido/160:.1f} meses de 1 pessoa)")

json.dump({"n_fila": int(n), "limiar": LIMIAR, "sempre_humano": sorted(SEMPRE_HUMANO),
           "cobertura_auto": round(cobertura, 4), "acerto_auto": round(float(acerto[auto].mean()), 4),
           "mal_roteados": int((~acerto[auto]).sum()), "acerto_no_humano": round(float(acerto[~auto].mean()), 4),
           "economia_premissas": linhas},
          open(AQUI / "relatorios" / "simulacao.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
