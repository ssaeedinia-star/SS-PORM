import os
from functools import wraps
from urllib.parse import quote, unquote
import boto3
from botocore.config import Config
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template, Response, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
app.secret_key = os.environ.get("SECRET_KEY")
app.config.update(SESSION_COOKIE_SECURE=True, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
CORS(app)
ADMIN_USERNAME=os.environ.get("ADMIN_USERNAME"); ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD")
LIARA_ENDPOINT_URL=os.environ.get("LIARA_ENDPOINT_URL"); LIARA_ACCESS_KEY=os.environ.get("LIARA_ACCESS_KEY"); LIARA_SECRET_KEY=os.environ.get("LIARA_SECRET_KEY"); LIARA_BUCKET_NAME=os.environ.get("LIARA_BUCKET_NAME")
s3=boto3.client("s3",endpoint_url=LIARA_ENDPOINT_URL,aws_access_key_id=LIARA_ACCESS_KEY,aws_secret_access_key=LIARA_SECRET_KEY,config=Config(s3={"addressing_style":"path"}))
database_url=os.environ.get("DATABASE_URL","sqlite:///ss_porm.db")
if database_url.startswith("postgres://"): database_url=database_url.replace("postgres://","postgresql://",1)
app.config["SQLALCHEMY_DATABASE_URI"]=database_url; app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)

def login_required(f):
 @wraps(f)
 def decorated_function(*args,**kwargs):
  if not session.get("logged_in"): return jsonify({"error":"Unauthorized"}),401
  return f(*args,**kwargs)
 return decorated_function

@app.route("/api/login",methods=["POST"])
def login():
 data=request.get_json(silent=True) or {}
 if data.get("username")==ADMIN_USERNAME and data.get("password")==ADMIN_PASSWORD: session["logged_in"]=True; return jsonify({"status":"ok"})
 return jsonify({"error":"نام کاربری یا رمز عبور اشتباه است"}),401
@app.route("/api/logout",methods=["POST"])
def logout(): session.clear(); return jsonify({"status":"ok"})
@app.route("/api/auth-status",methods=["GET"])
def auth_status(): return jsonify({"logged_in":bool(session.get("logged_in"))})

class Patient(db.Model):
 id=db.Column(db.Integer,primary_key=True); patient_code=db.Column(db.String(100),unique=True,nullable=False); data=db.Column(db.JSON,nullable=False)
with app.app_context(): db.create_all()

PERSIAN_DATE_ASSETS='''<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/persian-datepicker@1.2.0/dist/css/persian-datepicker.min.css"><script src="https://code.jquery.com/jquery-3.7.1.min.js"></script><script src="https://cdn.jsdelivr.net/npm/persian-date@1.1.0/dist/persian-date.min.js"></script><script src="https://cdn.jsdelivr.net/npm/persian-datepicker@1.2.0/dist/js/persian-datepicker.min.js"></script>'''
PERSIAN_DATE_SCRIPT=r'''<script>(function(){function initPersianDates(){if(!window.jQuery||!jQuery.fn.persianDatepicker)return;var selectors=['input[name="assessment_date"]','input[name="surgery_date"]','input[type="date"]','input[name*="date"]','input[id*="date"]'];var seen=new Set();document.querySelectorAll(selectors.join(',')).forEach(function(el){if(seen.has(el)||el.dataset.persianReady==='1')return;seen.add(el);el.dataset.persianReady='1';el.type='text';el.removeAttribute('pattern');el.removeAttribute('min');el.removeAttribute('max');el.setAttribute('inputmode','none');el.setAttribute('autocomplete','off');el.setAttribute('placeholder','انتخاب تاریخ شمسی');el.readOnly=true;jQuery(el).persianDatepicker({format:'YYYY/MM/DD',autoClose:true,initialValue:false,observer:true,calendar:{persian:{locale:'fa'}}});});}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initPersianDates);else initPersianDates();setTimeout(initPersianDates,500);})();</script>'''
CLEAR_FORM_SCRIPT=r'''<script>(function(){function clearPatientForm(){var f=document.getElementById('f');if(!f)return;f.reset();['bmi','mfi','mfic','modqScore','odi'].forEach(function(id){var e=document.getElementById(id);if(e){if(id==='mfi')e.textContent='0.00';else if(id==='mfic')e.textContent='0';else e.textContent='—';}});var ls=document.getElementById('loadStatus');if(ls)ls.textContent='';}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',clearPatientForm);else clearPatientForm();window.addEventListener('pageshow',function(e){if(e.persisted)clearPatientForm();});})();</script>'''
UNIFIED_FILES_SCRIPT=r'''<script>(function(){function unify(){document.querySelectorAll('input[type="file"]').forEach(function(inp){var card=inp.closest('.card');if(!card||card.dataset.unifiedFiles==='1')return;card.dataset.unifiedFiles='1';card.innerHTML='<h2>تصاویر و مدارک بیمار</h2><p class="small">آپلود و مشاهده تمام X-ray، CT، MRI و مدارک از پرونده واحد بیمار انجام می‌شود.</p><button type="button" onclick="openPatientProfile()">📁 باز کردن پرونده تصاویر و مدارک</button>';});}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',unify);else unify();})();</script>'''

