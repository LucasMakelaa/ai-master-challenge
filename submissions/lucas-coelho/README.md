# Submissão: Lucas Pereira Coelho, Challenge 002 (Redesign de Suporte)

## Sobre mim

- **Nome:** Lucas Pereira Coelho
- **LinkedIn:** https://www.linkedin.com/in/lucas-p-coelho
- **Challenge escolhido:** 002, Redesign de Suporte (Operações / CX)

---

## Executive Summary

O Dataset 1 (métricas de tickets) **não sustenta diagnóstico**: as categorias são sorteio uniforme, os "tempos" são
timestamps de 3 dias em que 49,3% das resoluções acontecem antes da primeira resposta, e o texto não prevê nenhum
rótulo (18,9% contra 20% de acaso). Em vez de inventar gargalos, provo isso com testes e uso o Dataset 2 (48 mil
tickets reais de TI) para construir uma triagem automática. Ela roteia **51,8% dos tickets sem humano, com 97,4% de
acerto**, num conjunto de teste que o modelo nunca viu. A recomendação principal é automatizar a triagem com regra de
parada (limiar de confiança + categorias que nunca vão sozinhas) e trocar as premissas de economia por uma medição de
tempo real antes de qualquer promessa de ROI.

---

## Solução

Detalhes em `solution/`: [DIAGNOSTICO.md](solution/DIAGNOSTICO.md), [PROPOSTA.md](solution/PROPOSTA.md), código em
`solution/analise/` e `solution/prototipo/`, gráficos e métricas em `solution/prototipo/relatorios/`.

### Abordagem

1. Antes de modelar, **auditei os dois datasets**: o enunciado diz ~30.000 registros e o arquivo tem 8.469, o que já
   avisou que precisava conferir tudo.
2. Testei se o Dataset 1 tem sinal (qui-quadrado de uniformidade, Kruskal-Wallis, Spearman, ajuste de Bonferroni,
   classificação do texto pelo rótulo). Não tem.
3. Movi o esforço de construção para o Dataset 2, onde há sinal, e avaliei com conjunto de teste separado, checagem
   de quase-duplicatas e curva de confiança contra cobertura.
4. Defini a política de triagem como decisão de negócio (onde a IA para), não como saída do modelo.

### Resultados / Findings

- Dataset 1: nenhuma variável explica a satisfação (0 de 8 testes passam no Bonferroni; poder para detectar
  correlação de 0,05).
- Dataset 2: 86,5% de acerto (linha de base 28,5%; 85,9% sem quase-duplicatas), F1-macro 0,867.
- Política final: 51,8% automático a 97,4% de acerto; 48,2% para humano com sugestão (74,9% de acerto).
- Economia estimada: 191 a 709 h/ano líquidas conforme o tempo de triagem manual (**premissa**, não medição).
- Protótipo rodando: `python solution/prototipo/triar.py "texto do ticket"`.

### Recomendações

1. Implantar a triagem com limiar 0,90 e as categorias "Administrative rights" e "Miscellaneous" sempre para humano.
2. Auditar semanalmente uma amostra do que foi roteado sozinho, porque é a única medida honesta de acerto em produção.
3. Cronometrar uma amostra de tickets reais para substituir as premissas de tempo antes de apresentar ROI.
4. Só depois disso avaliar resposta sugerida e prioridade automática.

### Limitações

Acerto medido dentro da mesma distribuição do treino; modelo excessivamente confiante em texto fora do estilo do
treino; rótulos do Dataset 2 com ruído aparente; não testei LLM/embeddings; economia baseada em tempos assumidos.
Lista completa no fim de [PROPOSTA.md](solution/PROPOSTA.md).

### Contexto de operação (o que só quem operou suporte sabe)

Liderei Customer Success, Sportsbook e Risco de uma operação regulada de iGaming, com ~18.000 tickets/mês de CS por
chat e, depois da regulamentação, também por telefone. Criei NPS, SLA e taxa de resolução, que não existiam. O Risco
tinha equipe 24h/7 para KYC, fraude de pagamento, bonus abuse e surebet. Três coisas dessa operação moldaram a proposta:

