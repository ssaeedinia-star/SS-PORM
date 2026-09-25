(function(){
  function collectForm(){
    const f=document.getElementById('f'),o={};
    if(!f)return null;
    for(const el of f.elements){
      if(!el.name||el.type==='file'||el.type==='button')continue;
      if(el.type==='checkbox')o[el.name]=el.checked;
      else if(el.type==='radio'){if(el.checked)o[el.name]=el.value;}
      else o[el.name]=el.value;
    }
    o.patient_code=(o.study_id||'').trim();
    const bmi=document.getElementById('bmi'),mfi=document.getElementById('mfi');
    o.BMI=bmi?bmi.textContent:'';
    o.mFI5=mfi?mfi.textContent:'';
    return o;
  }

  function clearMainFormAfterSave(){
    const f=document.getElementById('f');
    if(!f)return;
    f.reset();
    try{sessionStorage.removeItem('ssporm_main_form_draft_v1');}catch(_){}

    // Re-run the page's existing calculators/UI listeners after reset.
    for(const el of f.querySelectorAll('input,select,textarea')){
      try{el.dispatchEvent(new Event('input',{bubbles:true}));}catch(_){}
      try{el.dispatchEvent(new Event('change',{bubbles:true}));}catch(_){}
    }

    // Clear derived/read-only displays that may not be covered by listeners.
    const bmi=document.getElementById('bmi'); if(bmi)bmi.textContent='—';
    const mfi=document.getElementById('mfi'); if(mfi)mfi.textContent='0.00';
    const mfic=document.getElementById('mfic'); if(mfic)mfic.textContent='0';
    const loadStatus=document.getElementById('loadStatus'); if(loadStatus)loadStatus.textContent='';
    const patientFiles=document.getElementById('patientFiles'); if(patientFiles){patientFiles.innerHTML='';patientFiles.style.display='none';}
    try{window.scrollTo({top:0,behavior:'smooth'});}catch(_){window.scrollTo(0,0);}
  }

  window.savePatient=async function(){
    const o=collectForm();
    const s=document.getElementById('saveStatus'),b=document.getElementById('saveBtn');
    if(!o||!s||!b)return;
    s.style.display='block';
    if(!o.patient_code){s.textContent='ابتدا کد بیمار / کد مطالعه را وارد کنید.';return;}
    b.disabled=true;s.textContent='در حال ذخیره...';
    try{
      const r=await fetch('/api/patients',{
        method:'POST',
        credentials:'same-origin',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(o)
      });
      let d={};
      try{d=await r.json();}catch(_){throw new Error('پاسخ نامعتبر از سرور (HTTP '+r.status+')');}
      if(r.status===401)throw new Error('نشست ورود منقضی شده؛ یک‌بار خارج و دوباره وارد شوید.');
      if(!r.ok)throw new Error(d.error||('HTTP '+r.status));
      s.textContent='✓ اطلاعات بیمار با موفقیت ذخیره شد. ردیف پرونده: '+(d.row_number||'—');
      clearMainFormAfterSave();
      if(typeof window.refreshRecordNumber==='function')await window.refreshRecordNumber();
      if(typeof window.listPatients==='function')await window.listPatients();
    }catch(e){
      s.textContent='ذخیره انجام نشد: '+e.message;
    }finally{b.disabled=false;}
  };

  // The legacy page still points patient/file requests to the old Render backend.
  // Override file-list loading so every request stays on the current authenticated Liara origin.
  window.loadPatientFiles=async function(patientCode){
    const box=document.getElementById('patientFiles'); if(!box)return;
    try{
      const r=await fetch('/api/files/'+encodeURIComponent(patientCode),{credentials:'same-origin'});
      const d=await r.json();
      if(!r.ok)throw new Error(d.error||('HTTP '+r.status));
      const files=d.files||[];
      if(!files.length){box.innerHTML='<b>فایل‌های بیمار:</b><br>فایلی ثبت نشده است.';box.style.display='block';return;}
      box.innerHTML='<b>فایل‌های بیمار:</b><br>'+files.map(function(file){
        const fn=(typeof file==='string')?file:(file.filename||'');
        const title=(typeof file==='object'&&file.title)?file.title:fn;
        const href='/api/files/'+encodeURIComponent(patientCode)+'/'+encodeURIComponent(fn);
        return '<a target="_blank" href="'+href+'">'+String(title).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];})+'</a>';
      }).join('<br>');
      box.style.display='block';
    }catch(e){box.innerHTML='خطا در دریافت فایل‌ها: '+e.message;box.style.display='block';}
  };
})();
