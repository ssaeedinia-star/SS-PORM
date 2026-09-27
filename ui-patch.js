(function(){
  function esc(v){return String(v||'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function code(){var f=document.getElementById('f');var e=f&&f.elements&&f.elements['study_id'];return e?String(e.value||'').trim():'';}
  function openCervical(){var c=code();if(!c){alert('ابتدا کد بیمار / کد مطالعه را وارد کنید.');return;}window.open('/cervical?patient_code='+encodeURIComponent(c),'ssporm_cervical_'+c,'width=850,height=900,scrollbars=yes');}
  function cardByTitle(f,text){
    var cards=f.querySelectorAll('.card');
    for(var i=0;i<cards.length;i++){
      var h=cards[i].querySelector('h2');
      if(h&&(h.textContent||'').indexOf(text)>=0)return cards[i];
    }
    return null;
  }
  function makeLabsMedsCollapsible(f){
    var card=cardByTitle(f,'آزمایش‌ها و داروهای مهم');
    if(!card||card.dataset.collapsibleReady)return;
    card.dataset.collapsibleReady='1';
    var h=card.querySelector('h2');
    var details=document.createElement('details');
    details.className='labs-meds-folder';
    var summary=document.createElement('summary');
    summary.innerHTML='🧪💊 <b>آزمایش‌ها و داروهای مهم</b> <span class="small">Core / Extended</span>';
    summary.style.cursor='pointer';summary.style.fontSize='20px';summary.style.padding='6px 0';
    details.appendChild(summary);
    var body=document.createElement('div');body.style.marginTop='12px';
    Array.from(card.childNodes).forEach(function(n){if(n!==h)body.appendChild(n);});
    details.appendChild(body);card.innerHTML='';card.appendChild(details);
  }
  function reorderAssessmentSections(f){
    var base=cardByTitle(f,'مشخصات پایه');
    if(!base)return;
    var ordered=[
      cardByTitle(f,'بیماری‌های همراه'),
      cardByTitle(f,'Frailty و ASA'),
      cardByTitle(f,'Persian Modified Oswestry Disability Questionnaire'),
      document.getElementById('cervicalModuleCard')
    ].filter(Boolean);
    var anchor=base;
    ordered.forEach(function(card){anchor.insertAdjacentElement('afterend',card);anchor=card;});
  }
  function install(){
    var f=document.getElementById('f');if(!f)return;
    var first=f.querySelector('.card');
    if(first&&!f.elements['patient_phone']){
      var phone=document.createElement('div');phone.className='row';phone.innerHTML='<div><label>شماره تماس بیمار</label><input type="tel" name="patient_phone" inputmode="tel" autocomplete="tel" placeholder="مثال: 0912xxxxxxx"></div>';
      var pname=first.querySelector('input[name="patient_name"]');if(pname){var anchor=pname.closest('.row')||pname;anchor.insertAdjacentElement('afterend',phone);}else first.appendChild(phone);
    }
    var card=document.getElementById('cervicalModuleCard');
    if(!card){
      card=document.createElement('div');card.id='cervicalModuleCard';card.className='card';card.innerHTML='<h2>📁 ماژول بیماران گردنی</h2><p class="small">معاینه اختصاصی گردن، NDI و mJOA در پوشه اختصاصی بیمار ثبت می‌شوند.</p><button type="button" id="openCervicalModule">باز کردن پوشه بیماران گردنی</button><div class="out" style="margin-top:10px">NDI: <b id="cervicalNdiSummary">—</b> &nbsp; | &nbsp; mJOA: <b id="cervicalMjoaSummary">—</b></div>';
      if(first)first.insertAdjacentElement('afterend',card);else f.insertBefore(card,f.firstChild);
      document.getElementById('openCervicalModule').onclick=openCervical;
      document.querySelectorAll('.card').forEach(function(x){if(x===card)return;var h=x.querySelector('h2');if(!h)return;var t=(h.textContent||'').toLowerCase();if(t.indexOf('ndi')>=0||t.indexOf('mjoa')>=0)x.style.display='none';});
      window.addEventListener('message',function(e){if(e.origin!==location.origin||!e.data)return;if(e.data.type==='ssporm-cervical'){if(e.data.ndi!=null)document.getElementById('cervicalNdiSummary').textContent=e.data.ndi;if(e.data.mjoa!=null)document.getElementById('cervicalMjoaSummary').textContent=e.data.mjoa;}});
    }
    reorderAssessmentSections(f);
    makeLabsMedsCollapsible(f);
  }
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',install):install();setTimeout(install,700);
})();