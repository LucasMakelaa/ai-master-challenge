# Como rodar

Dados (licença CC0, exigem login no Kaggle, por isso não estão no repositório):
- https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset  -> `customer_support_tickets.csv`
- https://www.kaggle.com/datasets/adisongoh/it-service-ticket-classification-dataset -> `all_tickets_processed_improved_v3.csv`

Coloque os dois CSVs numa pasta `dados/` ao lado de `analise/` e `prototipo/`.

```
pip install -r requirements.txt
python analise/01_explorar.py dados             # qualidade do Dataset 1
python analise/02_testes_de_sinal.py dados      # ha sinal ou e sorteio?
python analise/03_explorar_dataset2.py dados    # qualidade do Dataset 2
cd prototipo
python treinar_e_avaliar.py ../dados            # treina, avalia, salva modelo e graficos
python simular_fila.py ../dados                 # fila simulada + economia (premissas)
python triar.py "texto de um ticket"            # protótipo: categoria + confianca + decisao
```
O modelo treinado (`prototipo/modelo/triagem.joblib`) não vai no repositório; o passo de treino o recria em ~1 minuto.
Testado em Python 3.14.
