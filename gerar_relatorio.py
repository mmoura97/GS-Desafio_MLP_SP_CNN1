"""Gera relatório PDF com exatamente 10 slides a partir das métricas reais."""
from pathlib import Path
import json,pickle
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle
ROOT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/truetype/dejavu/'
if Path(FONT+'DejaVuSans.ttf').exists():
    pdfmetrics.registerFont(TTFont('Body',FONT+'DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('Bold',FONT+'DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold')
else:
    raise RuntimeError('Instale as fontes DejaVu Sans para gerar o relatório com este layout.')
NAVY=HexColor('#142d3d');TEAL=HexColor('#137b80');PAPER=HexColor('#f5f3ec');INK=HexColor('#243d49');MUTED=HexColor('#64747c');GOLD=HexColor('#df9a54');LINE=HexColor('#d9dfd9')
W,H=960,540
r=json.loads((ROOT/'artifacts/resultados.json').read_text());p=json.loads((ROOT/'data/proveniencia.json').read_text())
out=ROOT/'relatorio/relatorio_10_slides.pdf';out.parent.mkdir(exist_ok=True)
c=canvas.Canvas(str(out),pagesize=(W,H));c.setTitle('Ocorrências SP | Global Solution | Relatório técnico');c.setAuthor('Matheus Moura da Silva - RM 566782 - 2CCPR')

def txt(text,x,y,width=860,size=16,color=INK,bold=False,leading=None):
    style=ParagraphStyle('p',fontName='Bold' if bold else 'Body',fontSize=size,leading=leading or size*1.4,textColor=color)
    par=Paragraph(text,style);_,h=par.wrap(width,H)
    assert y < 40 or y-h>=43, f'Texto fora do slide: {text[:60]} em {y-h}'
    par.drawOn(c,x,y-h);return y-h

def box(x,y,w,h,fill=white,stroke=None):
    c.setFillColor(fill);c.setStrokeColor(stroke or fill);c.roundRect(x,y,w,h,12,fill=1,stroke=bool(stroke))

def start(n,kicker,title,subtitle=None,dark=False):
    bg=NAVY if dark else PAPER;c.setFillColor(bg);c.rect(0,0,W,H,fill=1,stroke=0)
    txt('OCORRÊNCIAS<span color="#80d5c6">SP.</span>',46,510,300,12,white if dark else TEAL,True)
    txt(kicker.upper(),46,468,860,11,HexColor('#80d5c6') if dark else TEAL,True)
    txt(title,46,439,865,28,white if dark else NAVY,True,leading=34)
    if subtitle:txt(subtitle,46,391,865,12,HexColor('#c7d5da') if dark else MUTED)
    c.setStrokeColor(HexColor('#3b5665') if dark else LINE);c.line(46,39,914,39)
    txt('GLOBAL SOLUTION  |  MLP TABULAR  |  DADOS HISTÓRICOS DE 2016',46,29,760,8,HexColor('#b7c7cd') if dark else MUTED)
    txt(f'{n:02d} / 10',855,29,70,9,HexColor('#b7c7cd') if dark else MUTED)

def bullets(items,x=46,y=365,w=865,size=16,gap=17):
    for t in items:
        c.setFillColor(TEAL);c.circle(x+3,y-9,3,fill=1,stroke=0)
        y=txt(t,x+20,y,w-20,size)-gap
    return y

def table(data,x,y,widths,size=13):
    style=ParagraphStyle('cell',fontName='Body',fontSize=size,leading=size*1.35,textColor=INK)
    rows=[[Paragraph(str(v),style) for v in row] for row in data]
    t=Table(rows,colWidths=widths);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#deebe6')),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#eceee8')]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),13),('BOTTOMPADDING',(0,0),(-1,-1),13),('LEFTPADDING',(0,0),(-1,-1),12),('LINEBELOW',(0,0),(-1,0),1,TEAL)]));_,h=t.wrap(870,450);assert y-h>43;t.drawOn(c,x,y-h);return y-h

def end():c.showPage()

def pct(v):return f'{100*v:.2f}%'.replace('.',',')

# 1
start(1,'Projeto e objetivo','Classificar registros.<br/>Compreender os limites.',dark=True)
txt('Segurança pública inteligente em São Paulo',46,330,860,22,white)
txt('Uma MLP para distinguir <b>roubo</b> e <b>furto simples</b> em ocorrências já registradas ou hipotéticas na capital.',46,280,790,20,HexColor('#d8e5e7'))
for x,n,label in [(46,'20.000','BOs na amostra'),(340,'3','arquiteturas testadas'),(634,'62,77%','acurácia no teste')]:
    txt(n,x,181,260,30,HexColor('#80d5c6'),True);txt(label,x,135,260,12,HexColor('#c7d5da'))
txt('Matheus Moura da Silva  |  RM 566782  |  Turma 2CCPR',46,81,865,12,white)
end()
# 2
start(2,'Problema, fonte e seleção','Dados reais, recorte explícito.','Objetivo: classificar a natureza do registro; não estimar a chance de acontecer um crime.')
bullets([
'<b>Fonte:</b> espelho histórico nublia/data-science-playground, atribuído à SSP-SP e distribuído via data.world. Registros de 2016; acesso em 10/11/2026.',
'<b>Capital:</b> departamento da circunscrição do fato = DECAP e CIDADE = S.PAULO. A delegacia de registro não define o local do crime.',
'<b>Seleção:</b> roubo ou furto simples consumado; exclusão de BOs com rubricas ou dados conflitantes; deduplicação por ano + delegacia + número.',
'<b>Volume:</b> 770.371 linhas de origem → 404.108 BOs elegíveis → amostra estratificada de 20.000 (10.016 furtos / 9.984 roubos).',
'<b>Entradas:</b> distrito do fato e mês de registro, escolhidos pela disponibilidade e pelo contexto territorial/temporal. Sem dados pessoais ou campos jurídicos.'
],size=14.5,gap=12)
txt('<link href="https://github.com/nublia/data-science-playground">Espelho e documentação</link>  |  <link href="https://www.ssp.sp.gov.br/estatistica/consultas">Portal oficial SSP-SP</link>  |  Hash SHA-256 e etapas no notebook.',46,77,865,10,TEAL)
end()
# 3
start(3,'Preparação dos dados','Separar antes de aprender.')
table([['Entrada','Tratamento','Justificativa'],['Distrito do fato','One-hot: 93 categorias','Contexto local sem ordem artificial'],['Mês de registro','One-hot: 12 categorias','A data/hora do fato não existe no CSV limpo'],['Rubrica','Somente alvo: 0 furto / 1 roubo','Excluída das entradas para evitar vazamento'] ],46,373,[220,260,388],12)
bullets(['Textos normalizados; ausência de distrito receberia “NAO INFORMADO”. A amostra final não tem ausências nas entradas. Sem variáveis contínuas: não se aplica escalonamento.',
'Encoder ajustado apenas no treino. BOs únicos e conjuntos disjuntos: <b>14.000 treino / 3.000 validação / 3.000 teste</b>; estratificação e semente 42.'],y=166,size=13.5,gap=12)
end()
# 4
start(4,'Arquitetura e funcionamento','A MLP selecionada tem 1.713 parâmetros.','Rede A: 105 entradas → 16 neurônios ReLU → 1 saída sigmoid.')
for x,w,title,body in [(46,260,'105 entradas','93 distritos + 12 meses\nOne-hot com valores 0/1'),(350,260,'16 neurônios','Camada densa\nh = ReLU(XW + b)'),(654,260,'1 saída','p(roubo) = sigmoid(hW + b)\np(furto) = 1 - p(roubo)')]:
    box(x,216,w,136);txt(title,x+20,333,w-40,21,TEAL,True);txt(body.replace('\n','<br/>'),x+20,288,w-40,14)
for x in [319,623]:txt('→',x,285,30,24,TEAL,True)
bullets(['Camadas densas combinam todas as entradas por pesos e vieses. ReLU permite relações não lineares; sigmoid produz a saída binária.',
'Limiar fixo: p(roubo) ≥ 0,5 → roubo; caso contrário → furto. Os percentuais não tiveram calibração validada.',
'Implementação real com MLPClassifier (scikit-learn). O enunciado pede MLP tabular; não exige uma CNN.'],y=184,size=14,gap=12)
end()
# 5
start(5,'Configuração do treinamento','Treino controlado pela validação.')
table([['Componente','Configuração adotada'],['Perda / saída','Entropia cruzada binária + L2 nos pesos; sigmoid'],['Otimizador','Adam; beta1 = 0,9; beta2 = 0,999; epsilon = 1e-8'],['Taxa de aprendizado','A e B: 0,001; C: 0,0005'],['Épocas / lotes','Máximo 100 épocas; batch size 128; embaralhamento; semente 42'],['Parada e seleção','F1 macro na validação; paciência 12; melhoria mínima 0,0001'],['Pesos entregues','Rede A, época 6; parada após 18 épocas; limiar 0,5'] ],46,374,[220,648],12)
txt('partial_fit preserva o estado de Adam. Os pesos escolhidos são restaurados; o teste não define arquitetura ou época.',46,73,865,11,MUTED)
end()
# 6
start(6,'Experimentação','Mais camadas não trouxeram ganho.')
table([['Modelo','Ocultas / parâmetros','L2 alpha / taxa','Hipótese testada'],['A · compacta','16 / 1.713','0,0001 / 0,001','Referência de baixa capacidade'],['B · intermediária','64 → 32 / 8.897','0,0001 / 0,001','Maior capacidade e profundidade'],['C · regularizada','128 → 64 → 32 / 23.937','0,01 / 0,0005','Profundidade com L2 mais forte e passos menores'] ],46,373,[140,228,180,320],12)
bullets(['Mesmo recorte, divisão e encoder para os três experimentos. Melhor época: A = 6; B = 3; C = 3.',
'B e C ficaram abaixo de A no F1 macro de validação. A diferença é pequena; uma semente não comprova superioridade estatística.',
'C muda vários fatores simultaneamente: não é possível atribuir seu resultado apenas à regularização.'],y=171,size=14,gap=12)
end()
# 7
start(7,'Avaliação e escolha','A vence na validação; teste fica reservado.','Precision, recall e F1 usam roubo como classe positiva. F1 macro considera ambas as classes.')
rows=[['Conjunto / modelo','Acurácia','Precision','Recall','F1 roubo','F1 macro']]
for a in r['arquiteturas']:rows.append(['Validação · '+a['nome'].split(' •')[0]]+[pct(a[k]) for k in ['acuracia','precision','recall','f1','f1_macro']])
rows.append(['Teste final · A']+[pct(r['teste'][k]) for k in ['acuracia','precision','recall','f1','f1_macro']])
table(rows,46,357,[218,130,130,130,130,130],11.5)
bullets(['Seleção por <b>F1 macro de validação = 63,16%</b>. Arquitetura, pesos e limiar congelados antes do teste.',
'Baseline majoritária no teste: 50,10% de acurácia e 33,38% de F1 macro. Ganho de acurácia da rede: <b>12,67 pontos percentuais</b>.'],y=134,size=14,gap=12)
end()
# 8
start(8,'Curvas, matriz e diagnóstico','Overfitting leve após a melhor época.')
c.drawImage(str(ROOT/'artifacts/curvas.png'),46,205,width=566,height=190,mask='auto')
c.drawImage(str(ROOT/'artifacts/matriz.png'),628,180,width=286,height=218,mask='auto')
bullets(['Época 6: acurácia treino/validação = 63,01% / 63,20%; perda = 0,6439 / 0,6507. As curvas mostram entropia cruzada sem o termo L2.',
'A perda de treino segue caindo e a de validação sobe levemente. Early stopping restaura a época 6. A baixa informação das entradas também limita o desempenho.',
'Teste: 898 furtos e 985 roubos corretos; 605 furtos confundidos com roubo e 512 roubos com furto. São <b>1.117 erros em 3.000 casos</b>.'],y=174,size=12.5,gap=8)
end()
# 9: captura real da página inicial publicada e testes observados no navegador
start(9,'Aplicação web','Acesso público e formulário testado.','Página inicial do site publicado. Testes de interação realizados no navegador, sem autenticação.')
c.drawImage(str(ROOT/'relatorio/interface_publica.png'),46,88,width=448,height=280,mask='auto')
box(516,182,398,183,white)
txt('TESTES REALIZADOS',534,345,362,12,TEAL,True)
txt('Distrito vazio: classificação impedida.<br/><b>Sé / Janeiro</b><br/>Furto 68,6% | Roubo 31,4%<br/><b>Capão Redondo / Dezembro</b><br/>Roubo 66,0% | Furto 34,0%',534,316,362,12)
txt('Categorias one-hot e pesos em JSON; ReLU e sigmoid calculadas no navegador. Paridade Python/JavaScript em 200 casos: erro máximo de 1,11 × 10⁻¹⁶.',516,163,398,11)
txt('<link href="https://ocorrencias-sp-mlp-lab.awakegerbil3.chatgpt.site/">Abrir aplicação pública - não exige login</link> · Percentuais classificam um registro; não medem risco de acontecer um crime.',46,77,865,11,TEAL)
end()
# 10
start(10,'Conclusões, limites e IA','Um experimento reproduzível, com alcance limitado.')
bullets([
'<b>Resultado:</b> três MLPs treinadas, comparação em validação e teste final reservado. A rede compacta foi a melhor neste recorte; acurácia de 62,77% no teste.',
'<b>Limitações:</b> dados secundários de 2016, duas entradas, subnotificação, chave de deduplicação operacional e uma única semente. Sem validação temporal ou calibração.',
'<b>Interpretação:</b> o modelo aprende padrões contextuais, não o critério jurídico de violência/ameaça. Não usar para decisões policiais ou estimar risco de vitimização.',
'<b>IA generativa:</b> ChatGPT apoiou programação, depuração, documentação e relatório. Métricas e curvas foram calculadas em execução real; a equipe deve revisar e compreender o código.',
'<b>Antes da entrega:</b> enviar o projeto ao GitHub e entregar os materiais pelo portal da faculdade. A aplicação pública já foi testada no navegador.'
],size=14,gap=12)
txt('Próximos experimentos: fonte oficial recente, dicionário auditado, mais variáveis do fato, múltiplas sementes e validação temporal.',46,76,865,10.5,TEAL)
end()
c.save();print(out)
