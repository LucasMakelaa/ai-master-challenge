"""Passo 1: qualidade e estrutura dos dados, antes de qualquer conclusao."""
import sys
import pandas as pd

D = sys.argv[1]
a = pd.read_csv(D + "/customer_support_tickets.csv")

print("LINHAS:", len(a))
print("\nNULOS por coluna:")
print(a.isna().sum().to_string())

print("\nStatus:")
print(a["Ticket Status"].value_counts(dropna=False).to_string())

for c in ["Ticket Type", "Ticket Priority", "Ticket Channel"]:
    print(f"\n{c}:")
    print(a[c].value_counts(dropna=False).to_string())

print("\nSatisfacao (nota):")
print(a["Customer Satisfaction Rating"].value_counts(dropna=False).sort_index().to_string())

print("\nAmostra das colunas de tempo (como vem no arquivo):")
print(a[["Date of Purchase", "First Response Time", "Time to Resolution"]].head(5).to_string())

print("\nTEXTO: descricoes unicas vs total:")
print("descricoes:", len(a), "| unicas:", a["Ticket Description"].nunique())
print("assuntos unicos:", a["Ticket Subject"].nunique())
print("resolucoes unicas:", a["Resolution"].nunique(), "(de", a["Resolution"].notna().sum(), "preenchidas)")
print("\n3 descricoes de exemplo:")
for t in a["Ticket Description"].head(3):
    print("-", t[:230].replace("\n", " "))
print("\nClientes: nomes unicos", a["Customer Name"].nunique(), "| e-mails unicos", a["Customer Email"].nunique())
print("Produtos:", a["Product Purchased"].nunique())