**1. O que nunca podia ser automático: fraude.** Era o assunto mais delicado da triagem e tinha que ser manual. Não dava
para "robotizar". Por isso a minha política tem uma regra fora do modelo: ticket que envolva dinheiro, identidade ou
risco não é fechado pela IA, mesmo que a categoria esteja certa (ver `PROPOSTA.md`).

**2. O que mais consumia tempo antes da automatização: conferência de saques.** Todo saque acima de um valor de corte
precisava ser conferido por uma pessoa, um por um. Isso mostra o que os dados públicos não mostram: em operação de
dinheiro, o que decide se um ticket pode ser automatizado é o **valor envolvido**, não só a categoria do texto.

**3. Erro de roteamento acontecia, e era caro.** Várias vezes: a transferência ia para o ramal errado, ou o atendente
entendia errado a dúvida do cliente e transferia para o setor errado. Depois que organizamos o processo, isso parou. Um
exemplo típico: um caso de aposta não paga que foi parar no setor de saques. Assuntos vizinhos, com palavras parecidas,
que pertencem a filas diferentes. É o mesmo tipo de erro que o meu classificador comete entre categorias parecidas
(ver a matriz de confusão), e é o motivo de eu tratar o roteamento errado como métrica de alarme e de manter a
auditoria semanal. Não medi esse custo com dados, é experiência de operação, e digo isso de propósito.

---

## Process Log: Como usei IA

> Log completo e datado em [process-log/PROCESS_LOG.md](process-log/PROCESS_LOG.md).

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| Claude Code (Claude Sonnet 5) | Leitura do enunciado, análise exploratória, testes estatísticos, treino e avaliação do classificador, escrita dos documentos |
| Python (pandas, scipy, scikit-learn) | Execução dos testes e do modelo. A IA escreveu o código, eu não escrevo código à mão |

### Workflow

1. Li o enunciado com a IA. Ela propôs o desafio 002 e eu validei (é o único dos 4 onde tenho contexto de operação).
2. Antes de pedir análise, a IA registrou uma hipótese ("o Dataset 1 pode ser sintético") para comparar depois com os dados.
3. Baixei os datasets (exigem login) e conferi o que veio.
4. A IA explorou, testou e modelou em passos pequenos, cada um com script salvo e resultado salvo em `analise/`.
5. A IA propôs a política de triagem (limiar e categorias sempre humano). Eu defini, pela minha operação, o que nunca se automatiza.

### Onde a IA errou e como corrigi

Ver o log datado. Resumo: a IA repetiu do enunciado "~30.000 registros" e "colunas de tempo" antes de abrir os dados;
os dados desmentiram os dois. Também o protótipo devolveu 100% de confiança num texto fora do estilo do treino, o que
virou uma limitação registrada, não escondida.

### O que eu adicionei que a IA sozinha não faria

A IA escreveu o código e rodou os testes. O que veio de mim:

- **O limite do que não se automatiza.** Fraude, dinheiro e identidade ficam com humano. Isso vem de ter operado
  suporte e risco, não de uma métrica do dataset.
- **Onde estava o desperdício de verdade.** A conferência manual de saques acima de um valor de corte. Os dados
  públicos não têm esse tipo de informação. É o que eu testaria primeiro numa operação real: regra por valor, além da
  regra por categoria.
- **O custo do roteamento errado.** Sei por experiência que o erro entre setores vizinhos (aposta não paga que cai em
  saque) acontece e é complicado de desfazer. Isso sustenta o cuidado da proposta com a fila de humano e com a
  auditoria do que foi roteado sozinho.
- **Validação da direção.** A IA propôs o desafio 002 e o plano. Eu validei porque é o desafio em que a minha
  experiência de operação vale mais, e a IA não tem essa experiência.

O que **não** vem de mim: os números, os testes, o classificador e a leitura estatística dos dados. Isso é trabalho da
IA, conferido pelos resultados salvos em `solution/analise/`.

---

## Evidências

- [x] Git history (commits do código e dos resultados)
- [x] Chat export / narrativa datada (`process-log/PROCESS_LOG.md`)
- [ ] Screenshots das conversas com IA (a anexar)

_Submissão enviada em: 24/09/2026_
