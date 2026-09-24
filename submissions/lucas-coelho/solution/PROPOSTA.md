# Proposta de automação (Dataset 2: IT Service Ticket Classification)

Base da proposta: 47.837 tickets reais de TI com texto e categoria (8 categorias). Tudo abaixo vem de um conjunto de
**teste de 9.565 tickets que o modelo nunca viu**. Reprodução: `prototipo/treinar_e_avaliar.py`, `prototipo/simular_fila.py`.

## O que automatizar: triagem e roteamento com regra de parada

**O que o protótipo faz:** lê o texto do ticket, devolve a categoria, a confiança e uma decisão (roteia sozinho ou
manda para humano). Modelo: TF-IDF + regressão logística.

| Medida | Valor |
|---|---|
| Chutar sempre a categoria mais comum (linha de base) | 28,5% de acerto |
| Modelo, todos os tickets | **86,5%** de acerto, F1-macro 0,867 |
| Modelo, só tickets sem quase-duplicata no treino | 85,9% (a quase-duplicata infla só ~0,6 ponto) |

**A decisão importante não é o modelo, é onde parar.** Quanto mais eu deixo a IA rotear sozinha, mais erro aceito:

| Limiar de confiança | % roteado sozinho | Acerto no que roteia |
|---|---|---|
| 0,50 | 93,6% | 89,2% |
| 0,70 | 80,2% | 93,6% |
| **0,90** | 61,3% | 97,3% |
| 0,95 | 51,5% | 98,5% |

**Política proposta** (`prototipo/politica.py`): limiar 0,90 **e** duas categorias que nunca são roteadas sozinhas.
Resultado na fila simulada: **51,8% dos tickets roteados sem humano, com 97,4% de acerto (130 mal roteados em 4.956)**.
Os outros 48,2% vão para um humano, que recebe a categoria sugerida (o modelo acerta 74,9% nesses casos, então a
sugestão ainda encurta o trabalho).

## O que NÃO automatizar (e por quê)

1. **Administrative rights** (permissões). O modelo só recupera 71% dos casos (21% caem em Hardware) e o assunto é
   acesso, onde erro tem custo de segurança. Mesmo com confiança alta, vai para humano. Só 4,3% dessa categoria passa.
2. **Miscellaneous**. É a caixa de "não sei". Rotear sozinho para um balde sem dono não ajuda ninguém. 1,9% passa.
3. **Qualquer ticket abaixo do limiar.** Exemplo real do protótipo: "hi please help" recebe 80% de confiança em HR
   Support. Um texto sem informação nunca deveria ser roteado; o limiar é o que protege disso.
4. **Regra de negócio, fora do modelo:** ticket que envolva dinheiro, identidade do cliente ou risco legal nunca é
   fechado pela IA, mesmo que a classificação esteja certa. Isso é julgamento humano sobre consequência, não resultado
   estatístico. (Ver "Contexto de operação" no README.)

## Como funcionaria na prática

1. **Ticket entra** (e-mail, chat, telefone transcrito, rede social).
2. **Texto é normalizado** do mesmo jeito do treino (o dataset vem em minúsculas e sem palavras vazias).
3. **IA classifica** e devolve categoria + confiança + top 3.
4. **Política decide:** roteia para a fila da categoria, ou manda para a fila de triagem humana com top 3 e confiança.
5. **Humano corrige a categoria com um clique** quando errar. Cada correção vira dado de treino.
6. **Controle de qualidade:** auditoria semanal de uma amostra do que foi roteado sozinho (a única forma honesta de
   saber o acerto real em produção), reabertura por roteamento errado como métrica de alarme, e reajuste do limiar.
7. **Re-treino mensal** com as correções, e alerta se a mistura de categorias mudar (deriva).

## Economia: premissas, não medição

Volume de 30.000 tickets/ano (premissa do enunciado). O tempo de triagem manual por ticket **não existe nos dados**,
então mostro 3 cenários. Cada erro de roteamento custa 10 min de retrabalho (premissa).

| Triagem manual por ticket | Horas poupadas/ano | Retrabalho dos erros | **Líquido** |
|---|---|---|---|
| 1 min | 259 h | 68 h | **191 h (~1,2 mês de 1 pessoa)** |
| 2 min | 518 h | 68 h | **450 h (~2,8 meses)** |
| 3 min | 777 h | 68 h | **709 h (~4,4 meses)** |

Leitura honesta: o ganho é **moderado**, não transformacional, porque triagem é uma fração pequena do tempo de um
ticket. O maior valor provável não é a hora poupada, é o ticket certo chegar na fila certa mais rápido. Isso não dá
para medir aqui. Outra conta: enquanto o erro de roteamento for menor que `tempo de triagem / 10 min` (20% para 2
min), automatizar mais rende hora. O motivo de manter o limiar em 0,90 é **confiança e experiência do cliente**, não economia.

## Fases seguintes, só depois de medir

- **Resposta sugerida** para categorias com resposta padronizada: não avaliei porque o Dataset 1 (o único com
  resoluções) tem descrições geradas por template e o Dataset 2 não traz resolução. Só faz sentido testar com
  resoluções reais da operação.
- **Prioridade automática:** o Dataset 1 não sustenta nenhuma conclusão sobre prioridade (o texto prevê prioridade a
  25,2%, o acaso). Proposta: só depois de ter prioridade real e rotulada.
- **Detecção de duplicatas:** o Dataset 2 tem 0 textos idênticos, então não há o que medir.

## Limitações que eu não escondo

- O teste é dentro da mesma distribuição do treino. **Em produção o acerto cai** se os textos forem diferentes.
  O dataset é pré-processado (minúsculas, sem palavras vazias); textos crus exigiriam a mesma normalização.
- O modelo é **excessivamente confiante em texto fora do estilo do treino**: "please install visual studio license on
  my laptop urgent" deu 100% de confiança. A calibração só foi validada dentro da distribuição. Por isso proponho auditoria semanal.
- Os rótulos do Dataset 2 têm ruído aparente (ex.: "Outlook not starting" aparece como "Administrative rights"). O teto
  de acerto (~87%) provavelmente é o teto do rótulo, não do modelo.
- Não testei modelos de linguagem (embeddings ou zero-shot com LLM). É uma comparação natural e está fora desta entrega.
- A economia usa tempos assumidos. É o número que mais precisa ser trocado por medição.
