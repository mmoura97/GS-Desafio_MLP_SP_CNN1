# Global Solution | Classificação de ocorrências com MLP

Projeto de **Segurança Pública Inteligente em São Paulo**, desenvolvido para a disciplina **Aprendizado Profundo com Redes Neurais Convolucionais**.

| Aluno | RM | Turma |
|---|---|---|
| Matheus Moura da Silva | 566782 | 2CCPR |

Uma rede neural MLP classifica ocorrências já registradas ou hipotéticas da capital paulista como **furto simples** ou **roubo**. Foram treinadas e comparadas três arquiteturas com uma amostra real de **20.000 boletins de ocorrência** de 2016.

> A aplicação estima o **tipo de uma ocorrência**, considerando que ela aconteceu. Os percentuais apresentados não representam a chance de ocorrer um crime em determinado local ou mês.

## Acesso rápido para avaliação

| Entrega | Acesso |
|---|---|
| Aplicação web funcional | **[Abrir o classificador — acesso público, sem login](https://ocorrencias-sp-mlp-lab.awakegerbil3.chatgpt.site/)** |
| Notebook documentado e executado | [modelo_mlp_sp.ipynb](modelo_mlp_sp.ipynb) |
| Relatório técnico com 10 slides | [relatorio_10_slides.pdf](relatorio/relatorio_10_slides.pdf) |
| Código e materiais completos | [Repositório do projeto](https://github.com/mmoura97/GS-Desafio_MLP_SP_CNN1) |
| Resultados completos dos experimentos | [resultados.json](artifacts/resultados.json) |

**Para testar pelo navegador:** abra a aplicação, selecione o distrito policial do local do fato e o mês de registro do boletim, e clique em **Classificar ocorrência**. A interface exibe a classe estimada e os percentuais atribuídos a roubo e furto. A aplicação está hospedada separadamente do GitHub; não é necessário instalar o projeto para testá-la.

## 1. Dados, recorte e atributos

| Item | Definição adotada |
|---|---|
| Fonte institucional de referência | [Secretaria da Segurança Pública de São Paulo — consultas](https://www.ssp.sp.gov.br/estatistica/consultas) |
| Distribuição efetivamente utilizada | [Espelho histórico nublia/data-science-playground](https://github.com/nublia/data-science-playground) |
| Período e acesso | Registros de 2016; arquivo acessado em 10/11/2026 |
| Recorte geográfico | `NOME_DEPARTAMENTO_CIRC = DECAP`, corroborado por `CIDADE = S.PAULO` |
| Unidade de análise | BO único, identificado por ano, delegacia de registro e número do boletim |
| Variável-alvo | `Furto (art. 155)` = 0; `Roubo (art. 157)` = 1; somente consumados |
| Entradas da rede | Distrito policial **do fato** e mês **do registro** |
| Amostra | 20.000 BOs: 10.016 furtos e 9.984 roubos |

O arquivo é um **espelho histórico atribuído à SSP-SP e distribuído via data.world**, e não um download direto do portal atual. A base e o período foram escolhidos pela disponibilidade pública e pelo tamanho adequado ao experimento. O [notebook do distribuidor](https://github.com/nublia/data-science-playground/blob/master/nb/boletins_ocorrencia.ipynb) documenta seu contexto.

A circunscrição do fato fundamenta o recorte da capital. A delegacia que recebeu o boletim não é utilizada como localização do crime; o campo `CIDADE` isoladamente seria insuficiente pela descrição ambígua no dicionário secundário. O CSV limpo não contém data ou hora do fato, portanto o projeto usa explicitamente o **mês de registro**, sem criar dia da semana ou período do dia fictícios.

### Preparação e prevenção de vazamento

1. Normalização dos textos e exclusão de BOs com rubricas ou informações conflitantes.
2. Seleção de roubos e furtos simples consumados na capital; exclusão de outras naturezas, tentativas e atos infracionais.
3. Deduplicação por `(ANO_BO, ID_DELEGACIA, NUM_BO)` **antes** da amostragem e da divisão.
4. Amostragem estratificada proporcional, com semente 42.
5. Divisão estratificada: **14.000 treino / 3.000 validação / 3.000 teste**.
6. Codificação one-hot ajustada **somente no treino**: 93 distritos + 12 meses = 105 entradas.

Rubrica, desdobramentos, conduta e outros campos jurídicos não são entradas. Nomes, endereços e características pessoais também foram excluídos. Não há valores ausentes nas duas entradas da amostra final; o código prevê categorias de ausência. Como todos os atributos são categóricos codificados em 0/1, não há variável contínua a escalonar.

O arquivo original tem 770.371 linhas. Após os filtros e a deduplicação, há 404.108 BOs elegíveis, dos quais foram amostrados 20.000. As etapas, contagens e o SHA-256 do arquivo utilizado estão em [proveniencia.json](data/proveniencia.json). A amostra incluída é minimizada e contém somente hash técnico do BO, distrito, mês e rótulo.

## 2. Arquiteturas e treinamento

Implementação com `MLPClassifier` do scikit-learn: camadas densas, ativação **ReLU** nas ocultas e **sigmoid** na saída binária. Embora o nome da disciplina mencione CNN, o enunciado desta atividade pede uma **MLP para dados tabulares**.

| Modelo | Camadas ocultas | Parâmetros | Taxa de aprendizado | L2 alpha | Melhor época |
|---|---|---:|---:|---:|---:|
| **A — compacta** | 16 | 1.713 | 0,001 | 0,0001 | 6 |
| B — intermediária | 64 → 32 | 8.897 | 0,001 | 0,0001 | 3 |
| C — regularizada | 128 → 64 → 32 | 23.937 | 0,0005 | 0,01 | 3 |

- **Perda:** entropia cruzada binária com penalização L2 nos pesos.
- **Otimizador:** Adam; beta1 = 0,9; beta2 = 0,999; epsilon = 1e-8.
- **Batch size:** 128; máximo de 100 épocas; embaralhamento e semente 42.
- **Parada antecipada:** F1 macro na validação externa, paciência 12 e melhoria mínima de 0,0001.
- **Seleção:** melhores pesos restaurados; arquitetura e época escolhidas pela validação; limiar fixado em 0,5 antes do teste.

A rede A é a referência compacta; B testa maior capacidade; C testa mais profundidade com L2 mais forte e taxa menor. Como C altera vários fatores simultaneamente, seu resultado não permite isolar o efeito de cada alteração.

## 3. Resultados

### Comparação na validação

Precision, recall e F1 usam **roubo como classe positiva**. F1 macro é a média dos F1 das duas classes e foi o critério de seleção.

| Modelo | Acurácia | Precision | Recall | F1 de roubo | F1 macro |
|---|---:|---:|---:|---:|---:|
| **A** | **63,20%** | 62,28% | 66,69% | 64,41% | **63,16%** |
| B | 62,87% | 61,94% | 66,49% | 64,13% | 62,82% |
| C | 62,40% | 61,98% | 63,89% | 62,92% | 62,39% |

A arquitetura **A, com 16 neurônios ocultos**, foi selecionada pelo maior F1 macro de validação. O treinamento parou na época 18 e restaurou os pesos da época 6. As diferenças entre arquiteturas são pequenas e foram medidas com uma única semente; não demonstram superioridade estatística.

### Avaliação final no teste reservado

| Métrica | Modelo A |
|---|---:|
| Acurácia | **62,77%** |
| Precision de roubo | 61,95% |
| Recall de roubo | 65,80% |
| F1 de roubo | 63,82% |
| F1 macro | 62,74% |
| Acurácia da baseline majoritária, sempre furto | 50,10% |

O ganho de acurácia sobre a baseline foi de **12,67 pontos percentuais**. A arquitetura, os pesos e o limiar estavam congelados antes dessa avaliação; não houve novo ajuste com base no teste.

| Classe real | Estimado furto | Estimado roubo |
|---|---:|---:|
| Furto | 898 | 605 |
| Roubo | 512 | 985 |

Foram 1.117 erros em 3.000 casos. Na época escolhida, treino e validação tinham acurácias próximas, de 63,01% e 63,20%. Posteriormente, a perda de treino continuou caindo e a de validação aumentou levemente: sinal de overfitting leve, tratado pela restauração dos melhores pesos. O desempenho moderado também pode refletir baixa informação nos atributos; não comprova, sozinho, underfitting.

<details>
<summary><strong>Ver curvas e matriz de confusão</strong></summary>

As curvas mostram a entropia cruzada preditiva, sem o termo L2.

![Curvas de treinamento e validação](artifacts/curvas.png)

![Matriz de confusão no teste](artifacts/matriz.png)

</details>

## 4. Executar a aplicação localmente

Com **Python 3.12** instalado, abra o terminal na raiz deste repositório e execute:

```bash
python SERVIR_APP.py
```

Acesse **http://localhost:8000**. A aplicação já inclui o modelo treinado e o servidor usa somente a biblioteca padrão do Python. Sirva a pasta por HTTP; abrir o HTML diretamente por `file://` pode bloquear o carregamento do modelo.

O formulário recebe exatamente os dois atributos usados no treinamento. `dist/modelo.json` contém as categorias do encoder, matrizes de pesos e vieses; `dist/app.js` executa one-hot, camadas densas, ReLU e sigmoid no navegador. Os valores informados no formulário não são enviados a um servidor de inferência.

## 5. Reproduzir os experimentos

Crie um ambiente virtual na raiz do projeto:

```bash
python -m venv .venv
```

Ative-o com o comando correspondente ao seu sistema:

| Terminal | Comando |
|---|---|
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows Prompt de Comando | `.venv\Scripts\activate.bat` |
| Linux / macOS | `source .venv/bin/activate` |

Depois execute:

```bash
python -m pip install -r requirements.txt
python treinar.py
python verificar.py
jupyter lab modelo_mlp_sp.ipynb
```

O notebook já contém saídas e gráficos dos experimentos. Executar todas as células refaz o treinamento e sobrescreve os artefatos. A amostra minimizada está incluída, portanto não é necessário baixar novamente o arquivo original para reproduzir o treinamento. Pequenas diferenças numéricas podem ocorrer entre ambientes.

Para refazer também a aquisição e a preparação dos dados:

```bash
python preparar_dados.py
python treinar.py
python verificar.py
```

O download original tem aproximadamente 43 MB comprimidos. O script confere o SHA-256 e interrompe a preparação se o arquivo remoto tiver mudado. A fonte completa está registrada em [preparar_dados.py](preparar_dados.py) e [data/proveniencia.json](data/proveniencia.json).

## 6. Organização do repositório

| Arquivo ou pasta | Conteúdo |
|---|---|
| [modelo_mlp_sp.ipynb](modelo_mlp_sp.ipynb) | Notebook documentado e executado com as três MLPs |
| [preparar_dados.py](preparar_dados.py) | Aquisição, verificação do hash, filtros e amostragem |
| [treinar.py](treinar.py) | Treinamento, seleção, avaliação e exportação |
| [verificar.py](verificar.py) | Separação dos BOs e equivalência Python/JavaScript |
| [SERVIR_APP.py](SERVIR_APP.py) | Servidor local da aplicação |
| [requirements.txt](requirements.txt) | Dependências dos experimentos |
| [data/](data/) | Amostra real minimizada e procedência |
| [artifacts/](artifacts/) | Modelo treinado, encoder, métricas, gráficos e divisões |
| [dist/](dist/) | Interface web e pesos exportados para o navegador |
| [relatorio/](relatorio/) | Relatório PDF de 10 slides e captura da interface |
| [GUIA_DE_DEFESA.md](GUIA_DE_DEFESA.md) | Material de estudo para compreender e apresentar a solução |
| [gerar_relatorio.py](gerar_relatorio.py) | Código de geração do relatório a partir das métricas |
| [.github/workflows/pages.yml](.github/workflows/pages.yml) | Hospedagem alternativa opcional no GitHub Pages |

## 7. Verificações realizadas

- Unicidade dos 20.000 BOs e separação dos conjuntos de treino, validação e teste.
- Equivalência da inferência Python/JavaScript em 200 casos da validação, com diferença máxima de aproximadamente **1,11 × 10⁻¹⁶**.
- Abertura da aplicação pública no navegador desktop sem autenticação, em 10/11/2026.
- Validação do distrito obrigatório e classificação de dois exemplos: Sé/Janeiro e Capão Redondo/Dezembro.
- Relatório com exatamente 10 slides e revisão visual das páginas.

Registros disponíveis em [verificacao.json](artifacts/verificacao.json) e [teste_interface.json](artifacts/teste_interface.json). Não foi realizada uma bateria de testes em dispositivos móveis. O arquivo `artifacts/modelo.pkl` deve ser carregado somente de uma origem confiável, usando as versões de referência.

## 8. Limitações e uso responsável

A base é histórica, secundária e sujeita a subnotificação e diferenças nas práticas de registro. O hash identifica os bytes utilizados, mas não constitui auditoria de autenticidade de toda a cadeia de origem. A chave de deduplicação pode não identificar todos os vínculos entre boletins complementares, e o recorte exclui furtos qualificados e BOs com múltiplas rubricas.

Distrito e mês fornecem apenas contexto: não incluem a informação de violência ou grave ameaça que distingue juridicamente as classes. As probabilidades não tiveram calibração avaliada. Uma única amostra/semente e a divisão aleatória no mesmo período não medem generalização temporal ou a situação atual da cidade.

O sistema é acadêmico. Não deve orientar decisões policiais ou judiciais, avaliar pessoas ou representar risco de vitimização. Os dados de terceiros permanecem sujeitos aos termos de suas fontes.

## 9. Uso de IA generativa

ChatGPT apoiou a interpretação do enunciado, programação, depuração, documentação e relatório. Os três modelos foram efetivamente treinados, e tabelas e gráficos foram produzidos a partir das execuções. A responsabilidade pela revisão e compreensão da solução é do aluno.

## Referências técnicas

- [MLPClassifier — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html)
- [OneHotEncoder — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html)
- [Métricas de avaliação — scikit-learn](https://scikit-learn.org/stable/modules/model_evaluation.html)

Para regenerar o PDF, instale `requirements_relatorio.txt`, ajuste o caminho das fontes DejaVu Sans em `gerar_relatorio.py` conforme seu sistema e execute `python gerar_relatorio.py`.
