"""Obtém e minimiza microdados públicos; não mantém endereços ou pessoas."""
from pathlib import Path
import hashlib, json, urllib.request
import pandas as pd
from sklearn.model_selection import train_test_split
ROOT=Path(__file__).resolve().parent
URL='https://raw.githubusercontent.com/nublia/data-science-playground/master/dat/boletins_ocorrencia_sp_clean_2016.csv.gz'
SHA='fcad92a9f348b59b9c7a5b195d1fb956f8fb75eb9a5e55f84665d0bb7c0de70d'

def preparar(arquivo=None):
    if arquivo is None:
        arquivo=ROOT/'data/original.csv.gz'
        urllib.request.urlretrieve(URL,arquivo)
    arquivo=Path(arquivo)
    digest=hashlib.sha256(arquivo.read_bytes()).hexdigest()
    if SHA and digest!=SHA: raise ValueError('A fonte mudou. Revise o recorte antes de continuar.')
    d=pd.read_csv(arquivo,encoding='latin1',low_memory=False)
    stats={'linhas_fonte':len(d),'sha256':digest,'url':URL,'acesso':'2026-11-10'}
    for c in d.select_dtypes('object'):d[c]=d[c].str.strip()
    key=['ANO_BO','ID_DELEGACIA','NUM_BO']
    # Avaliar o BO completo ANTES de filtrar rótulos ou amostrar.
    g=d.groupby(key,dropna=False)
    sizes=g[['RUBRICA','NOME_DELEGACIA_CIRC','MES','CIDADE','NOME_DEPARTAMENTO_CIRC']].nunique(dropna=False)
    bad=sizes.index[(sizes>1).any(axis=1)]
    idx=pd.MultiIndex.from_frame(d[key]);stats['linhas_BO_inconsistente']=int(idx.isin(bad).sum())
    d=d.loc[~idx.isin(bad)].copy()
    cap=d.NOME_DEPARTAMENTO_CIRC.eq('DECAP') & d.CIDADE.eq('S.PAULO')
    stats['linhas_capital_consistentes']=int(cap.sum())
    d=d.loc[cap & d.RUBRICA.isin(['Roubo (art. 157)','Furto (art. 155)']) & d.FLAG_STATUS.eq('C') & d.ANO.eq(2016)].copy()
    stats['linhas_elegiveis']=len(d)
    d=d.sort_values(key).drop_duplicates(key)
    stats['BOs_elegiveis']=len(d)
    d['rotulo']=d.RUBRICA.eq('Roubo (art. 157)').astype(int)
    d['distrito']=d.NOME_DELEGACIA_CIRC.fillna('NAO INFORMADO')
    d['mes_registro']=d.MES.fillna(0).astype(int).astype(str)
    d['bo_hash']=[hashlib.sha256(('|'.join(map(str,x))).encode()).hexdigest()[:24] for x in d[key].itertuples(index=False,name=None)]
    d=d[['bo_hash','distrito','mes_registro','rotulo']]
    stats['classes_populacao']=d.rotulo.value_counts().sort_index().to_dict()
    if len(d)>20000:d,_=train_test_split(d,train_size=20000,stratify=d.rotulo,random_state=42)
    d=d.sort_values('bo_hash').reset_index(drop=True)
    stats['amostra']=len(d);stats['classes_amostra']=d.rotulo.value_counts().sort_index().to_dict()
    d.to_csv(ROOT/'data/amostra.csv',index=False)
    (ROOT/'data/proveniencia.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False))
    print(json.dumps(stats,indent=2,ensure_ascii=False))
    return d
if __name__=='__main__':
    import sys
    preparar(sys.argv[1] if len(sys.argv)>1 else None)
