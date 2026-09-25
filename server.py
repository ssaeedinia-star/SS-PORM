import os
from functools import wraps
from urllib.parse import quote, unquote
import boto3
from botocore.config import Config
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template, Response, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app=Flask(__name__,static_folder="."); app.secret_key=os.environ.get("SECRET_KEY"); app.config.update(SESSION_COOKIE_SECURE=True,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE="Lax"); CORS(app)
ADMIN_USERNAME=os.environ.get("ADMIN_USERNAME"); ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD")
LIARA_ENDPOINT_URL=os.environ.get("LIARA_ENDPOINT_URL"); LIARA_ACCESS_KEY=os.environ.get("LIARA_ACCESS_KEY"); LIARA_SECRET_KEY=os.environ.get("LIARA_SECRET_KEY"); LIARA_BUCKET_NAME=os.environ.get("LIARA_BUCKET_NAME")
s3=boto3.client("s3",endpoint_url=LIARA_ENDPOINT_URL,aws_access_key_id=LIARA_ACCESS_KEY,aws_secret_access_key=LIARA_SECRET_KEY,config=Config(s3={"addressing_style":"path"}))
database_url=os.environ.get("DATABASE_URL","sqlite:///ss_porm.db")
if database_url.startswith("postgres://"): database_url=database_url.replace("postgres://","postgresql://",1)
app.config["SQLALCHEMY_DATABASE_URI"]=database_url; app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False; db=SQLAlchemy(app)
def login_required(f):
 @wraps(f)
 def d(*a,**k):
  if not session.get("logged_in"): return jsonify({"error":"Unauthorized"}),401
  return f(*a,**k)
 return d
@app.route('/api/login',methods=['POST'])
def login():
 d=request.get_json(silent=True) or {}
 if d.get('username')==ADMIN_USERNAME and d.get('password')==ADMIN_PASSWORD: session['logged_in']=True; return jsonify({'status':'ok'})
 return jsonify({'error':'نام کاربری یا رمز عبور اشتباه است'}),401
@app.route('/api/logout',methods=['POST'])
def logout(): session.clear(); return jsonify({'status':'ok'})
@app.route('/api/auth-status')
def auth_status(): return jsonify({'logged_in':bool(session.get('logged_in'))})
class Patient(db.Model):
 id=db.Column(db.Integer,primary_key=True); patient_code=db.Column(db.String(100),unique=True,nullable=False); data=db.Column(db.JSON,nullable=False)
class PatientFile(db.Model):
 id=db.Column(db.Integer,primary_key=True); patient_code=db.Column(db.String(100),nullable=False,index=True); filename=db.Column(db.String(255),nullable=False); title=db.Column(db.Text,default=''); file_date=db.Column(db.String(32),default=''); file_type=db.Column(db.String(100),default=''); stage=db.Column(db.String(100),default='')
 __table_args__=(db.UniqueConstraint('patient_code','filename',name='uq_patient_file'),)
