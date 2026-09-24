# Diagnóstico operacional (Dataset 1: Customer Support Ticket Dataset)

**Conclusão em uma frase:** esse dataset não permite um diagnóstico operacional. Ele parece gerado por sorteio,
e qualquer "gargalo" ou "driver de satisfação" que eu apresentasse seria ficção com aparência de análise.
O enunciado pede três respostas (onde trava, o que move satisfação, quanto se desperdiça). Abaixo está o que os dados
permitem afirmar, com teste, e o que não permitem.

Reprodução: `python analise/01_explorar.py dados` e `python analise/02_testes_de_sinal.py dados`.

## O que eu esperava e o que encontrei

O enunciado descreve ~30.000 registros. O arquivo tem **8.469**. Antes de qualquer conclusão, testei se os dados
têm estrutura de operação real.

| Verificação | Resultado | Leitura |
|---|---|---|
| Distribuição de tipo, prioridade, canal e status | Todas quase uniformes (maior/menor categoria ≤ 1,07). Qui-quadrado contra "todas iguais": p entre 0,12 e 0,72 | Compatível com sorteio uniforme. Suporte real tem canal e tipo muito concentrados |
| Nota de satisfação (2.769 fechados) | 1 a 5 com ~20% cada (p = 0,80 contra uniforme) | Idem |
| Colunas de "tempo" | São timestamps, não durações, todos em 3 dias (31/05 a 02/06/2023) | Não existe tempo de resolução medível |
| Resolução antes da 1ª resposta | **49,3%** dos 2.769 fechados (diferença de −23 h a +23 h) | Impossível em dado real (deveria ser ~0%) |
| Texto das descrições | **100%** (8.469) têm o marcador `{product_purchased}` sem preencher, com frases coladas sem relação | Texto gerado por template |
| O texto prevê o rótulo? (TF-IDF + regressão logística, 5 dobras) | Tipo: 18,9% (acaso: 20%). Prioridade: 25,2% (acaso: 25%). Canal: 26,3% (acaso: 25%) | O texto não carrega informação sobre o rótulo |

## O que move a satisfação?

Testei 8 candidatos entre os 2.769 tickets fechados (canal, prioridade, tipo, produto, gênero, duração,
hora da 1ª resposta, idade).

- **Nenhum** passa no ajuste de Bonferroni (limite p < 0,0063).
- O menor p foi 0,033 (hora da 1ª resposta, ρ = −0,04). Com 8 testes, o esperado por puro acaso é ~0,4 resultado
  "significativo". É exatamente o que apareceu.
- Com n = 2.769, qualquer correlação maior que ~0,05 teria sido detectada (poder de 80%). Ou seja: não é falta de
  amostra. Se existe efeito, é menor que 0,05, sem valor prático.
- A duração não depende de canal (p = 0,46), prioridade (p = 0,64) nem tipo (p = 0,92). As medianas chegam a ser negativas.

## Onde o fluxo trava? Quanto se desperdiça?

**Não dá para responder com este dataset.** As categorias são uniformes e o tempo não mede tempo. Dizer "o canal
telefone é o gargalo" seria escolher o maior de 4 números que variam por acaso.

A única coisa quantificável é a estrutura: 32,7% dos tickets estão fechados, 33,3% abertos e 34,0% aguardando o
cliente. Como o status também é uniforme (p = 0,33), eu não atribuo isso a nenhuma causa operacional.

## O que eu entrego no lugar

1. **A auditoria acima**, que é reaproveitável: os dois scripts rodam sobre qualquer exportação real de tickets e
   respondem "há sinal aqui ou é ruído?" antes de alguém tomar decisão.
2. **O que um diagnóstico real precisaria medir**, com as colunas certas:
   - Tempo de 1ª resposta e de resolução como **duração** (abertura → evento), separando horário comercial, e
     medindo pela **mediana e p90**, não pela média (a cauda longa é onde o cliente sofre).
   - Reabertura e "ping-pong" entre filas (ticket que muda de mãos mais de 2 vezes).
   - Satisfação contra tempo de resposta **dentro de cada tipo de problema**, para não confundir tipo difícil com
     atendimento lento.
   - Custo: minutos de trabalho humano por ticket por tipo, medido por amostra cronometrada (não estimado).
3. **A parte que os dados sustentam:** o Dataset 2 (48 mil textos reais de TI), onde há sinal de verdade. Ver `PROPOSTA.md`.

## Por que não usei o cruzamento dos dois datasets

O enunciado sugere que "o poder está no cruzamento". Cruzar exigiria que o texto do Dataset 1 refletisse o
problema do cliente. Ele não reflete (acurácia de 18,9% para 5 classes, abaixo do acaso). Treinar ou avaliar um
modelo com esse texto seria dar aparência de resultado a ruído. Prefiro usar cada dataset para o que ele sustenta:
o 1 para auditar, o 2 para construir.
