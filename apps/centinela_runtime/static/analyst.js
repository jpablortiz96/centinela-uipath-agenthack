document.addEventListener('DOMContentLoaded', () => {
    // Buttons
    const btnRefresh = document.getElementById('btn-refresh');
    const btnRunApiDown = document.getElementById('btn-run-api-down');
    const btnApprove = document.getElementById('btn-approve');
    const btnExport = document.getElementById('btn-export');

    // Attach events
    btnRefresh.addEventListener('click', fetchCases);
    btnRunApiDown.addEventListener('click', runApiDownCase);
    btnApprove.addEventListener('click', approveLatest);
    btnExport.addEventListener('click', exportLatest);

    // Initial load
    fetchCases();
    fetchLatestStats();
});

async function fetchCases() {
    try {
        const res = await fetch('/api/analyst/cases');
        if (!res.ok) throw new Error('Failed to fetch cases');
        const cases = await res.json();
        
        const tbody = document.getElementById('cases-body');
        tbody.innerHTML = '';
        
        cases.forEach(c => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${c.case_id}</td>
                <td>${c.status}</td>
                <td>${c.current_stage}</td>
                <td><span class="${getRiskColor(c.risk_level)}">${c.risk_level || '--'}</span></td>
                <td><button class="btn btn-small" onclick="viewCase('${c.case_id}')">View</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
        alert('Error fetching cases');
    }
}

async function fetchLatestStats() {
    try {
        const res = await fetch('/api/analyst/latest');
        if (res.ok) {
            const caseData = await res.json();
            updateStatusCards(caseData);
            renderCaseDetail(caseData);
        }
    } catch (e) {
        console.error('No latest case found', e);
    }
}

async function viewCase(caseId) {
    try {
        const res = await fetch(`/api/analyst/cases/${caseId}`);
        if (!res.ok) throw new Error('Failed to fetch case detail');
        const caseData = await res.json();
        updateStatusCards(caseData);
        renderCaseDetail(caseData);
    } catch (e) {
        console.error(e);
        alert('Error viewing case');
    }
}

async function runApiDownCase() {
    document.getElementById('btn-run-api-down').disabled = true;
    try {
        const res = await fetch('/api/analyst/run-api-down-case');
        if (!res.ok) throw new Error('Failed to run scenario');
        await fetchCases();
        await fetchLatestStats();
    } catch (e) {
        alert('Error running scenario');
    } finally {
        document.getElementById('btn-run-api-down').disabled = false;
    }
}

async function approveLatest() {
    document.getElementById('btn-approve').disabled = true;
    try {
        const res = await fetch('/api/analyst/approve-latest');
        const data = await res.json();
        if (!res.ok) {
            alert(data.message || 'Error approving');
        } else {
            alert(data.message);
            await fetchCases();
            await fetchLatestStats();
        }
    } catch (e) {
        alert('Error approving latest case');
    } finally {
        document.getElementById('btn-approve').disabled = false;
    }
}

async function exportLatest() {
    window.open('/api/analyst/export-latest', '_blank');
}

function updateStatusCards(data) {
    document.getElementById('latest-case-status').textContent = data.status || '--';
    
    const riskEl = document.getElementById('latest-risk-level');
    riskEl.textContent = data.risk_level || '--';
    riskEl.className = getRiskColor(data.risk_level);
    
    document.getElementById('latest-sla-status').textContent = (data.sla_summary && data.sla_summary.sla_status) || '--';
    
    const reqGate = data.policy_summary ? data.policy_summary.required_human_gate : '--';
    const gateEl = document.getElementById('latest-human-gate');
    gateEl.textContent = reqGate === true ? 'YES' : (reqGate === false ? 'NO' : '--');
    if(reqGate === true) gateEl.className = 'status-warn';
    else gateEl.className = '';
    
    document.getElementById('latest-retries').textContent = data.retry_attempts !== undefined ? data.retry_attempts : '--';
}

function renderCaseDetail(data) {
    document.getElementById('no-case-selected').style.display = 'none';
    document.getElementById('case-detail-view').style.display = 'block';
    
    document.getElementById('detail-case-id').textContent = data.case_id;
    document.getElementById('detail-stage').textContent = data.current_stage || '--';
    document.getElementById('detail-status').textContent = data.status || '--';
    document.getElementById('detail-risk-score').textContent = data.risk_score || '--';
    document.getElementById('detail-risk-level').textContent = data.risk_level || '--';
    document.getElementById('detail-recommended').textContent = data.recommended_action || '--';
    document.getElementById('detail-human-decision').textContent = data.human_decision || '--';
    document.getElementById('detail-sla-status').textContent = (data.sla_summary && data.sla_summary.sla_status) || '--';
    
    // Policy
    const polEl = document.getElementById('detail-policy-summary');
    if (data.policy_summary) {
        polEl.innerHTML = `
            <p><strong>Result:</strong> ${data.policy_summary.policy_result || '--'}</p>
            <p><strong>Reasons:</strong> ${data.policy_summary.policy_reasons ? data.policy_summary.policy_reasons.join(', ') : 'None'}</p>
        `;
    } else {
        polEl.innerHTML = '<p>No policy data</p>';
    }

    // Analyst Brief
    document.getElementById('detail-analyst-brief').innerHTML = data.analyst_brief ? `<p>${data.analyst_brief}</p>` : '<p>No brief available.</p>';
    
    // Customer Draft
    document.getElementById('detail-customer-draft').innerHTML = data.customer_response_draft ? `<p>${data.customer_response_draft}</p>` : '<p>No draft available.</p>';

    // Raw JSON
    document.getElementById('detail-raw-json').textContent = JSON.stringify(data, null, 2);

    // Timeline
    const tlEl = document.getElementById('detail-timeline');
    tlEl.innerHTML = '';
    if (data.timeline && Array.isArray(data.timeline)) {
        data.timeline.forEach(ev => {
            const type = ev.event_type || 'Unknown';
            let extraClass = '';
            if (type.includes('Retry')) extraClass = 'retry';
            if (type.includes('Human')) extraClass = 'human';
            
            const timeStr = ev.timestamp ? new Date(ev.timestamp).toLocaleString() : 'N/A';
            
            const div = document.createElement('div');
            div.className = `timeline-event ${extraClass}`;
            div.innerHTML = `
                <small>${timeStr}</small>
                <strong>${type}</strong>
                <pre>${JSON.stringify(ev.details, null, 2)}</pre>
            `;
            tlEl.appendChild(div);
        });
    } else {
        tlEl.innerHTML = '<p>No timeline data.</p>';
    }
}

function getRiskColor(level) {
    if (level === 'critical') return 'status-error';
    if (level === 'high') return 'status-warn';
    if (level === 'low') return 'status-ok';
    return '';
}
