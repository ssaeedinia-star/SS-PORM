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
DIRECT_MODULE_UI=r'''<style>.diseaseModule{border:2px solid #1769aa;background:#f4f9ff}.diseaseModule button{background:#1769aa;color:#fff;width:100%;margin-top:8px}#patientPhoneDirect{margin-top:10px}</style><script>(function(){function install(){var f=document.getElementById('f');if(!f)return;var first=f.querySelector('.card');if(first&&!f.elements['patient_phone']&&!document.getElementById('patientPhoneDirect')){var p=document.createElement('div');p.id='patientPhoneDirect';p.className='row';p.innerHTML='<div><label>شماره تماس بیمار</label><input type="tel" name="patient_phone" inputmode="tel" autocomplete="tel" placeholder="مثال: 0912xxxxxxx"></div>';first.appendChild(p)}var mods=[['cervical','📁 ماژول بیماران گردنی','معاینه گردن، NDI، mJOA و جراحی اختصاصی گردن'],['thoracolumbar','📁 ماژول Thoracolumbar / Lumbar','معاینه، ODI/MODQ و جراحی توراکولومبار/لومبار'],['deformity','📁 ماژول Deformity','Alignment، پارامترهای دفورمیتی و جراحی اصلاح دفورمیتی'],['asd','📁 ماژول ASD / Revision','Adjacent segment disease، سابقه عمل و Revision'],['tumor','📁 ماژول Tumor','اطلاعات اختصاصی تومور و جراحی'],['trauma','📁 ماژول Trauma','اطلاعات اختصاصی تروما و جراحی']];var anchor=first;mods.forEach(function(m){var id=m[0]+'ModuleDirect';if(document.getElementById(id)){anchor=document.getElementById(id);return}var c=document.createElement('div');c.id=id;c.className='card diseaseModule';c.innerHTML='<h2>'+m[1]+'</h2><p class="small">'+m[2]+'</p><button type="button">باز کردن ماژول</button>';anchor.insertAdjacentElement('afterend',c);anchor=c;c.querySelector('button').onclick=function(){var e=f.elements['study_id'],code=e?String(e.value||'').trim():'';if(!code){alert('ابتدا کد بیمار / کد مطالعه را وارد کنید.');return}var url=m[0]==='cervical'?'/cervical?patient_code='+encodeURIComponent(code):'/module?type='+m[0]+'&patient_code='+encodeURIComponent(code);window.open(url,'ssporm_'+m[0]+'_'+code,'width=900,height=900,scrollbars=yes')}});
// Items now owned by dedicated modules are hidden from the long main form.
document.querySelectorAll('.card').forEach(function(x){if(x.classList.contains('diseaseModule'))return;var h=x.querySelector('h2');if(!h)return;var t=(h.textContent||'').toLowerCase();if(t.indexOf('patient-reported outcome')>=0)x.style.display='none'});
['ndi_baseline','mjoa_baseline','ndi_3m','mjoa_3m','ndi_6m','mjoa_6m','ndi_12m','mjoa_12m','ndi_24m','mjoa_24m'].forEach(function(n){var e=f.elements[n];if(e){var w=e.closest('.prom-score-wrap')||e.parentElement;if(w)w.style.display='none'}});
// Hide module-specific subsections of the general surgery card, while keeping generic procedure fields available.
var surgeryHeaders=['Anterior Cervical Surgery','Posterior Cervical Surgery','Interbody','Decompression / Osteotomy'];document.querySelectorAll('.card h3').forEach(function(h){var t=(h.textContent||'').trim();if(surgeryHeaders.indexOf(t)<0)return;var n=h;while(n){var next=n.nextElementSibling;n.style.display='none';if(next&&next.tagName==='H3')break;n=next}});
// Deformity/alignment values are now in the Deformity module.
document.querySelectorAll('.card').forEach(function(x){var h=x.querySelector('h2');if(h&&(h.textContent||'').trim()==='استخوان و Alignment'){x.querySelectorAll('[name="pi"],[name="pt"],[name="ll"],[name="pill"],[name="sva"],[name="t1pa"]').forEach(function(e){var w=e.parentElement;if(w)w.style.display='none'})}});
}document.readyState==='loading'?document.addEventListener('DOMContentLoaded',install):install();setTimeout(install,300);setTimeout(install,1000)})();</script>'''
@app.after_request
def inject_ui_patch(response):
 if request.path=='/' and response.content_type and 'text/html' in response.content_type:
  try:
   html=response.get_data(as_text=True)
   if 'thoracolumbarModuleDirect' not in html: html=html.replace('</body>',DIRECT_MODULE_UI+'</body>')
   response.set_data(html);response.headers['Content-Length']=str(len(response.get_data()))
  except Exception: pass
  response.headers['Cache-Control']='no-store, no-cache, must-revalidate, max-age=0';response.headers['Pragma']='no-cache';response.headers['Expires']='0'
 return response