@app.route("/")
def home():
 with open("index.html","r",encoding="utf-8") as f: html=f.read()
 if "persian-datepicker.min.css" not in html: html=html.replace("</head>",PERSIAN_DATE_ASSETS+"</head>")
 html=html.replace("</body>",PERSIAN_DATE_SCRIPT+CLEAR_FORM_SCRIPT+UNIFIED_FILES_SCRIPT+"</body>")
 resp=Response(html,mimetype="text/html"); resp.headers["Cache-Control"]="no-store, no-cache, must-revalidate, max-age=0"; return resp

@app.route("/api/patients",methods=["POST"])
@login_required
def save_patient():
 payload=request.get_json(silent=True)
 if not payload:return jsonify({"error":"No data received"}),400
 patient_code=payload.get("patient_code")
 if not patient_code:return jsonify({"error":"patient_code is required"}),400
 patient=Patient.query.filter_by(patient_code=patient_code).first()
 if patient: patient.data=payload
 else: patient=Patient(patient_code=patient_code,data=payload); db.session.add(patient)
 db.session.commit(); return jsonify({"success":True,"patient_code":patient_code})
@app.route("/api/patients/<patient_code>",methods=["GET"])
@login_required
def get_patient(patient_code):
 patient=Patient.query.filter_by(patient_code=patient_code).first()
 if not patient:return jsonify({"error":"Patient not found"}),404
 return jsonify(patient.data)
@app.route("/api/patients",methods=["GET"])
@login_required
def list_patients():
 patients=Patient.query.order_by(Patient.id.desc()).all(); result=[]
 for patient in patients:
  data=patient.data or {}; result.append({"patient_code":patient.patient_code,"patient_name":data.get("patient_name",""),"age":data.get("age",""),"sex":data.get("sex",""),"diagnosis":data.get("diagnosis","")})
 return jsonify(result)
@app.route("/api/health")
def health(): return jsonify({"status":"ok","service":"SS-PORM"})

@app.route("/upload")
def upload_page():
 code=request.args.get("patient","").strip()
 return redirect("/patient/"+quote(code,safe="")) if code else redirect("/")

@app.route("/api/upload/<patient_code>",methods=["POST"])
@login_required
def upload_file(patient_code):
 if "file" not in request.files:return jsonify({"error":"No file provided"}),400
 file=request.files["file"]
 if not file or not file.filename:return jsonify({"error":"No file selected"}),400
 patient_code_safe=secure_filename(patient_code); filename=secure_filename(file.filename)
 file_title=request.form.get("title","").strip(); file_date=request.form.get("date","").strip().translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹","0123456789")); file_type=request.form.get("type","").strip(); file_stage=request.form.get("stage","").strip(); object_key=f"{patient_code_safe}/{filename}"
 metadata={"title":quote(file_title,safe=""),"date":file_date,"type":quote(file_type,safe=""),"stage":quote(file_stage,safe="")}
 s3.upload_fileobj(file,LIARA_BUCKET_NAME,object_key,ExtraArgs={"ContentType":file.content_type or "application/octet-stream","Metadata":metadata})
 return jsonify({"status":"ok","filename":filename,"title":file_title})

def file_info(obj,prefix):
 filename=obj["Key"][len(prefix):]; head=s3.head_object(Bucket=LIARA_BUCKET_NAME,Key=obj["Key"]); m=head.get("Metadata",{})
 return {"filename":filename,"title":unquote(m.get("title","")),"date":m.get("date",""),"type":unquote(m.get("type","")),"stage":unquote(m.get("stage",""))}
@app.route("/api/files/<patient_code>")
@login_required
def list_patient_files(patient_code):
 prefix=f"{secure_filename(patient_code)}/"; response=s3.list_objects_v2(Bucket=LIARA_BUCKET_NAME,Prefix=prefix); files=[]
 for obj in response.get("Contents",[]):
  if obj["Key"][len(prefix):]: files.append(file_info(obj,prefix))
 return jsonify({"patient_code":patient_code,"files":files})
@app.route("/api/files/<patient_code>/<filename>")
@login_required
def get_patient_file(patient_code,filename):
 object_key=f"{secure_filename(patient_code)}/{secure_filename(filename)}"
 try:
  obj=s3.get_object(Bucket=LIARA_BUCKET_NAME,Key=object_key); return Response(obj["Body"].read(),mimetype=obj.get("ContentType","application/octet-stream"))
 except Exception as e:return jsonify({"error":str(e)}),404
@app.route("/patient/<patient_code>")
@login_required
def patient_profile(patient_code):
 prefix=f"{secure_filename(patient_code)}/"; response=s3.list_objects_v2(Bucket=LIARA_BUCKET_NAME,Prefix=prefix); files=[]
 for obj in response.get("Contents",[]):
  if obj["Key"][len(prefix):]: files.append(file_info(obj,prefix))
 return render_template("patient.html",patient_code=patient_code,files=files)

if __name__=="__main__":
 port=int(os.environ.get("PORT",10000)); app.run(host="0.0.0.0",port=port)
