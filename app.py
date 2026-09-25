from flask import render_template, session, redirect
from server import app

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
 function install(){
   Object.keys(labels).forEach(function(key){const inp=document.querySelector('input[name="'+key+'"]');if(inp)replaceOne(inp,key.indexOf('ndi_')===0?'ndi':'mjoa')});
 }
 window.addEventListener('message',function(e){if(e.origin!==location.origin||!e.data)return;let type=e.data.type==='ssporm-ndi'?'ndi':e.data.type==='ssporm-mjoa'?'mjoa':null;if(!type)return;const x=document.getElementById(type+'_final_'+e.data.key);if(x&&e.data.score!==null)x.value=e.data.score});
 document.readyState==='loading'?document.addEventListener('DOMContentLoaded',install):install();setTimeout(install,800);
})();
</script>
'''

JS_NULL_FIX = r'''
<script>
(function(){
 function ensureCompat(){
   var f=document.getElementById('f'); if(!f)return;
   [['modq_n','span'],['modq_score','span'],['odi_hidden','input']].forEach(function(x){
     if(document.getElementById(x[0]))return;
     var e=document.createElement(x[1]); e.id=x[0]; e.style.display='none';
     if(x[0]==='odi_hidden'){e.type='hidden'; e.name='odi_legacy_compat';}
     f.appendChild(e);
   });
 }
 document.readyState==='loading'?document.addEventListener('DOMContentLoaded',ensureCompat):ensureCompat();
 setTimeout(ensureCompat,900);
 document.addEventListener('input',function(){ensureCompat();},true);
})();
</script>
'''

@app.after_request
def inject_prom_ui(response):
    try:
        if response.mimetype == 'text/html' and response.status_code == 200 and request_path_is_home():
            html=response.get_data(as_text=True)
            injection=''
            if 'prom-score-wrap' not in html:
                injection += QUESTIONNAIRE_UI
            if 'odi_legacy_compat' not in html:
                injection += JS_NULL_FIX
            if injection:
                html=html.replace('</body>',injection+'</body>')
                response.set_data(html)
                response.headers['Content-Length']=str(len(response.get_data()))
    except Exception:
        pass
    return response

def request_path_is_home():
    from flask import request
    return request.path == '/'
