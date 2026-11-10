'use strict';
function infer(model,values){
 let x=[];model.categories.forEach((cats,i)=>cats.forEach(cat=>x.push(cat===String(values[i])?1:0)));
 model.weights.forEach((w,l)=>{x=model.biases[l].map((b,j)=>{let z=b;for(let i=0;i<w.length;i++)z+=x[i]*w[i][j];return l===model.weights.length-1?1/(1+Math.exp(-Math.max(-700,Math.min(700,z)))):Math.max(0,z)});});return x[0];
}
if(typeof module!=='undefined')module.exports={infer};
if(typeof document!=='undefined'){
 const $=id=>document.getElementById(id);let model;
 const months=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
 months.forEach((s,i)=>$('mes').add(new Option(s,String(i+1))));
 fetch('modelo.json').then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()}).then(m=>{
 model=m;$('distrito').replaceChildren(new Option('Selecione o distrito',''));m.categories[0].forEach(c=>$('distrito').add(new Option(c,c)));$('distrito').disabled=false;$('submit').disabled=false;$('status').textContent='Modelo treinado carregado. Nenhum dado do formulário é enviado.';
 const meta=m.metadata;const best=meta.arquiteturas[meta.vencedor];$('modelo').textContent=`Modelo ${meta.nome} · ${meta.dimensao_entrada} entradas → ${best.hidden.join(' → ')} → 1 saída sigmoid · ${meta.divisao.teste.toLocaleString('pt-BR')} boletins no teste.`;
 [['acuracia','Acurácia'],['precision','Precision · roubo'],['recall','Recall · roubo'],['f1','F1 · roubo']].forEach(([k,l])=>{let el=document.createElement('div');el.className='metric';let strong=document.createElement('strong');strong.textContent=(meta.teste[k]*100).toFixed(1).replace('.',',')+'%';let span=document.createElement('span');span.textContent=l;el.append(strong,span);$('metrics').append(el)});
 }).catch(()=>{$('status').textContent='Não foi possível carregar o modelo. Abra a aplicação por um servidor HTTP e recarregue.'});
 $('form').addEventListener('submit',e=>{e.preventDefault();if(!model||!$('form').reportValidity())return;const vals=[$('distrito').value,$('mes').value];if(!vals.every((v,i)=>model.categories[i].includes(v))){$('status').textContent='Selecione valores disponíveis no treinamento.';return}const p=infer(model,vals);$('empty').hidden=true;$('answer').hidden=false;$('classe').textContent=p>=model.threshold?'Roubo':'Furto';$('contexto').textContent=vals[0]+' · '+months[Number(vals[1])-1];$('pr').textContent=(100*p).toFixed(1).replace('.',',')+'%';$('pf').textContent=(100*(1-p)).toFixed(1).replace('.',',')+'%';$('br').style.width=(100*p)+'%';$('bf').style.width=(100*(1-p))+'%';$('status').textContent='Classificação concluída com os pesos da MLP selecionada.';});
}
