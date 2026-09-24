"""Treina o classificador de triagem (Dataset 2) e avalia com rigor.

Uso:  python treinar_e_avaliar.py <pasta_dos_dados>
Saidas em prototipo/relatorios/ e modelo em prototipo/modelo/triagem.joblib
"""
import sys, json, time
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

AQUI = Path(__file__).parent
DADOS = Path(sys.argv[1])
REL = AQUI / "relatorios"; REL.mkdir(exist_ok=True)
MOD = AQUI / "modelo"; MOD.mkdir(exist_ok=True)

t0 = time.time()
df = pd.read_csv(DADOS / "all_tickets_processed_improved_v3.csv")
df["doc"] = df["Document"].astype(str)
antes = len(df)
df = df[df["doc"].str.split().str.len() >= 3].reset_index(drop=True)   # 14 textos vazios ou de 1-2 palavras
print(f"linhas: {antes} -> {len(df)} (removidos {antes-len(df)} textos com menos de 3 palavras)")

X_tr_txt, X_te_txt, y_tr, y_te = train_test_split(df["doc"], df["Topic_group"], test_size=0.2,
                                                  stratify=df["Topic_group"], random_state=42)
print("treino:", len(X_tr_txt), "| teste (nunca visto no treino):", len(X_te_txt))

vec = TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_features=250000, sublinear_tf=True)
X_tr = vec.fit_transform(X_tr_txt)      # o vetorizador so ve o treino
X_te = vec.transform(X_te_txt)
print("vocabulario:", X_tr.shape[1])

resultados = {}
# 1) linha de base: sempre chutar a categoria mais comum
dummy = DummyClassifier(strategy="most_frequent").fit(X_tr, y_tr)
p = dummy.predict(X_te)
resultados["Chutar sempre a mais comum"] = (accuracy_score(y_te, p), f1_score(y_te, p, average="macro"))
# 2) regressao logistica
lr = LogisticRegression(max_iter=2000, C=10)
lr.fit(X_tr, y_tr); p = lr.predict(X_te)
resultados["Regressao logistica"] = (accuracy_score(y_te, p), f1_score(y_te, p, average="macro"))
# 3) SVM linear com probabilidades calibradas
svm = CalibratedClassifierCV(LinearSVC(C=0.5), cv=3, method="sigmoid")
svm.fit(X_tr, y_tr); p_svm = svm.predict(X_te)
resultados["SVM linear calibrado"] = (accuracy_score(y_te, p_svm), f1_score(y_te, p_svm, average="macro"))

print("\nMODELO                          acuracia   F1-macro")
for k, (a, f) in resultados.items():
    print(f"{k:30s}  {a:7.1%}   {f:7.3f}")

# modelo escolhido: o de maior F1-macro entre lr e svm (F1-macro pune ignorar categorias pequenas)
escolhido, mdl = ("SVM linear calibrado", svm) if resultados["SVM linear calibrado"][1] >= resultados["Regressao logistica"][1] else ("Regressao logistica", lr)
proba = mdl.predict_proba(X_te)
classes = mdl.classes_
pred = classes[proba.argmax(1)]
conf = proba.max(1)
y_te_arr = y_te.values
print(f"\nMODELO ESCOLHIDO: {escolhido}")
rep = classification_report(y_te_arr, pred, output_dict=True, zero_division=0)
print(classification_report(y_te_arr, pred, zero_division=0))

# ---- rigor 1: quase-duplicatas entre teste e treino inflam o resultado? ----
maxsim = np.zeros(X_te.shape[0])
XtrT = X_tr.T.tocsc()
for i in range(0, X_te.shape[0], 1000):
    bloco = (X_te[i:i+1000] @ XtrT).toarray()
    maxsim[i:i+1000] = bloco.max(1)
