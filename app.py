from flask import render_template, session, redirect
from server import app

# Redeploy trigger: 2026-09-27 (no functional change)

@app.route('/mjoa')
def mjoa_page():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('mjoa.html')

@app.route('/ndi')
def ndi_page():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('ndi.html')

QUESTIONNAIRE_UI = r'''
<style>
.prom-score-wrap{background:#eef6ff;border:1px solid #b9d7f5;border-radius:10px;padding:10px;margin:4px 0}
.prom-score-wrap input{background:#fff;font-weight:800;text-align:center}
.prom-open{margin-top:8px;background:#1769aa;color:#fff;width:100%}
</style>
<script>
(function(){
 const labels={
  ndi_baseline:'NDI baseline',ndi_3m:'NDI — پیگیری ۳ ماه',ndi_6m:'NDI — پیگیری ۶ ماه',ndi_12m:'NDI — پیگیری ۱۲ ماه',ndi_24m:'NDI — پیگیری ۲۴ ماه',
  mjoa_baseline:'mJOA baseline',mjoa_3m:'mJOA — پیگیری ۳ ماه',mjoa_6m:'mJOA — پیگیری ۶ ماه',mjoa_12m:'mJOA — پیگیری ۱۲ ماه',mjoa_24m:'mJOA — پیگیری ۲۴ ماه'
 };
 function openQ(type,key){window.open('/'+type+'?key='+encodeURIComponent(key),type+'_'+key,'width=760,height=850,scrollbars=yes')}
 function replaceOne(inp,type){
   if(!inp||inp.dataset.promConverted)return;
   const key=inp.name, value=inp.value||'', max=type==='ndi'?100:18;
   const wrap=document.createElement('div');wrap.className='prom-score-wrap';
   wrap.innerHTML='<label>'+labels[key]+' (0–'+max+')</label><input type="number" min="0" max="'+max+'" step="1" name="'+key+'" id="'+type+'_final_'+key+'" value="'+value+'" readonly><button type="button" class="prom-open">📋 باز کردن فرم '+(type==='ndi'?'NDI':'mJOA')+'</button>';
   inp.replaceWith(wrap);wrap.querySelector('button').onclick=function(){openQ(type,key)};
   try{const s=JSON.parse(localStorage.getItem('ssporm_'+type+'_'+key)||'{}');const x=document.getElementById(type+'_final_'+key);if(x&&s.score!==undefined&&s.score!==null)x.value=s.score}catch(e){}
 }
 function removeStrayModq(){
   const allowed=new Set(['odi','odi_3m','odi_6m','odi_12m','odi_24m']);
   document.querySelectorAll('.modq-summary').forEach(function(w){
     const inp=w.querySelector('input');