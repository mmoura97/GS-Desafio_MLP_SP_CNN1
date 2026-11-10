"""Três MLPs, seleção em validação externa e uma avaliação final em teste."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import copy,json,pickle,time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,log_loss,confusion_matrix,classification_report
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parent
FEATURES=['distrito','mes_registro']
CONFIGS=[dict(nome='A • compacta',hidden=(16,),alpha=0.0001,lr=0.001),dict(nome='B • intermediária',hidden=(64,32),alpha=0.0001,lr=0.001),dict(nome='C • regularizada',hidden=(128,64,32),alpha=0.01,lr=0.0005)]
def metricas(y,p):
    h=(np.asarray(p)>=0.5).astype(int)
    return dict(acuracia=accuracy_score(y,h),precision=precision_score(y,h,zero_division=0),recall=recall_score(y,h,zero_division=0),f1=f1_score(y,h,zero_division=0),f1_macro=f1_score(y,h,average='macro',zero_division=0),perda=log_loss(y,p,labels=[0,1]))
def executar():
    d=pd.read_csv(ROOT/'data/amostra.csv',dtype={'mes_registro':str})
    tr,rest=train_test_split(np.arange(len(d)),test_size=0.3,stratify=d.rotulo,random_state=42)
    va,te=train_test_split(rest,test_size=0.5,stratify=d.rotulo.iloc[rest],random_state=42)
    assert not(set(tr)&set(va) or set(tr)&set(te) or set(va)&set(te))
    assert d.bo_hash.is_unique
    enc=OneHotEncoder(handle_unknown='ignore',sparse_output=False,dtype=np.float64)
    Xtr=enc.fit_transform(d.iloc[tr][FEATURES]);Xva=enc.transform(d.iloc[va][FEATURES])
    ytr=d.rotulo.iloc[tr].to_numpy();yva=d.rotulo.iloc[va].to_numpy()
    results=[];models=[];histories=[]
    for cfg in CONFIGS:
        m=MLPClassifier(hidden_layer_sizes=cfg['hidden'],activation='relu',solver='adam',alpha=cfg['alpha'],batch_size=128,learning_rate_init=cfg['lr'],random_state=42,shuffle=True,max_iter=1,early_stopping=False)
        best=-1;wait=0;history=[];start=time.time()
        with threadpool_limits(limits=1):
            for epoch in range(1,101):
                m.partial_fit(Xtr,ytr,classes=np.array([0,1]))
                mt=metricas(ytr,m.predict_proba(Xtr)[:,1]);mv=metricas(yva,m.predict_proba(Xva)[:,1])
                history.append(dict(epoca=epoch,treino=mt,validacao=mv))
                if mv['f1_macro']>best+0.0001:
                    best=mv['f1_macro'];chosen=copy.deepcopy(m);best_epoch=epoch;wait=0
                else:wait+=1
                if wait>=12:break
        row=dict(nome=cfg['nome'],hidden=list(cfg['hidden']),alpha=cfg['alpha'],lr=cfg['lr'],epocas=len(history),melhor_epoca=best_epoch,parametros=sum(w.size for w in chosen.coefs_)+sum(b.size for b in chosen.intercepts_),segundos=round(time.time()-start,2),**metricas(yva,chosen.predict_proba(Xva)[:,1]))
        results.append(row);models.append(chosen);histories.append(history)
        print(json.dumps(row,ensure_ascii=False),flush=True)
    winner=max(range(3),key=lambda i:results[i]['f1_macro']);m=models[winner]
    # O teste é acessado só depois de congelar arquitetura, pesos e limiar.
    Xte=enc.transform(d.iloc[te][FEATURES]);yte=d.rotulo.iloc[te].to_numpy();p=m.predict_proba(Xte)[:,1]
    majority=int(pd.Series(ytr).mode().iloc[0]);base=metricas(yte,np.repeat(majority,len(yte)))
    info=dict(arquiteturas=results,vencedor=winner,nome=results[winner]['nome'],dimensao_entrada=Xtr.shape[1],divisao={'treino':len(tr),'validacao':len(va),'teste':len(te)},distribuicao={k:d.iloc[v].rotulo.value_counts().sort_index().to_dict() for k,v in [('treino',tr),('validacao',va),('teste',te)]},teste=metricas(yte,p),baseline_teste=base,matriz=confusion_matrix(yte,p>=0.5).tolist(),relatorio=classification_report(yte,p>=0.5,target_names=['Furto','Roubo'],output_dict=True,zero_division=0),historicos=histories)
    art=ROOT/'artifacts';art.mkdir(exist_ok=True)
    (art/'resultados.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
    pd.DataFrame(results).to_csv(art/'comparacao.csv',index=False)
    with open(art/'modelo.pkl','wb') as f:pickle.dump({'encoder':enc,'modelo':m,'features':FEATURES},f)
    splits=d[['bo_hash']].copy();splits['conjunto']='';
    for ids,name in [(tr,'treino'),(va,'validacao'),(te,'teste')]:splits.loc[ids,'conjunto']=name
    splits.to_csv(art/'divisao.csv',index=False)
    export=dict(features=FEATURES,categories=[list(x) for x in enc.categories_],weights=[x.tolist() for x in m.coefs_],biases=[x.tolist() for x in m.intercepts_],classes=['Furto','Roubo'],threshold=0.5,metadata={k:v for k,v in info.items() if k not in ['historicos','relatorio']})
    (ROOT/'dist/modelo.json').write_text(json.dumps(export,ensure_ascii=False))
    h=histories[winner];plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(11,3.7))
    for ax,key,title in [(axs[0],'acuracia','Acurácia'),(axs[1],'perda','Entropia cruzada')]:
        for part,label,color in [('treino','Treino','#146b82'),('validacao','Validação','#dd8942')]:ax.plot([x['epoca'] for x in h],[x[part][key] for x in h],label=label,color=color,lw=2)
        ax.axvline(results[winner]['melhor_epoca'],color='#909090',ls=':',label='Pesos escolhidos');ax.set(xlabel='Época',title=title);ax.legend(fontsize=8);ax.grid(alpha=.15)
    fig.tight_layout();fig.savefig(art/'curvas.png',dpi=180);plt.close(fig)
    cm=np.array(info['matriz']);fig,ax=plt.subplots(figsize=(4.6,3.5));ax.imshow(cm,cmap='Blues',vmin=0,vmax=cm.max())
    for i in range(2):
        for j in range(2):ax.text(j,i,str(cm[i,j]),ha='center',va='center',fontsize=20,color='white' if cm[i,j]>cm.max()*0.75 else '#172c40')
    ax.set(xticks=[0,1],xticklabels=['Furto','Roubo'],yticks=[0,1],yticklabels=['Furto','Roubo'],xlabel='Classe estimada',ylabel='Classe real',title='Matriz de confusão • teste final');fig.tight_layout();fig.savefig(art/'matriz.png',dpi=180);plt.close(fig)
    print('FINAL',json.dumps({k:info[k] for k in ['nome','dimensao_entrada','divisao','teste','baseline_teste','matriz']},ensure_ascii=False),flush=True)
    return info
if __name__=='__main__':executar()
