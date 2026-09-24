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
@app.route('/')
def home():
 with open('index.html',encoding='utf-8') as f: html=f.read()
 if 'persian-datepicker.min.css' not in html: html=html.replace('</head>',PERSIAN_DATE_ASSETS+'</head>')
 html=html.replace('</body>',PERSIAN_DATE_SCRIPT+CLEAR_FORM_SCRIPT+UNIFIED_FILES_SCRIPT+'</body>'); r=Response(html,mimetype='text/html'); r.headers['Cache-Control']='no-store, no-cache, must-revalidate, max-age=0'; return r

@app.route('/api/patients',methods=['POST'])
@login_required
def save_patient():
 p=request.get_json(silent=True); code=(p or {}).get('patient_code')
 if not p:return jsonify({'error':'No data received'}),400
 if not code:return jsonify({'error':'patient_code is required'}),400
 x=Patient.query.filter_by(patient_code=code).first()
 if x:x.data=p
 else:db.session.add(Patient(patient_code=code,data=p))
 db.session.commit(); return jsonify({'success':True,'patient_code':code})
@app.route('/api/patients/<patient_code>')
@login_required
def get_patient(patient_code):
 p=Patient.query.filter_by(patient_code=patient_code).first(); return jsonify(p.data) if p else (jsonify({'error':'Patient not found'}),404)
@app.route('/api/patients')
@login_required
def list_patients():
 return jsonify([{'patient_code':p.patient_code,'patient_name':(p.data or {}).get('patient_name',''),'age':(p.data or {}).get('age',''),'sex':(p.data or {}).get('sex',''),'diagnosis':(p.data or {}).get('diagnosis','')} for p in Patient.query.order_by(Patient.id.desc()).all()])
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
 row.title=title; row.file_date=date; row.file_type=typ; row.stage=stage; db.session.commit()
 return jsonify({'status':'ok','filename':fn,'title':title})

def file_info(obj,prefix,code):
 fn=obj['Key'][len(prefix):]; row=PatientFile.query.filter_by(patient_code=code,filename=fn).first()
 if row:return {'filename':fn,'title':row.title or '','date':row.file_date or '','type':row.file_type or '','stage':row.stage or ''}
 head=s3.head_object(Bucket=LIARA_BUCKET_NAME,Key=obj['Key']); m=head.get('Metadata',{})
 return {'filename':fn,'title':unquote(m.get('title','')),'date':m.get('date',''),'type':unquote(m.get('type','')),'stage':unquote(m.get('stage',''))}
def patient_files(patient_code):
 code=secure_filename(patient_code); prefix=f'{code}/'; res=s3.list_objects_v2(Bucket=LIARA_BUCKET_NAME,Prefix=prefix); return [file_info(o,prefix,code) for o in res.get('Contents',[]) if o['Key'][len(prefix):]]
@app.route('/api/files/<patient_code>')
@login_required
def list_patient_files(patient_code): return jsonify({'patient_code':patient_code,'files':patient_files(patient_code)})
@app.route('/api/files/<patient_code>/<filename>')
@login_required
def get_patient_file(patient_code,filename):
 try:
  o=s3.get_object(Bucket=LIARA_BUCKET_NAME,Key=f'{secure_filename(patient_code)}/{secure_filename(filename)}'); return Response(o['Body'].read(),mimetype=o.get('ContentType','application/octet-stream'))
 except Exception as e:return jsonify({'error':str(e)}),404
@app.route('/patient/<patient_code>')
@login_required
def patient_profile(patient_code): return render_template('patient.html',patient_code=patient_code,files=patient_files(patient_code))
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))