with app.app_context(): db.create_all()
PERSIAN_DATE_ASSETS='''<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/persian-datepicker@1.2.0/dist/css/persian-datepicker.min.css"><script src="https://code.jquery.com/jquery-3.7.1.min.js"></script><script src="https://cdn.jsdelivr.net/npm/persian-date@1.1.0/dist/persian-date.min.js"></script><script src="https://cdn.jsdelivr.net/npm/persian-datepicker@1.2.0/dist/js/persian-datepicker.min.js"></script>'''
PERSIAN_DATE_SCRIPT=r'''<script>(function(){function i(){if(!window.jQuery||!jQuery.fn.persianDatepicker)return;document.querySelectorAll('input[name="assessment_date"],input[name="surgery_date"],input[type="date"],input[name*="date"],input[id*="date"]').forEach(function(e){if(e.dataset.persianReady)return;e.dataset.persianReady='1';e.type='text';e.removeAttribute('pattern');e.setAttribute('inputmode','none');e.readOnly=true;jQuery(e).persianDatepicker({format:'YYYY/MM/DD',autoClose:true,initialValue:false,observer:true,calendar:{persian:{locale:'fa'}}});});}document.readyState==='loading'?document.addEventListener('DOMContentLoaded',i):i();setTimeout(i,500)})();</script>'''
CLEAR_FORM_SCRIPT=r'''<script>(function(){function c(){var f=document.getElementById('f');if(!f)return;f.reset();['bmi','mfi','mfic','modqScore','odi'].forEach(function(id){var e=document.getElementById(id);if(e)e.textContent=id==='mfi'?'0.00':id==='mfic'?'0':'—';});}document.readyState==='loading'?document.addEventListener('DOMContentLoaded',c):c();window.addEventListener('pageshow',function(e){if(e.persisted)c()})})();</script>'''
UNIFIED_FILES_SCRIPT=r'''<script>(function(){function u(){document.querySelectorAll('input[type="file"]').forEach(function(inp){var card=inp.closest('.card');if(!card||card.dataset.unifiedFiles)return;card.dataset.unifiedFiles='1';card.innerHTML='<h2>تصاویر و مدارک بیمار</h2><p class="small">آپلود و مشاهده تصاویر و مدارک از پرونده واحد بیمار انجام می‌شود.</p><button type="button" onclick="openPatientProfile()">📁 باز کردن پرونده تصاویر و مدارک</button>';});}document.readyState==='loading'?document.addEventListener('DOMContentLoaded',u):u()})();</script>'''
PATIENT_LIST_SCRIPT=r'''<style>#patientList{max-height:260px;overflow-y:auto;border:1px solid #ddd;border-radius:10px;margin-top:8px;background:#fff}#patientList .patient-row{display:grid;grid-template-columns:42px 1fr auto;gap:8px;align-items:center;padding:8px 10px;border-bottom:1px solid #eee;font-size:13px}#patientList .patient-row:last-child{border-bottom:0}#patientList .patient-main{min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer}#patientList .row-no{font-weight:700;text-align:center;background:#eef2f3;border-radius:7px;padding:5px 2px}.delete-patient{background:#b42318;color:#fff;padding:7px 9px;font-size:12px;border-radius:7px}.record-no-box{display:flex;align-items:center;gap:10px;margin:10px 0 14px;padding:10px 12px;background:#eef6ff;border:1px solid #b9d7f5;border-radius:10px}.record-no-label{font-weight:700}.record-no-value{min-width:58px;text-align:center;font-size:18px;font-weight:800;background:#fff;border:1px solid #9fc4ea;border-radius:8px;padding:7px 12px}</style><script>function escHtml(v){return String(v??'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}async function refreshRecordNumber(){try{const r=await fetch('/api/patients/next-row');if(!r.ok)return;const d=await r.json(),e=document.getElementById('recordNumberValue');if(e)e.textContent=d.next_row}catch(e){}}function installRecordNumber(){const f=document.getElementById('f');if(!f||document.getElementById('recordNumberBox'))return;const box=document.createElement('div');box.id='recordNumberBox';box.className='record-no-box';box.innerHTML='<span class="record-no-label">ردیف پرونده</span><span id="recordNumberValue" class="record-no-value">—</span><span class="small">(اتوماتیک)</span>';f.insertBefore(box,f.firstChild);refreshRecordNumber()}window.listPatients=async function(){const box=document.getElementById('patientList');box.textContent='در حال دریافت لیست بیماران...';try{const r=await fetch('/api/patients'),patients=await r.json();if(!r.ok)throw new Error('HTTP '+r.status);if(!patients.length){box.textContent='بیماری ذخیره نشده است.';refreshRecordNumber();return}box.innerHTML=patients.map(p=>{const code=escHtml(p.patient_code),name=escHtml(p.patient_name),row=p.row_number;return `<div class="patient-row"><span class="row-no">${row}</span><span class="patient-main" data-code="${code}" data-row="${row}" onclick="document.getElementById('f').elements['study_id'].value=this.dataset.code;document.getElementById('recordNumberValue').textContent=this.dataset.row;loadPatient();"><b>${code}</b>${name?' — '+name:''}</span><button type="button" class="delete-patient" data-code="${code}" onclick="deletePatient(this.dataset.code)">حذف</button></div>`}).join('')}catch(e){box.textContent='دریافت لیست بیماران انجام نشد: '+e.message}};window.deletePatient=async function(code){if(!confirm('پرونده '+code+' به‌طور کامل حذف شود؟\nاطلاعات بیمار و همه تصاویر/فایل‌های او حذف خواهند شد.'))return;if(!confirm('تأیید نهایی حذف پرونده '+code+'؟ این عملیات قابل بازگشت نیست.'))return;try{const r=await fetch('/api/patients/'+encodeURIComponent(code),{method:'DELETE'}),d=await r.json();if(!r.ok)throw new Error(d.error||('HTTP '+r.status));const f=document.getElementById('f');if((f.elements['study_id'].value||'').trim()===code)f.reset();await listPatients();await refreshRecordNumber();alert('پرونده حذف شد.')}catch(e){alert('حذف پرونده انجام نشد: '+e.message)}};document.addEventListener('DOMContentLoaded',installRecordNumber);window.addEventListener('pageshow',refreshRecordNumber);</script>'''
@app.route('/')
def home():
 with open('index.html',encoding='utf-8') as f: html=f.read()
 if 'persian-datepicker.min.css' not in html: html=html.replace('</head>',PERSIAN_DATE_ASSETS+'</head>')
 html=html.replace('</body>',PERSIAN_DATE_SCRIPT+CLEAR_FORM_SCRIPT+UNIFIED_FILES_SCRIPT+PATIENT_LIST_SCRIPT+'</body>'); r=Response(html,mimetype='text/html'); r.headers['Cache-Control']='no-store, no-cache, must-revalidate, max-age=0'; return r
