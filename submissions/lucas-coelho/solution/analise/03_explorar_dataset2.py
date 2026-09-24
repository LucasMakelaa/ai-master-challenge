"""Passo 3: Dataset 2 (48 mil tickets de TI com texto e categoria). Qualidade antes de modelar."""
import sys
import pandas as pd

D = sys.argv[1]
b = pd.read_csv(D + "/all_tickets_processed_improved_v3.csv")
print("LINHAS:", len(b), "| nulos:", b.isna().sum().to_dict())

print("\nCategorias (contagem e %):")
vc = b["Topic_group"].value_counts()
print(pd.DataFrame({"n": vc, "%": (vc / len(b) * 100).round(1)}).to_string())

b["doc"] = b["Document"].astype(str)
print("\nTextos vazios ou curtissimos (<3 palavras):", (b["doc"].str.split().str.len() < 3).sum())
b["palavras"] = b["doc"].str.split().str.len()
print("palavras por ticket: mediana", b["palavras"].median(), "| p90", b["palavras"].quantile(.9), "| max", b["palavras"].max())

dup = b.duplicated(subset=["doc"], keep=False)
print("\nTextos IDENTICOS repetidos:", dup.sum(), f"({dup.mean():.1%} das linhas) | textos unicos:", b['doc'].nunique())
# duplicados com categorias diferentes = ruido de rotulo
g = b[dup].groupby("doc")["Topic_group"].nunique()
print("Grupos de texto igual com categorias DIFERENTES (ruido de rotulo):", int((g > 1).sum()), "de", len(g), "grupos")

print("\n3 exemplos por categoria (primeiros 140 caracteres):")
for cat in vc.index:
    print(f"[{cat}]")
    for t in b[b["Topic_group"] == cat]["doc"].sample(2, random_state=1):
        print("   -", t[:140].replace("\n", " "))
