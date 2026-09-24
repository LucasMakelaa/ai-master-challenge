# Process log: G4 AI Master Challenge 002

Regra deste arquivo: registrar o que aconteceu de verdade, com data e hora do relógio do computador, inclusive
erros. Nada reescrito depois para ficar bonito. Ferramenta de IA: Claude Code (Claude Sonnet 5), sessão do Lucas.
Quem fez o quê: o Lucas delegou a execução técnica e baixou os datasets (exigem login dele); a IA leu, analisou,
codificou e escreveu; as decisões de negócio da proposta foram **propostas pela IA e ainda precisam da validação do Lucas**.

## 24/09/2026

**~16h20, escolha do desafio.** O Lucas se candidatou à vaga G4 Ai Master e disse que "o case já tinha chegado".
Conferi: o e-mail de confirmação não trazia case e o portal mostrava o status "Hunting" sem atualização. Procurei no
GitHub e achei que o desafio é público (AI Master Challenge, 4 opções). **Erro de premissa do Lucas, corrigido antes
de agir, em vez de inventar um case.**

**Decomposição.** Li o README geral, o do Challenge 002, o guia de submissão, o template e o CONTRIBUTING. O que
decide o trabalho: a G4 compara a entrega com um baseline de vários modelos (colar o enunciado numa IA não basta),
sem process log é desclassificado, e o envio é por Pull Request.

**Decisão do desafio: 002.** Motivo: é onde o Lucas tem contexto real de operação (CS em escala no iGaming). Os
outros três (churn, lead scorer, social media) não usam essa vantagem. Proposto pela IA; o Lucas seguiu baixando os
datasets do 002.

**Hipótese registrada ANTES de ver os dados:** o Dataset 1 pode ser sintético e não ter relação real entre tempo de
resposta, resolução e nota. Não verificado nesse momento.

**~17h16, dados baixados.** O Lucas baixou os dois zips do Kaggle (Downloads). Conferi o conteúdo antes de extrair
(nomes e tamanhos batem com os datasets certos) e copiei para `dados/`.

**Erro 1, do enunciado repetido pela IA:** o plano dizia "~30.000 registros". O arquivo do Dataset 1 tem **8.469**.
Corrigi no plano ao ver `shape`. Lição: conferir o dado antes de repetir o enunciado.

**Passo 1, exploração (`01_explorar.py`).** Tipo, prioridade, canal e nota quase perfeitamente uniformes; as colunas
de "tempo" são timestamps de 3 dias; 100% das descrições têm o marcador `{product_purchased}` sem preencher.
Tudo consistente com a hipótese, mas olhar não é provar.

**Erro 2, suposição sobre as colunas de tempo:** eu tinha planejado tratar "First Response Time" e "Time to
Resolution" como durações. Não são. Ao calcular a diferença entre as duas, 49,3% dos tickets fechados deram
resolução ANTES da primeira resposta. Isso desmente a suposição e vira um achado.

**Passo 2, testes (`02_testes_de_sinal.py`).** Qui-quadrado de uniformidade, Kruskal-Wallis, Spearman, ajuste de
Bonferroni, e classificação do texto pelo rótulo. Resultado: nenhum sinal (detalhes em `analise/02_resultado.txt` e
em `DIAGNOSTICO.md`). Hipótese confirmada por teste. Decisão: parar de tentar extrair diagnóstico do Dataset 1.

**Passo 3, Dataset 2 (`03_explorar_dataset2.py`).** 47.837 tickets, 8 categorias desbalanceadas (Hardware 28,5%,
Administrative rights 3,7%), 0 textos idênticos, rótulos com ruído visível (ex.: "Outlook not starting" como
"Administrative rights").

**Passo 4, classificador (`treinar_e_avaliar.py`), primeira execução.** Regressão logística e SVM empataram
(86,5%). Antes de confiar no número, chequei quase-duplicatas entre teste e treino (podem inflar acerto): 6,7% do teste
tem parecido ≥ 0,9, e o acerto sem esses é 85,9%. Só ~0,6 ponto de inflação.

**Passo 5, protótipo e política (`triar.py`, `politica.py`, `simular_fila.py`).** Escolhi limiar 0,90 e duas
categorias "sempre humano" (Administrative rights, Miscellaneous). Resultado na fila simulada: 51,8% automático a
97,4% de acerto.

**Erro 3, achado ao testar o protótipo:** o texto "please install visual studio license on my laptop urgent" saiu
com 100% de confiança. O modelo é excessivamente confiante em texto fora do estilo do treino (o dataset é
pré-processado). **Não corrigi**: registrei como limitação e como razão para auditoria semanal em produção.

**Limite de ferramenta.** A IA não baixa dataset (login), não cria conta e não abre o Pull Request (GitHub é do Lucas).

**Ainda em aberto:** a seção "O que eu adicionei que a IA sozinha não faria" depende de uma conversa com o Lucas
sobre a operação real de suporte dele. Não foi escrita pela IA de propósito.

## Contagem de iterações (honesta)

3 execuções de análise/modelo, 1 script por passo, nenhum refeito por erro de código. As correções foram de premissa
(volume do Dataset 1, natureza das colunas de tempo), não de sintaxe.

## 24/09/2026, noite: fork e envio dos arquivos para a branch

**~17h50, fork.** Com o Lucas logado no GitHub, criei o fork `LucasMakelaa/ai-master-challenge` do repositório
oficial `Gestao-Quatro-Ponto-Zero/ai-master-challenge` (autorizado por ele) e a branch `submission/lucas-coelho`.
Corrigi um erro de rota: a cópia que eu lia era o fork de outro candidato, não o repositório oficial.

**Erro 4, envio dos arquivos pela interface web:** 3 dos 5 commits não pegaram na primeira tentativa (cliquei em
"Commit changes" e naveguei antes de o GitHub processar). Refiz esperando e conferindo cada commit.

**Erro 5, quase abri um Pull Request sem querer:** um clique por coordenada marcou a opção "Create a new branch and
start a pull request" (o botão virou "Propose changes"). Percebi pela tela, **não confirmei**, voltei para "Commit
directly to the branch" e passei a validar o estado por script antes de cada commit. Nenhum PR foi aberto.
Resultado: 5 commits na branch, nenhum Pull Request.

**~19h, contribuição do Lucas (conversa de 3 perguntas).** Fraude era o assunto que tinha que ser manual; antes da
automatização o que mais consumia tempo era conferir todo saque acima de um valor de corte; erro de roteamento
aconteceu várias vezes (ramal errado, atendente entendendo errado a dúvida, aposta não paga transferida para o setor de
saque) e parou depois de organizarem o processo. Escrevi os dois blocos do README só com isso, sem acrescentar nada.
O número do valor de corte ficou fora do texto público de propósito.

**Pendente:** enviar o README e este log à branch, e o Pull Request, que só o Lucas autoriza.
