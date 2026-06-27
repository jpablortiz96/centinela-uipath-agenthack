document.addEventListener('DOMContentLoaded', () => {
    // Buttons
    const btnRefresh = document.getElementById('btn-refresh');
    const btnRunApiDown = document.getElementById('btn-run-api-down');
    const btnApprove = document.getElementById('btn-approve');
    const btnExport = document.getElementById('btn-export');
    const rawJsonHeader = document.getElementById('raw-json-header');

    // Attach events
    btnRefresh.addEventListener('click', fetchCases);
    btnRunApiDown.addEventListener('click', runApiDownCase);
    btnApprove.addEventListener('click', approveLatest);
    btnExport.addEventListener('click', exportLatest);
    rawJsonHeader.addEventListener('click', () => {
        const content = document.getElementById('raw-json-content');
        if (content.style.display === 'none') {
            content.style.display = 'block';
            rawJsonHeader.querySelector('span').textContent = '▲';
        } else {
            content.style.display = 'none';
            rawJsonHeader.querySelector('span').textContent = '▼';
        }
    });

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
            const retries = c.retry_attempts !== undefined ? c.retry_attempts : 0;
            let retryText = retries.toString();
            if (retries >= 3) {
                retryText = '3 / 3 (Exhausted)';
            } else if (retries === 0) {
                retryText = '0';
            }
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${c.case_id}</td>
                <td>${c.status}</td>
                <td>${c.current_stage}</td>
                <td><span class="${getRiskColor(c.risk_level)}">${c.risk_level || '--'}</span></td>
                <td>${c.human_decision || '--'}</td>
                <td>${c.source || '--'}</td>
                <td>${retryText}</td>
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

function countRetries(timeline) {
    if (!timeline || !Array.isArray(timeline)) return 0;
    return timeline.filter(ev => ev.event_type === 'ReceiverBankRetryAttempted').length;
}

function updateStatusCards(data) {
    document.getElementById('latest-case-status').textContent = data.status || '--';
    document.getElementById('latest-case-outcome').textContent = data.status || '--';
    
    const riskEl = document.getElementById('latest-risk-level');
    riskEl.textContent = data.risk_level || '--';
    riskEl.className = getRiskColor(data.risk_level);
    
    document.getElementById('latest-sla-status').textContent = (data.sla_summary && data.sla_summary.sla_status) || '--';
    
    // Human Gate Logic
    const gateEl = document.getElementById('latest-human-gate');
    let gateStatus = '--';
    if (data.status === 'waiting_for_human') {
        gateStatus = 'Required';
        gateEl.className = 'status-warn';
    } else if (data.status === 'resolved_by_human' || data.status === 'escalated_to_fraud_ops' || data.status === 'waiting_for_evidence') {
        gateStatus = 'Applied';
        gateEl.className = 'status-ok';
    } else if (data.status === 'auto_resolved') {
        gateStatus = 'Not required';
        gateEl.className = '';
    } else {
        gateEl.className = '';
    }
    gateEl.textContent = gateStatus;
    
    // Retry logic
    const retries = countRetries(data.timeline);
    let retryText = retries.toString();
    if (retries >= 3) {
        retryText = '3 / 3 (Exhausted)';
    }
    document.getElementById('latest-retries').textContent = retryText;
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
    document.getElementById('detail-evidence-summary').textContent = data.evidence_summary || '--';
    document.getElementById('detail-risk-explanation').textContent = data.risk_explanation || '--';
    
    const qList = document.getElementById('detail-questions');
    qList.innerHTML = '';
    
    // Check if questions exist and are populated, otherwise use deterministic defaults
    let questions = data.recommended_questions_for_analyst;
    if (!questions || questions.length === 0) {
        questions = [
            "Was the customer identity verified?",
            "Does the customer evidence match the disputed transaction?",
            "Was the receiver bank unavailable after all retry attempts?",
            "Should the refund be approved, rejected, or escalated to fraud operations?"
        ];
    }
    
    questions.forEach(q => {
        const li = document.createElement('li');
        li.textContent = q;
        qList.appendChild(li);
    });
    
    const allowedDecisionsEl = document.getElementById('detail-allowed-decisions');
    allowedDecisionsEl.innerHTML = '';
    if (data.allowed_decisions && data.allowed_decisions.length > 0) {
        data.allowed_decisions.forEach(dec => {
            const span = document.createElement('span');
            span.className = 'badge badge-external'; // Reuse visual style
            span.style.marginRight = '5px';
            span.textContent = dec;
            allowedDecisionsEl.appendChild(span);
        });
    } else {
        allowedDecisionsEl.textContent = '--';
    }
    
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
            let badgeHtml = '';
            
            if (type.includes('Retry')) {
                extraClass = 'retry';
                badgeHtml = '<span class="badge badge-retry">Retry</span>';
            } else if (type.includes('Human')) {
                extraClass = 'human';
                badgeHtml = '<span class="badge badge-human">Human Decision</span>';
            } else if (type.includes('Resolution')) {
                extraClass = 'resolution';
                badgeHtml = '<span class="badge badge-resolution">Resolution</span>';
            } else if (type.includes('Policy') || type.includes('Stage')) {
                extraClass = 'policy';
                badgeHtml = '<span class="badge badge-policy">Policy/Stage</span>';
            } else if (type.includes('Check') || type.includes('Bank')) {
                extraClass = 'external';
                badgeHtml = '<span class="badge badge-external">External Check</span>';
            }
            
            const timeStr = ev.timestamp ? new Date(ev.timestamp).toLocaleString() : 'N/A';
            
            const div = document.createElement('div');
            div.className = `timeline-event ${extraClass}`;
            div.innerHTML = `
                <small>${timeStr}</small>
                <strong>${type} ${badgeHtml}</strong>
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
