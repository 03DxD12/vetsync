

  function updateBreeds() {
    const animal = document.getElementById('animal_type').value;
    const breeds = breedsByAnimal[animal] || [];
    const sel = document.getElementById('breed');
    sel.innerHTML = breeds.map(b => `<option value="${b}">${b}</option>`).join('');
  }

  function setToggle(fieldId, value, btn) {
    document.getElementById(fieldId).value = value;
    const group = btn.closest('.toggle-group');
    group.querySelectorAll('.toggle-btn').forEach(b => {
      b.classList.remove('active-yes', 'active-no');
    });
    btn.classList.add(value === 'Yes' ? 'active-yes' : 'active-no');
  }

  // Initialize toggles — default all to "Yes"
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.toggle-group').forEach(group => {
      const firstBtn = group.querySelector('.toggle-btn');
      if (firstBtn) firstBtn.classList.add('active-yes');
    });
  });

  const SEV_COLORS = {
    critical: '#c1121f',
    high:     '#c1121f',
    medium:   '#e07a12',
    low:      '#2d6a4f',
  };

  const SEV_BAR = {
    critical: '#ef4444',
    high:     '#f87171',
    medium:   '#f59e0b',
    low:      '#52b788',
  };

  async function runPrediction() {
    const btn = document.getElementById('predict-btn');
    const errEl = document.getElementById('error-msg');
    errEl.style.display = 'none';

    btn.disabled = true;
    btn.innerHTML = `<div class="spinner"></div> Analyzing…`;

    const payload = {
      animal_type:        document.getElementById('animal_type').value,
      breed:              document.getElementById('breed').value,
      age:                document.getElementById('age').value,
      gender:             document.getElementById('gender').value,
      weight:             document.getElementById('weight').value,
      symptom_1:          document.getElementById('symptom_1').value,
      symptom_2:          document.getElementById('symptom_2').value,
      symptom_3:          document.getElementById('symptom_3').value,
      symptom_4:          document.getElementById('symptom_4').value,
      duration:           document.getElementById('duration').value,
      appetite_loss:      document.getElementById('appetite_loss').value,
      vomiting:           document.getElementById('vomiting').value,
      diarrhea:           document.getElementById('diarrhea').value,
      coughing:           document.getElementById('coughing').value,
      labored_breathing:  document.getElementById('labored_breathing').value,
      lameness:           document.getElementById('lameness').value,
      skin_lesions:       document.getElementById('skin_lesions').value,
      nasal_discharge:    document.getElementById('nasal_discharge').value,
      eye_discharge:      document.getElementById('eye_discharge').value,
      body_temperature:   document.getElementById('body_temperature').value,
      heart_rate:         document.getElementById('heart_rate').value,
    };

    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (!data.success) throw new Error(data.error || 'Prediction failed');
      renderResults(data.predictions, payload);

    } catch(e) {
      errEl.textContent = '⚠ ' + e.message;
      errEl.style.display = 'block';
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" stroke="white" fill="none" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Predict Disease`;
    }
  }

  function renderResults(predictions, form) {
    document.getElementById('placeholder').style.display = 'none';
    const content = document.getElementById('results-content');
    content.style.display = 'block';

    const top = predictions[0];
    const sevClass = `sev-${top.severity}`;

    let html = `
      <div class="prediction-header">
        <span class="prediction-label">Top Predictions</span>
        <span class="prediction-count">${predictions.length} result${predictions.length>1?'s':''}</span>
      </div>
    `;

    predictions.forEach((p, i) => {
      const barColor = SEV_BAR[p.severity] || '#52b788';
      const rankClass = i === 0 ? 'rank-1' : '';
      const rankBadge = i === 0 ? 'pred-rank-1' : '';
      const delay = i * 80;
      html += `
        <div class="pred-card ${rankClass}" style="animation-delay:${delay}ms">
          <div class="pred-top-row">
            <div class="pred-name">${p.disease}</div>
            <div class="pred-rank ${rankBadge}">#${i+1}</div>
          </div>
          <div class="conf-row">
            <div class="conf-bar-wrap">
              <div class="conf-bar" style="width:${p.confidence}%;background:${barColor}"></div>
            </div>
            <div class="conf-pct" style="color:${barColor}">${p.confidence}%</div>
          </div>
          <span class="severity-badge sev-${p.severity}">${p.severity} risk</span>
        </div>
      `;
    });

    // Summary box
    const signs = [];
    if (form.vomiting==='Yes') signs.push('vomiting');
    if (form.diarrhea==='Yes') signs.push('diarrhea');
    if (form.coughing==='Yes') signs.push('coughing');
    if (form.appetite_loss==='Yes') signs.push('appetite loss');
    if (form.labored_breathing==='Yes') signs.push('labored breathing');
    if (form.skin_lesions==='Yes') signs.push('skin lesions');

    html += `
      <div class="summary-box">
        <strong>${form.animal_type}</strong> · ${form.breed} · ${form.age}yr · ${form.weight}kg<br/>
        Primary: <strong>${form.symptom_1}</strong>${signs.length ? ` · Also: ${signs.join(', ')}` : ''}
      </div>
      <div class="disclaimer">⚕ For veterinary reference only. Always consult a licensed veterinarian.</div>
    `;

    content.innerHTML = html;
  }