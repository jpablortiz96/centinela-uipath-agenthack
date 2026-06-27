function log(msg, data = null) {
    const el = document.getElementById('execution-log');
    let text = `[${new Date().toLocaleTimeString()}] ${msg}\n`;
    if (data) text += JSON.stringify(data, null, 2) + '\n';
    el.textContent = text + '\n' + el.textContent;
}

document.getElementById('btn-step1').addEventListener('click', async () => {
    document.getElementById('btn-step1').disabled = true;
    log('Running Step 1: /api/analyst/run-api-down-case...');
    try {
        const res = await fetch('/api/analyst/run-api-down-case');
        const data = await res.json();
        log('Step 1 complete.', data);
        
        const content = document.getElementById('content-step1');
        content.innerHTML = `<div style="margin-bottom:8px;"><strong>Status:</strong> <span style="color:var(--success)">${data.status}</span></div><div><strong>Business Meaning:</strong> Maestro simulates an instant payment dispute. The receiver bank API fails to respond after all retries, forcing a human gate.</div>`;
        content.classList.add('active');
        
        document.getElementById('btn-step2').disabled = false;
    } catch (e) {
        log('Error: ' + e);
        document.getElementById('btn-step1').disabled = false;
    }
});

document.getElementById('btn-step2').addEventListener('click', async () => {
    document.getElementById('btn-step2').disabled = true;
    log('Running Step 2: Fetching latest case state...');
    try {
        const res = await fetch('/api/analyst/latest');
        const data = await res.json();
        const retries = data.timeline ? data.timeline.filter(e => e.event_type === 'ReceiverBankRetryAttempted').length : 0;
        log('Step 2 complete.', { risk: data.risk_summary, retries: retries });
        
        const content = document.getElementById('content-step2');
        content.innerHTML = `<div style="margin-bottom:8px;"><strong>Risk Level:</strong> <span style="color:var(--danger)">${data.risk_summary ? data.risk_summary.risk_level : 'unknown'}</span></div><div><strong>Business Meaning:</strong> The policy engine evaluates the risk as critical because the receiver bank is offline, blocking auto-resolution.</div>`;
        content.classList.add('active');
        
        document.getElementById('btn-step3').disabled = false;
    } catch (e) {
        log('Error: ' + e);
        document.getElementById('btn-step2').disabled = false;
    }
});

document.getElementById('btn-step3').addEventListener('click', async () => {
    document.getElementById('btn-step3').disabled = true;
    log('Running Step 3: /api/analyst/approve-latest...');
    try {
        const res = await fetch('/api/analyst/approve-latest');
        const data = await res.json();
        log('Step 3 complete.', data);
        
        const content = document.getElementById('content-step3');
        content.innerHTML = `<div style="margin-bottom:8px;"><strong>Action:</strong> <span style="color:var(--accent-blue)">${data.message}</span></div><div><strong>Business Meaning:</strong> The human analyst (or judge) approves the refund via the Maestro Action Center equivalent. The case transitions to resolved_by_human.</div>`;
        content.classList.add('active');
        
        document.getElementById('btn-step4').disabled = false;
    } catch (e) {
        log('Error: ' + e);
        document.getElementById('btn-step3').disabled = false;
    }
});

document.getElementById('btn-step4').addEventListener('click', async () => {
    document.getElementById('btn-step4').disabled = true;
    log('Running Step 4: /api/analyst/export-latest...');
    try {
        const res = await fetch('/api/analyst/export-latest');
        const data = await res.json();
        log('Step 4 complete. Audit package size: ' + JSON.stringify(data).length + ' bytes');
        
        const content = document.getElementById('content-step4');
        content.innerHTML = `<div style="margin-bottom:8px;"><strong>Exported Case:</strong> <span style="font-family:monospace; color:var(--text-primary)">${data.case_id}</span></div><div><strong>Business Meaning:</strong> Maestro fetches the final immutable audit trail (including timeline, fraud network, simulator, and SLA) to close the case in UiPath.</div>`;
        content.classList.add('active');
        
        document.getElementById('btn-step5').disabled = false;
    } catch (e) {
        log('Error: ' + e);
        document.getElementById('btn-step4').disabled = false;
    }
});

document.getElementById('btn-step5').addEventListener('click', () => {
    window.open('/analyst', '_blank');
});

document.getElementById('btn-full-replay').addEventListener('click', async () => {
    document.getElementById('btn-full-replay').disabled = true;
    log('Running Full Replay via /api/judge/replay...');
    try {
        const res = await fetch('/api/judge/replay');
        const data = await res.json();
        log('Full Replay complete.', data);
        
        const resEl = document.getElementById('full-replay-result');
        resEl.style.display = 'block';
        resEl.innerHTML = `
            <strong>Case ID:</strong> <span style="font-family:monospace;">${data.case_id}</span><br>
            <strong>Status:</strong> ${data.status}<br>
            <strong>Decision:</strong> ${data.human_decision}<br>
            <strong>Risk:</strong> ${data.risk_score} (${data.risk_level})<br>
            <strong>Retries:</strong> ${data.retry_event_count}<br>
            <strong>Events:</strong> ${data.audit_event_count}<br>
            <strong>Reasons:</strong>
            <ul>${data.policy_reasons.map(r => `<li>${r}</li>`).join('')}</ul>
        `;
    } catch (e) {
        log('Full Replay failed: ' + e);
    } finally {
        document.getElementById('btn-full-replay').disabled = false;
    }
});
