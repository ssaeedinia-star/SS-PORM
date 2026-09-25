from flask import render_template, session, redirect
from server import app

@app.route('/mjoa')
def mjoa_page():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('mjoa.html')

MJOA_UI = r'''
<style>
.mjoa-card{background:#fff;padding:16px;margin:12px 0;border-radius:14px}.mjoa-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.mjoa-box{background:#eef6ff;border:1px solid #b9d7f5;border-radius:10px;padding:12px}.mjoa-box input{background:#fff;font-weight:800;font-size:18px;text-align:center}.mjoa-open{margin-top:10px;background:#1769aa;color:#fff;width:100%}@media(max-width:520px){.mjoa-grid{grid-template-columns:1fr}}
</style>
<script>
(function(){
 const periods=[['mjoa_baseline','ارزیابی اولیه'],['mjoa_3m','پیگیری ۳ ماه'],['mjoa_6m','پیگیری ۶ ماه'],['mjoa_12m','پیگیری ۱۲ ماه']];
 function openMjoa(key){window.open('/mjoa?key='+encodeURIComponent(key),'mjoa_'+key,'width=760,height=850,scrollbars=yes')}
 function install(){
   const f=document.getElementById('f'); if(!f||document.getElementById('mjoaUnifiedCard'))return;
   const card=document.createElement('div'); card.id='mjoaUnifiedCard'; card.className='mjoa-card';
   card.innerHTML='<h2>mJOA — ارزیابی میلوپاتی گردنی</h2><p class="small">جزئیات چهار آیتم در پوشه اختصاصی ثبت می‌شود و در فرم اصلی فقط امتیاز نهایی ۰ تا ۱۸ نمایش داده می‌شود.</p><div class="mjoa-grid">'+periods.map(p=>'<div class="mjoa-box"><label>'+p[1]+'</label><input type="number" min="0" max="18" step="1" name="'+p[0]+'" id="mjoa_final_'+p[0]+'" readonly><button type="button" class="mjoa-open" data-key="'+p[0]+'">📋 باز کردن فرم mJOA</button></div>').join('')+'</div>';
   const submit=[...f.querySelectorAll('button')].find(b=>(b.textContent||'').includes('ذخیره بیمار'));
   if(submit&&submit.closest('.card')) f.insertBefore(card,submit.closest('.card')); else f.appendChild(card);
   card.querySelectorAll('.mjoa-open').forEach(b=>b.onclick=()=>openMjoa(b.dataset.key));
   periods.forEach(p=>{try{const s=JSON.parse(localStorage.getItem('ssporm_mjoa_'+p[0])||'{}');const x=document.getElementById('mjoa_final_'+p[0]);if(x&&s.score!==undefined&&s.score!==null)x.value=s.score}catch(e){}});
 }
 window.addEventListener('message',function(e){if(e.origin!==location.origin||!e.data||e.data.type!=='ssporm-mjoa')return;const x=document.getElementById('mjoa_final_'+e.data.key);if(x&&e.data.score!==null)x.value=e.data.score});
 document.readyState==='loading'?document.addEventListener('DOMContentLoaded',install):install();setTimeout(install,800);
})();
</script>
'''

# The legacy calc() function in index.html still references MODQ elements that are
# intentionally removed by the unified questionnaire UI. Keep invisible compatibility
# targets so input events cannot throw "Cannot set properties of null".
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
def inject_mjoa(response):
    try:
        if response.mimetype == 'text/html' and response.status_code == 200 and request_path_is_home():
            html=response.get_data(as_text=True)
            injection=''
            if 'mjoaUnifiedCard' not in html:
                injection += MJOA_UI
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
