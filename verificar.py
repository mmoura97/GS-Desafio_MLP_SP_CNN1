"""Valida separação, dimensões e equivalência numérica Python/JavaScript."""
from pathlib import Path
import json,pickle,subprocess
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent

def verificar():
    d=pd.read_csv(ROOT/'data/amostra.csv',dtype={'mes_registro':str})
    splits=pd.read_csv(ROOT/'artifacts/divisao.csv')
    assert d.bo_hash.is_unique and splits.bo_hash.is_unique
    assert set(d.bo_hash)==set(splits.bo_hash)
    assert splits.conjunto.value_counts().to_dict()=={'treino':14000,'validacao':3000,'teste':3000}
    with open(ROOT/'artifacts/modelo.pkl','rb') as f:bundle=pickle.load(f)
    # Somente validação, preservando o teste para a avaliação final.
    chosen=splits.loc[splits.conjunto.eq('validacao'),'bo_hash'].head(200)
    sample=d.set_index('bo_hash').loc[chosen,bundle['features']]
    py=bundle['modelo'].predict_proba(bundle['encoder'].transform(sample))[:,1]
    js="const fs=require('fs');const {infer}=require('./dist/app.js');const m=JSON.parse(fs.readFileSync('./dist/modelo.json'));let s='';process.stdin.on('data',d=>s+=d);process.stdin.on('end',()=>console.log(JSON.stringify(JSON.parse(s).map(v=>infer(m,v)))));"
    proc=subprocess.run(['node','-e',js],input=json.dumps(sample.values.tolist()),text=True,capture_output=True,cwd=ROOT,check=True)
    pred=np.array(json.loads(proc.stdout));err=float(np.max(np.abs(py-pred)));assert err<1e-10,err
    out={'boletins_unicos':len(d),'conjuntos_disjuntos':True,'casos_paridade':len(pred),'erro_maximo_python_js':err,'probabilidades_validas':bool(np.all((pred>=0)&(pred<=1)))}
    (ROOT/'artifacts/verificacao.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':verificar()