@app.route('/modq')
@login_required
def modq_page(): return render_template('modq.html')
@app.route('/api/patients/next-row')
@login_required
def next_patient_row():
 max_id=db.session.query(db.func.max(Patient.id)).scalar() or 0; return jsonify({'next_row':max_id+1})
@app.route('/api/patients',methods=['POST'])
@login_required
def save_patient():
 p=request.get_json(silent=True); code=(p or {}).get('patient_code')
 if not p:return jsonify({'error':'No data received'}),400
 if not code:return jsonify({'error':'patient_code is required'}),400
 x=Patient.query.filter_by(patient_code=code).first(); is_new=x is None
 if x:x.data=p
 else:x=Patient(patient_code=code,data=p); db.session.add(x)
 db.session.commit(); return jsonify({'success':True,'patient_code':code,'row_number':x.id,'is_new':is_new})
@app.route('/api/patients/<patient_code>',methods=['GET'])
@login_required
def get_patient(patient_code):
 p=Patient.query.filter_by(patient_code=patient_code).first()
 if not p:return jsonify({'error':'Patient not found'}),404
 data=dict(p.data or {}); data['_row_number']=p.id; return jsonify(data)
@app.route('/api/patients/<patient_code>',methods=['DELETE'])
@login_required
def delete_patient(patient_code):
 p=Patient.query.filter_by(patient_code=patient_code).first()
 if not p:return jsonify({'error':'Patient not found'}),404
 code=secure_filename(patient_code); prefix=f'{code}/'
 try:
  while True:
   res=s3.list_objects_v2(Bucket=LIARA_BUCKET_NAME,Prefix=prefix); objs=[{'Key':o['Key']} for o in res.get('Contents',[])]
   if objs:s3.delete_objects(Bucket=LIARA_BUCKET_NAME,Delete={'Objects':objs,'Quiet':True})
   if not res.get('IsTruncated'):break
  PatientFile.query.filter_by(patient_code=code).delete(synchronize_session=False); db.session.delete(p); db.session.commit(); return jsonify({'success':True,'patient_code':patient_code})
 except Exception as e: db.session.rollback(); return jsonify({'error':str(e)}),500
