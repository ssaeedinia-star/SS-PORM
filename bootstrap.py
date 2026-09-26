import os
from flask import Flask, send_from_directory, request

# Liara storage variable aliases used in the dashboard.
if not os.environ.get("LIARA_ENDPOINT_URL") and os.environ.get("LIARA_ENDPOINT"):
    os.environ["LIARA_ENDPOINT_URL"] = os.environ["LIARA_ENDPOINT"]
if not os.environ.get("LIARA_BUCKET_NAME") and os.environ.get("LIARA_BUCKET"):
    os.environ["LIARA_BUCKET_NAME"] = os.environ["LIARA_BUCKET"]

# Liara's application filesystem is read-only at runtime. Force Flask's
# automatically discovered instance directory to a writable /tmp location.
def _liara_instance_path(self):
    path = "/tmp/ss_porm_instance"
    os.makedirs(path, exist_ok=True)
    return path

Flask.auto_find_instance_path = _liara_instance_path

from app import app

@app.route('/static/save-fix.js')
def serve_save_fix():
    response = send_from_directory('/app', 'save-fix.js', mimetype='application/javascript')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/static/ui-patch.js')
def serve_ui_patch():
    response = send_from_directory('/app', 'ui-patch.js', mimetype='application/javascript')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/cervical')
def serve_cervical_module():
    response = send_from_directory('/app', 'cervical.html', mimetype='text/html')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

DIRECT_MODULE_UI = r'''
<style>
#cervicalModuleDirect{border:2px solid #1769aa;background:#f4f9ff}
#cervicalModuleDirect .cervical-open{background:#1769aa;color:#fff;width:100%;margin-top:8px}
#patientPhoneDirect{margin-top:10px}
</style>
<script>
(function(){
 function installDirect(){
   var f=document.getElementById('f'); if(!f)return;
   var first=f.querySelector('.card');
   if(first && !f.elements['patient_phone'] && !document.getElementById('patientPhoneDirect')){
     var p=document.createElement('div');p.id='patientPhoneDirect';p.className='row';
     p.innerHTML='<div><label>شماره تماس بیمار</label><input type="tel" name="patient_phone" inputmode="tel" autocomplete="tel" placeholder="مثال: 0912xxxxxxx"></div>';
     first.appendChild(p);
   }
   if(!document.getElementById('cervicalModuleDirect')){
     var c=document.createElement('div');c.id='cervicalModuleDirect';c.className='card';
     c.innerHTML='<h2>📁 ماژول بیماران گردنی</h2><p class="small">معاینه اختصاصی گردن، NDI و mJOA در پوشه اختصاصی بیمار ثبت می‌شوند.</p><button type="button" class="cervical-open">باز کردن پوشه بیماران گردنی</button>';
     if(first)first.insertAdjacentElement('afterend',c);else f.insertBefore(c,f.firstChild);
     c.querySelector('button').onclick=function(){var e=f.elements['study_id'],code=e?String(e.value||'').trim():'';if(!code){alert('ابتدا کد بیمار / کد مطالعه را وارد کنید.');return;}window.open('/cervical?patient_code='+encodeURIComponent(code),'ssporm_cervical_'+code,'width=850,height=900,scrollbars=yes');};
   }
   document.querySelectorAll('.card').forEach(function(x){
     if(x.id==='cervicalModuleDirect')return;
     var h=x.querySelector('h2');if(!h)return;var t=(h.textContent||'').toLowerCase();
     if(t.indexOf('ndi')>=0||t.indexOf('mjoa')>=0)x.style.display='none';
   });
 }
 document.readyState==='loading'?document.addEventListener('DOMContentLoaded',installDirect):installDirect();
 setTimeout(installDirect,300);setTimeout(installDirect,1000);
})();
</script>
'''

@app.after_request
def inject_ui_patch(response):
    if request.path == '/' and response.content_type and 'text/html' in response.content_type:
        try:
            html = response.get_data(as_text=True)
            # Inject the module code directly into the HTML response so it does not
            # depend on loading a separate JS asset or browser cache behavior.
            if 'cervicalModuleDirect' not in html:
                html = html.replace('</body>', DIRECT_MODULE_UI + '</body>')
            response.set_data(html)
            response.headers['Content-Length'] = str(len(response.get_data()))
        except Exception:
            pass
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response
