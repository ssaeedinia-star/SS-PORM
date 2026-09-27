import os
from flask import Flask, send_from_directory, request
if not os.environ.get("LIARA_ENDPOINT_URL") and os.environ.get("LIARA_ENDPOINT"): os.environ["LIARA_ENDPOINT_URL"]=os.environ["LIARA_ENDPOINT"]
if not os.environ.get("LIARA_BUCKET_NAME") and os.environ.get("LIARA_BUCKET"): os.environ["LIARA_BUCKET_NAME"]=os.environ["LIARA_BUCKET"]
def _liara_instance_path(self):
 p="/tmp/ss_porm_instance";os.makedirs(p,exist_ok=True);return p
Flask.auto_find_instance_path=_liara_instance_path
from app import app
@app.route('/static/save-fix.js')
def serve_save_fix():
 r=send_from_directory('/app','save-fix.js',mimetype='application/javascript');r.headers['Cache-Control']='no-store';return r
@app.route('/static/ui-patch.js')
def serve_ui_patch():
 r=send_from_directory('/app','ui-patch.js',mimetype='application/javascript');r.headers['Cache-Control']='no-store';return r
@app.route('/cervical')
def serve_cervical_module():
 r=send_from_directory('/app','cervical.html',mimetype='text/html');r.headers['Cache-Control']='no-store';return r
@app.route('/module')
def serve_generic_module():
 r=send_from_directory('/app','modules.html',mimetype='text/html');r.headers['Cache-Control']='no-store';return r

MODULE_CARDS=r'''<style>.diseaseModule{border:2px solid #1769aa;background:#f4f9ff}.diseaseModule button{background:#1769aa;color:#fff;width:100%;margin-top:8px}.module-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}@media(max-width:520px){.module-grid{grid-template-columns:1fr}}#patientPhoneDirect{margin-top:10px}.labsMedsFolder>summary{cursor:pointer;font-size:20px;font-weight:700;padding:4px 0}.labsMedsFolder>summary::marker{font-size:16px}.labsMedsFolder[open]>summary{margin-bottom:12px}</style>
<div id="allDiseaseModulesDirect" class="card diseaseModule"><h2>📁 ماژول‌های اختصاصی بیمار</h2><p class="small">فقط ماژول مرتبط با بیمار را باز و تکمیل کنید.</p><div class="module-grid">
<button type="button" onclick="openSSModule('cervical')">گردنی — Cervical</button>
<button type="button" onclick="openSSModule('thoracolumbar')">Thoracolumbar / Lumbar</button>
<button type="button" onclick="openSSModule('deformity')">Deformity</button>
<button type="button" onclick="openSSModule('asd')">ASD / Revision</button>
<button type="button" onclick="openSSModule('tumor')">Tumor</button>
<button type="button" onclick="openSSModule('trauma')">Trauma</button>
</div></div>
<script>
function openSSModule(type){var f=document.getElementById('f'),e=f&&f.elements['study_id'],code=e?String(e.value||'').trim():'';if(!code){alert('ابتدا کد بیمار / کد مطالعه را وارد کنید.');return}var url=type==='cervical'?'/cervical?patient_code='+encodeURIComponent(code):'/module?type='+encodeURIComponent(type)+'&patient_code='+encodeURIComponent(code);window.open(url,'ssporm_'+type+'_'+code,'width=900,height=900,scrollbars=yes')}
(function(){
function cardByTitle(f,text){var cards=f.querySelectorAll('.card');for(var i=0;i<cards.length;i++){var h=cards[i].querySelector('h2');if(h&&(h.textContent||'').indexOf(text)>=0)return cards[i]}return null}
function collapseLabsMeds(f){var card=cardByTitle(f,'آزمایش‌ها و داروهای مهم');if(!card||card.dataset.labsMedsCollapsed==='1')return;card.dataset.labsMedsCollapsed='1';var h=card.querySelector('h2');if(!h)return;var d=document.createElement('details');d.className='labsMedsFolder';var s=document.createElement('summary');s.textContent='🧪💊 آزمایش‌ها و داروهای مهم — Core / Extended';d.appendChild(s);var body=document.createElement('div');while(card.firstChild){var n=card.firstChild;card.removeChild(n);if(n!==h)body.appendChild(n)}d.appendChild(body);card.appendChild(d)}
function cleanMain(){var f=document.getElementById('f');if(!f)return;var first=f.querySelector('.card');if(first&&!f.elements['patient_phone']&&!document.getElementById('patientPhoneDirect')){var p=document.createElement('div');p.id='patientPhoneDirect';p.innerHTML='<label>شماره تماس بیمار</label><input type="tel" name="patient_phone" inputmode="tel" autocomplete="tel" placeholder="مثال: 0912xxxxxxx">';var pname=first.querySelector('input[name="patient_name"]');if(pname)pname.insertAdjacentElement('afterend',p);else first.appendChild(p)}document.querySelectorAll('.card').forEach(function(x){if(x.id==='allDiseaseModulesDirect')return;var h=x.querySelector('h2');if(!h)return;var t=(h.textContent||'').toLowerCase();if(t.indexOf('patient-reported outcome')>=0)x.style.display='none'});['ndi_baseline','mjoa_baseline','ndi_3m','mjoa_3m','ndi_6m','mjoa_6m','ndi_12m','mjoa_12m','ndi_24m','mjoa_24m'].forEach(function(n){var e=f.elements[n];if(e){var w=e.closest('.prom-score-wrap')||e.parentElement;if(w)w.style.display='none'}});var base=cardByTitle(f,'مشخصات پایه'),comorb=cardByTitle(f,'بیماری‌های همراه'),frailty=cardByTitle(f,'Frailty و ASA'),modq=cardByTitle(f,'Persian Modified Oswestry Disability Questionnaire'),mods=document.getElementById('allDiseaseModulesDirect');if(base){var anchor=base;[comorb,frailty,modq].filter(Boolean).forEach(function(card){anchor.insertAdjacentElement('afterend',card);anchor=card})}var neuro=cardByTitle(f,'معاینه نورولوژیک قبل از عمل');if(neuro&&mods)neuro.insertAdjacentElement('afterend',mods);collapseLabsMeds(f);var rev=null;document.querySelectorAll('.card h3').forEach(function(h){if((h.textContent||'').indexOf('در صورت Revision')>=0)rev=h});if(rev){var n=rev;while(n){var next=n.nextElementSibling;if(n!==rev&&n.tagName==='H3'&&(n.textContent||'').trim()==='Fusion / Instrumentation')break;n.style.display='none';n=next}}}document.readyState==='loading'?document.addEventListener('DOMContentLoaded',cleanMain):cleanMain();setTimeout(cleanMain,800)})();
</script>'''