@app.route('/api/patients')
@login_required
def list_patients():
 ps=Patient.query.order_by(Patient.id.asc()).all(); return jsonify([{'row_number':p.id,'patient_code':p.patient_code,'patient_name':(p.data or {}).get('patient_name',''),'age':(p.data or {}).get('age',''),'sex':(p.data or {}).get('sex',''),'diagnosis':(p.data or {}).get('diagnosis','')} for p in ps])
@app.route('/api/health')
def health(): return jsonify({'status':'ok','service':'SS-PORM'})
@app.route('/upload')
def upload_page():
 c=request.args.get('patient','').strip(); return redirect('/patient/'+quote(c,safe='')) if c else redirect('/')
@app.route('/api/upload/<patient_code>',methods=['POST'])
@login_required
def upload_file(patient_code):
 if 'file' not in request.files:return jsonify({'error':'No file provided'}),400
 f=request.files['file']
 if not f or not f.filename:return jsonify({'error':'No file selected'}),400
 code=secure_filename(patient_code); fn=secure_filename(f.filename); title=request.form.get('title','').strip(); date=request.form.get('date','').strip().translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹','0123456789')); typ=request.form.get('type','').strip(); stage=request.form.get('stage','').strip(); key=f'{code}/{fn}'
 s3.upload_fileobj(f,LIARA_BUCKET_NAME,key,ExtraArgs={'ContentType':f.content_type or 'application/octet-stream','Metadata':{'title':quote(title,safe=''),'date':date,'type':quote(typ,safe=''),'stage':quote(stage,safe='')}})
 row=PatientFile.query.filter_by(patient_code=code,filename=fn).first()
 if not row: row=PatientFile(patient_code=code,filename=fn); db.session.add(row)
 row.title=title; row.file_date=date; row.file_type=typ; row.stage=stage; db.session.commit(); return jsonify({'status':'ok','filename':fn,'title':title})
def file_info(obj,prefix,code):
 fn=obj['Key'][len(prefix):]; row=PatientFile.query.filter_by(patient_code=code,filename=fn).first()
 if row:return {'filename':fn,'title':row.title or '','date':row.file_date or '','type':row.file_type or '','stage':row.stage or ''}
 head=s3.head_object(Bucket=LIARA_BUCKET_NAME,Key=obj['Key']); m=head.get('Metadata',{}); return {'filename':fn,'title':unquote(m.get('title','')),'date':m.get('date',''),'type':unquote(m.get('type','')),'stage':unquote(m.get('stage',''))}
def patient_files(patient_code):
 code=secure_filename(patient_code); prefix=f'{code}/'; res=s3.list_objects_v2(Bucket=LIARA_BUCKET_NAME,Prefix=prefix); return [file_info(o,prefix,code) for o in res.get('Contents',[]) if o['Key'][len(prefix):]]
@app.route('/api/files/<patient_code>')
@login_required
def list_patient_files(patient_code): return jsonify({'patient_code':patient_code,'files':patient_files(patient_code)})
@app.route('/api/files/<patient_code>/<filename>')
@login_required
def get_patient_file(patient_code,filename):
 try:o=s3.get_object(Bucket=LIARA_BUCKET_NAME,Key=f'{secure_filename(patient_code)}/{secure_filename(filename)}'); return Response(o['Body'].read(),mimetype=o.get('ContentType','application/octet-stream'))
 except Exception as e:return jsonify({'error':str(e)}),404
@app.route('/patient/<patient_code>')
@login_required
def patient_profile(patient_code): return render_template('patient.html',patient_code=patient_code,files=patient_files(patient_code))
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))