acerto = (pred == y_te_arr)
print("\nQUASE-DUPLICATAS (similaridade de cosseno do ticket de teste com o mais parecido do treino):")
faixas = [(0, .5), (.5, .7), (.7, .9), (.9, 1.01)]
tab_dup = []
for lo, hi in faixas:
    m = (maxsim >= lo) & (maxsim < hi)
    if m.sum():
        tab_dup.append({"faixa": f"{lo:.1f}-{min(hi,1):.1f}", "n": int(m.sum()), "%_do_teste": round(m.mean()*100, 1),
                        "acuracia": round(acerto[m].mean()*100, 1)})
        print(f"  {lo:.1f} a {min(hi,1):.1f}: n={m.sum():5d} ({m.mean():5.1%} do teste)  acuracia={acerto[m].mean():.1%}")
sem_dup = maxsim < 0.9
print(f"  acuracia so nos tickets SEM parecido >=0.9 no treino: {acerto[sem_dup].mean():.1%} (n={sem_dup.sum()})")

# ---- rigor 2: confianca x cobertura (o que da pra automatizar sem errar demais) ----
print("\nCONFIANCA x COBERTURA (auto-roteia se confianca >= limiar; o resto vai pra humano):")
tab_cov = []
for t in [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
    m = conf >= t
    tab_cov.append({"limiar": t, "cobertura_%": round(m.mean()*100, 1), "acuracia_auto_%": round(acerto[m].mean()*100, 1),
                    "erros_a_cada_100_auto": round((1-acerto[m].mean())*100, 1)})
    print(f"  limiar {t:.2f}: automatiza {m.mean():5.1%}  |  acerta {acerto[m].mean():5.1%} do que automatiza")

# ---- por categoria: onde o modelo e confiavel ----
print("\nPOR CATEGORIA (precisao / recall / n no teste):")
por_cat = []
for c in classes:
    r = rep[c]
    por_cat.append({"categoria": c, "precisao": round(r["precision"], 3), "recall": round(r["recall"], 3), "n_teste": int(r["support"])})
    print(f"  {c:22s} precisao={r['precision']:.2f} recall={r['recall']:.2f} n={int(r['support'])}")

# graficos
cm = confusion_matrix(y_te_arr, pred, labels=classes, normalize="true")
fig, ax = plt.subplots(figsize=(7.5, 6.3))
im = ax.imshow(cm, cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(classes))); ax.set_yticks(range(len(classes)))
ax.set_xticklabels(classes, rotation=40, ha="right"); ax.set_yticklabels(classes)
for i in range(len(classes)):
    for j in range(len(classes)):
        ax.text(j, i, f"{cm[i,j]:.0%}", ha="center", va="center", color="white" if cm[i, j] > .5 else "black", fontsize=8)
ax.set_xlabel("O modelo previu"); ax.set_ylabel("Categoria real")
ax.set_title("Onde o classificador acerta e onde confunde (% da categoria real)")
fig.tight_layout(); fig.savefig(REL / "matriz_confusao.png", dpi=140); plt.close(fig)

ts = np.linspace(0, 0.99, 100)
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot([(conf >= t).mean()*100 for t in ts], [acerto[conf >= t].mean()*100 for t in ts], color="#1F3A5F")
ax.set_xlabel("% dos tickets que a IA roteia sozinha (cobertura)"); ax.set_ylabel("% de acerto no que ela roteia")
ax.set_title("Quanto mais eu automatizo, mais erro aceito"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(REL / "cobertura_x_acerto.png", dpi=140); plt.close(fig)

joblib.dump({"vec": vec, "modelo": mdl, "classes": list(classes), "nome_modelo": escolhido}, MOD / "triagem.joblib")
json.dump({"modelos": {k: {"acuracia": round(a, 4), "f1_macro": round(f, 4)} for k, (a, f) in resultados.items()},
           "escolhido": escolhido, "quase_duplicatas": tab_dup, "acuracia_sem_quase_duplicata": round(float(acerto[sem_dup].mean()), 4),
           "cobertura_x_acerto": tab_cov, "por_categoria": por_cat, "n_treino": len(X_tr_txt), "n_teste": len(X_te_txt)},
          open(REL / "metricas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nfeito em {time.time()-t0:.0f}s. Relatorios em {REL}")
