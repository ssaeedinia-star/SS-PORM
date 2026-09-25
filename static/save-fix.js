// SS-PORM same-origin save fix
(function(){
  async function safeJson(response){
    const text=await response.text();
    try{return text?JSON.parse(text):{};}catch(e){return {error:text||('HTTP '+response.status)};}
  }

  window.savePatient=async function(){
    const f=document.getElementById('f'), o={};
    if(!f)return;
    for(const el of f.elements){
      if(!el.name||el.type==='file'||el.type==='button')continue;
      if(el.type==='checkbox')o[el.name]=el.checked;
      else if(el.type==='radio'){if(el.checked)o[el.name]=el.value;}
      else o[el.name]=el.value;
    }
    o.patient_code=(o.study_id||'').trim();
    const bmi=document.getElementById('bmi'), mfi=document.getElementById('mfi');
    o.BMI=bmi?bmi.textContent:'';
    o.mFI5=mfi?mfi.textContent:'';
    const s=document.getElementById('saveStatus'), b=document.getElementById('saveBtn');
    if(s)s.style.display='block';
    if(!o.patient_code){if(s)s.textContent='ابتدا کد بیمار / کد مطالعه را وارد کنید.';return;}
    if(b)b.disabled=true;
    if(s)s.textContent='در حال ذخیره...';
    try{
      const r=await fetch('/api/patients',{
        method:'POST',
        credentials:'same-origin',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(o)
      });
      const d=await safeJson(r);
      if(!r.ok)throw new Error(d.error||('HTTP '+r.status));
      try{sessionStorage.removeItem('ssporm_main_form_draft_v1');}catch(e){}
      if(s)s.textContent='✓ اطلاعات بیمار با موفقیت در سرور ذخیره شد.';
      if(typeof window.refreshRecordNumber==='function')await window.refreshRecordNumber();
    }catch(e){
      if(s)s.textContent='ذخیره انجام نشد: '+e.message;
    }finally{
      if(b)b.disabled=false;
    }
  };

  window.loadPatientFiles=async function(patientCode){
    const box=document.getElementById('patientFiles');
    if(!box)return;
    try{
      const r=await fetch('/api/files/'+encodeURIComponent(patientCode),{credentials:'same-origin'});
      const d=await safeJson(r);
      if(!r.ok)throw new Error(d.error||('HTTP '+r.status));
      const files=d.files||[];
      if(!files.length){box.innerHTML='<b>فایل‌های بیمار:</b><br>فایلی ثبت نشده است.';box.style.display='block';return;}
      box.innerHTML='<b>فایل‌های بیمار:</b><br>'+files.map(function(file){
        const fn=typeof file==='string'?file:(file.filename||'');
        return '<a target="_blank" href="/api/files/'+encodeURIComponent(patientCode)+'/'+encodeURIComponent(fn)+'">'+fn+'</a>';
      }).join('<br>');
      box.style.display='block';
    }catch(e){box.innerHTML='خطا در دریافت فایل‌ها: '+e.message;box.style.display='block';}
  };
})();
