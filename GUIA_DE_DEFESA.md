# Guia de estudo e defesa

Este guia ajuda a equipe a compreender e revisar o trabalho. Leia também o notebook; não apresente a solução sem entender as limitações e as pendências de publicação.

## Qual problema o projeto resolve?

Dado um registro de ocorrência, classifica-o como furto simples ou roubo com base no distrito do fato e no mês de registro. Não prevê onde nem quando um crime ocorrerá. Não substitui o enquadramento jurídico, pois não recebe informação de violência ou grave ameaça.

## Por que uma MLP e não uma CNN?

O enunciado pede uma rede densa MLP para dados tabulares. CNNs são especialmente úteis quando há estrutura local, como em imagens. Aqui, a entrada é um vetor one-hot, sem organização espacial de pixels.

## De onde vêm os dados e por que 2016?

De um espelho público de microdados atribuídos à SSP-SP, no repositório nublia/data-science-playground. A disponibilidade do arquivo e seu tamanho permitiram uma experiência reprodutível. Não fizemos download direto do portal atual. Por serem dados antigos e tratados por terceiro, as conclusões são restritas a esse recorte. O SHA-256 permite identificar o arquivo usado, mas não prova sozinho a sua autenticidade.

## Como garantimos a capital e não São José dos Campos?

Filtramos o departamento de circunscrição do fato como DECAP e a cidade como S.PAULO. A delegacia que recebeu o boletim pode ser outra. O campo de circunscrição é o fundamento territorial; o campo CIDADE sozinho seria insuficiente pela ambiguidade do dicionário secundário.

## Por que não usamos dia da semana ou período?

O CSV limpo não contém a data ou hora do fato. Embora a documentação de origem mencione esses campos, eles não estão nos bytes disponíveis. Usamos o mês de registro e deixamos isso explícito; não inventamos informações.

## Como funcionam os 105 neurônios de entrada?

Existem 93 distritos e 12 meses no encoder ajustado no treino. Cada grupo vira um vetor one-hot: uma posição 1 indica a categoria escolhida, e as demais ficam 0. Isso evita atribuir uma ordem artificial aos distritos. Não há uma variável contínua que necessite de padronização.

## Como funciona uma camada densa?

Cada neurônio combina todas as entradas com pesos e um viés: z = soma(x_i × w_i) + b. Na camada oculta, ReLU devolve max(0,z), permitindo relações não lineares. A saída sigmoid transforma o valor final em um número entre 0 e 1 para roubo. A probabilidade de furto é o complemento.

## O que acontece no treinamento?

A rede calcula previsões, compara-as com os rótulos usando entropia cruzada e calcula gradientes por retropropagação. Adam atualiza os pesos em lotes de 128 exemplos, com taxas de aprendizado definidas por configuração. Cada chamada a partial_fit percorre uma época preservando o estado do otimizador.

## O que é vazamento de informação e como foi evitado?

É permitir que informação do alvo ou de dados reservados influencie o aprendizado. Rubrica, desdobramentos e campos jurídicos não entram no modelo. O encoder é ajustado só no treino. Duplicatas do mesmo BO são removidas antes da divisão, e o teste não escolhe arquitetura, época ou limiar.

## Por que três conjuntos?

Treino ajusta os pesos. Validação seleciona arquitetura e época. Teste mede uma vez a solução já congelada. Usar o teste várias vezes para decidir alterações contamina a estimativa de generalização. Nesta experiência não houve reentreino com treino+validação após a seleção.

## Por que escolher a rede A?

Seu F1 macro de validação foi 63,16%, superior a 62,82% de B e 62,39% de C. A rede A também é menor, com 1.713 parâmetros. A diferença é pequena e não foi validada em múltiplas sementes: não se deve afirmar superioridade universal ou estatística.

## O que são precision, recall e F1?

Usando roubo como classe positiva, precision mede a fração dos casos estimados como roubo que realmente são roubos. Recall mede a fração dos roubos reais que foram identificados. F1 equilibra as duas medidas pela média harmônica. F1 macro calcula o F1 de cada classe e faz a média, sem privilegiar a classe maior.

## Como explicar a matriz?

As linhas são as classes reais e as colunas, as estimadas. Foram 898 furtos e 985 roubos corretos. A rede confundiu 605 furtos com roubo e 512 roubos com furto. Portanto, errou 1.117 das 3.000 ocorrências do teste.

## O que as curvas mostram?

Na época 6, treino e validação têm acurácias próximas. Depois, a perda de treino continua caindo enquanto a validação piora levemente. Isso sugere overfitting leve, motivo para restaurar os pesos da época 6. O desempenho moderado também pode vir da baixa informação das variáveis; não prova sozinho underfitting.

## Por que a acurácia não é alta?

A natureza jurídica depende de aspectos como violência ou grave ameaça, não apenas de distrito e mês. Esses atributos trazem apenas padrões estatísticos de contexto. Melhorar o modelo exige dados adequados e confiáveis, não apenas adicionar camadas.

## O site usa uma rede de verdade?

Sim. O arquivo modelo.json contém as categorias e os pesos treinados. O JavaScript reproduz as operações densas, ReLU e sigmoid. Foram comparados 200 exemplos da validação com Python, com diferença máxima em torno de 10^-16. A revisão visual e interativa desktop também foi concluída: a página abriu sem login, validou distrito obrigatório e classificou dois exemplos, com atualização de classe e percentuais.

## Como interpretar um percentual?

“Considerando que uma ocorrência existe com esses atributos, o modelo atribui esse percentual à classe roubo.” Não diga que há esse percentual de chance de ocorrer um roubo no local. As probabilidades também não tiveram calibração avaliada.

## Como a IA foi usada?

ChatGPT apoiou leitura, programação, depuração e documentação. As métricas foram obtidas por execução real. A equipe precisa validar o material, conferir sua identificação e conseguir explicar o fluxo de dados, as redes e suas limitações.

## O que falta antes de entregar?

A identificação já está preenchida: Matheus Moura da Silva, RM 566782, turma 2CCPR. A aplicação já está pública e o slide 9 contém uma captura real. Falta o aluno enviar os arquivos à sua conta GitHub e realizar a entrega pelo portal da faculdade.