ASD_REVISION_PATCH=r'''<script>(function(){function addRevisionFields(){var q=new URLSearchParams(location.search);if(q.get('type')!=='asd')return;var f=document.getElementById('mf');if(!f||f.elements['prior_surgery_interval'])return;var count=f.elements['prior_spine_surgery_count'];if(!count)return;var box=count.closest('details');if(!box)return;var levels=f.elements['prior_surgery_levels'];var before=levels?levels.previousElementSibling:null;var extra=document.createElement('div');extra.id='asdRevisionExtra';extra.innerHTML='<label>تاریخ/فاصله از آخرین جراحی</label><input name="prior_surgery_interval" placeholder="مثال: 2 سال قبل"><label>نوع جراحی قبلی</label><select name="prior_surgery_type"><option></option><option>Decompression only</option><option>Discectomy</option><option>Anterior cervical fusion</option><option>Posterior fusion/instrumentation</option><option>Interbody fusion</option><option>Deformity correction / long fusion</option><option>Combined anterior + posterior</option><option>سایر / چند نوع</option></select>';
if(before)box.insertBefore(extra,before);else box.appendChild(extra);var desc=f.elements['prior_surgery_description'];if(desc&&!f.elements['pelvic']){var pelvic=document.createElement('div');pelvic.innerHTML='<label>Pelvic fixation</label><select name="pelvic"><option>خیر</option><option>بله</option></select>';var ind=f.elements['revision_indication'];if(ind&&ind.nextSibling)box.insertBefore(pelvic,ind.nextSibling);else box.appendChild(pelvic)}}document.readyState==='loading'?document.addEventListener('DOMContentLoaded',addRevisionFields):addRevisionFields();setTimeout(addRevisionFields,300)})();</script>'''

@app.after_request
def inject_modules(response):
 if response.content_type and 'text/html' in response.content_type:
  try:
   html=response.get_data(as_text=True)
   if request.path=='/':
    if 'allDiseaseModulesDirect' not in html:
     marker="<div class='card'><h2>پیوست تصاویر و فایل‌های رادیولوژیک بیمار</h2>"
     if marker in html: html=html.replace(marker,MODULE_CARDS+marker,1)
     else: html=html.replace('</form>',MODULE_CARDS+'</form>',1)
   elif request.path=='/module' and request.args.get('type')=='asd' and 'asdRevisionExtra' not in html:
    html=html.replace('</body>',ASD_REVISION_PATCH+'</body>',1)
   response.set_data(html);response.headers['Content-Length']=str(len(response.get_data()))
  except Exception: pass
  response.headers['Cache-Control']='no-store, no-cache, must-revalidate, max-age=0';response.headers['Pragma']='no-cache';response.headers['Expires']='0'
 return response
