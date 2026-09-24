"""Passo 2: o Dataset 1 tem sinal de verdade ou parece sorteio?

Cada teste responde: 'isso poderia ter sido gerado ao acaso?'. p-valor alto = pode ser acaso.
"""
import sys
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import make_pipeline

D = sys.argv[1]
a = pd.read_csv(D + "/customer_support_tickets.csv")
a["frt"] = pd.to_datetime(a["First Response Time"])
a["ttr"] = pd.to_datetime(a["Time to Resolution"])

print("=== A. As categorias parecem sorteio uniforme? (qui-quadrado contra 'todas iguais') ===")
closed = a[a["Ticket Status"] == "Closed"]
for nome, s in [("Tipo", a["Ticket Type"]), ("Prioridade", a["Ticket Priority"]),
                ("Canal", a["Ticket Channel"]), ("Status", a["Ticket Status"]),
                ("Nota de satisfacao (so fechados)", closed["Customer Satisfaction Rating"])]:
    obs = s.value_counts().values
    chi2, p = stats.chisquare(obs)
    print(f"{nome:36s} n={obs.sum():5d}  categorias={len(obs)}  maior/menor={obs.max()/obs.min():.2f}  p={p:.3f}")

print("\n=== B. As colunas de tempo medem tempo? ===")
print("datas distintas em 'First Response Time':", a["frt"].dt.date.nunique(), "->", a["frt"].dt.date.dropna().unique()[:3])
print("datas distintas em 'Time to Resolution':", a["ttr"].dt.date.nunique(), "->", a["ttr"].dt.date.dropna().unique()[:3])
both = a.dropna(subset=["frt", "ttr"]).copy()
both["dur_h"] = (both["ttr"] - both["frt"]).dt.total_seconds() / 3600
neg = (both["dur_h"] < 0).mean()
print(f"tickets com resposta E resolucao: {len(both)}")
print(f"resolucao ANTES da primeira resposta: {neg:.1%}  (duracao minima {both['dur_h'].min():.1f} h, maxima {both['dur_h'].max():.1f} h)")
print("Se fosse tempo real, isso deveria ser ~0%.")

print("\n=== C. Alguma variavel explica a satisfacao? (so os 2.769 fechados) ===")
closed = closed.copy()
closed["frt"] = pd.to_datetime(closed["First Response Time"])
closed["ttr"] = pd.to_datetime(closed["Time to Resolution"])
closed["dur_h"] = (closed["ttr"] - closed["frt"]).dt.total_seconds() / 3600
closed["hora_resp"] = closed["frt"].dt.hour
rows = []
y = closed["Customer Satisfaction Rating"]
for col in ["Ticket Channel", "Ticket Priority", "Ticket Type", "Product Purchased", "Customer Gender"]:
    grupos = [g["Customer Satisfaction Rating"].values for _, g in closed.groupby(col)]
    h, p = stats.kruskal(*grupos)
    rows.append((f"nota ~ {col}", "Kruskal-Wallis", p))
for col, nome in [("dur_h", "duracao resposta->resolucao"), ("hora_resp", "hora da 1a resposta"), ("Customer Age", "idade")]:
    rho, p = stats.spearmanr(closed[col], y)
    rows.append((f"nota ~ {nome}", f"Spearman rho={rho:+.3f}", p))
for r in rows:
    print(f"{r[0]:42s} {r[1]:28s} p={r[2]:.3f}")
n_testes = len(rows)
print(f"\n{n_testes} testes feitos. Com limite de 5%, o esperado por puro acaso e ~{n_testes*0.05:.1f} 'falso positivo'."
      f" Ajuste de Bonferroni: so vale p < {0.05/n_testes:.4f}.")
print("Testes com p abaixo desse limite:", sum(r[2] < 0.05 / n_testes for r in rows))

print("\n=== D. O tempo depende de canal/prioridade/tipo? (Kruskal-Wallis na duracao) ===")
for col in ["Ticket Channel", "Ticket Priority", "Ticket Type"]:
    grupos = [g["dur_h"].dropna().values for _, g in both.groupby(col)]
    h, p = stats.kruskal(*grupos)
    med = both.groupby(col)["dur_h"].median().round(2).to_dict()
    print(f"duracao ~ {col:16s} p={p:.3f}  medianas(h)={med}")

print("\n=== E. O TEXTO da descricao tem relacao com o rotulo? (TF-IDF + regressao logistica, 5 dobras) ===")
cv = StratifiedKFold(5, shuffle=True, random_state=42)
for alvo in ["Ticket Type", "Ticket Priority", "Ticket Channel"]:
    pipe = make_pipeline(TfidfVectorizer(max_features=20000, ngram_range=(1, 2), min_df=3),
                         LogisticRegression(max_iter=1000))
    acc = cross_val_score(pipe, a["Ticket Description"], a[alvo], cv=cv, scoring="accuracy")
    base = 1 / a[alvo].nunique()
    print(f"prever {alvo:16s} pelo texto: acuracia {acc.mean():.1%}  (acaso puro = {base:.0%}, {a[alvo].nunique()} classes)")
