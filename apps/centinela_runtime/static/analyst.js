document.addEventListener('DOMContentLoaded', () => {
    // Buttons
    const btnRefresh = document.getElementById('btn-refresh');
    const btnRunApiDown = document.getElementById('btn-run-api-down');
    const btnApprove = document.getElementById('btn-approve');
    const btnExport = document.getElementById('btn-export');
    const btnShowLatest = document.getElementById('btn-show-latest');

    // Attach events
    btnRefresh.addEventListener('click', fetchCases);
    btnRunApiDown.addEventListener('click', runApiDownCase);
    btnApprove.addEventListener('click', approveLatest);
    btnExport.addEventListener('click', exportLatest);
    btnShowLatest.addEventListener('click', fetchLatestStats);

    // Tab events
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
            btn.classList.add('active');
            document.getElementById(targetId).style.display = 'block';
        });
    });

    // Initial load
    fetchCases().then(() => fetchLatestStats());
});

let selectedCaseId = null;

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
                retryText = '3/3 (Max)';
            }
            
            let priorityBadgeClass = '';
            if (c.priority_level) {
                if (c.priority_level.includes('P0')) priorityBadgeClass = 'badge badge-retry'; // red/orange
                else if (c.priority_level.includes('P1')) priorityBadgeClass = 'badge badge-retry'; // orange
                else if (c.priority_level.includes('P2')) priorityBadgeClass = 'badge badge-external'; // gray/blue
                else priorityBadgeClass = 'badge badge-human'; // green
            }

            const tr = document.createElement('tr');
            tr.id = `row-${c.case_id}`;
            if (c.case_id === selectedCaseId) {
                tr.classList.add('selected-row');
            }
            
            tr.innerHTML = `
                <td style="font-family:monospace; font-size:0.8rem;">${c.case_id}</td>
                <td><span class="${priorityBadgeClass}">${c.priority_level || '--'}</span></td>
                <td>${c.status}</td>
                <td><span class="${getRiskColor(c.risk_level)}">${c.risk_level || '--'}</span></td>
                <td>${c.human_decision || '--'}</td>
                <td>${retryText}</td>
                <td>${c.source || '--'}</td>
                <td><button class="btn btn-small" onclick="selectCase('${c.case_id}')">View</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
    }
}

async function fetchLatestStats() {
    try {
        const res = await fetch('/api/analyst/latest');
        if (res.ok) {
            const caseData = await res.json();
            updateStatusCards(caseData);
            await selectCase(caseData.case_id);
        }
    } catch (e) {
        console.error('No latest case found', e);
    }
}

async function selectCase(caseId) {
    selectedCaseId = caseId;
    
    // Highlight row
    document.querySelectorAll('#cases-body tr').forEach(tr => tr.classList.remove('selected-row'));
    const row = document.getElementById(`row-${caseId}`);
    if (row) row.classList.add('selected-row');

    await viewCase(caseId);
}

async function viewCase(caseId) {
    try {
        const res = await fetch(`/api/analyst/cases/${caseId}`);
        if (!res.ok) throw new Error('Failed to fetch case detail');
        const caseData = await res.json();
        
        // Also update cards just to stay in sync with selected, though we might want cards to stay global
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
    document.getElementById('latest-case-outcome').textContent = data.status || '--';
    
    // Priority
    const ps = data.priority_summary || {};
    document.getElementById('latest-priority-level').textContent = ps.priority_level || '--';

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
        retryText = '3/3 (Max)';
    }
    document.getElementById('latest-retries').textContent = retryText;
}

function renderCaseDetail(data) {
    document.getElementById('no-case-selected').style.display = 'none';
    document.getElementById('case-detail-cols').style.display = 'contents';
    document.getElementById('lower-section').style.display = 'block';
    
    document.getElementById('detail-case-id').textContent = data.case_id;
    document.getElementById('detail-stage').textContent = data.current_stage || '--';
    document.getElementById('detail-status').textContent = data.status || '--';
    document.getElementById('detail-risk-score').textContent = data.risk_score || '--';
    document.getElementById('detail-risk-level').textContent = data.risk_level || '--';
    document.getElementById('detail-sla-status').textContent = (data.sla_summary && data.sla_summary.sla_status) || '--';
    
    // Policy
    const polEl = document.getElementById('detail-policy-summary');
    if (data.policy_summary) {
        polEl.innerHTML = `
            <div style="margin-bottom:5px;"><strong>Result:</strong> ${data.policy_summary.policy_result || '--'}</div>
            <div style="font-size:0.85em; color:var(--text-secondary);"><strong>Reasons:</strong> ${data.policy_summary.policy_reasons ? data.policy_summary.policy_reasons.join(', ') : 'None'}</div>
        `;
    } else {
        polEl.innerHTML = '<p>No policy data</p>';
    }

    // Analyst Brief
    document.getElementById('detail-analyst-brief').innerHTML = data.analyst_brief ? `<p>${data.analyst_brief}</p>` : '<p>No brief available.</p>';
    
    const qList = document.getElementById('detail-questions');
    qList.innerHTML = '';
    let questions = data.recommended_questions_for_analyst;
    if (!questions || questions.length === 0) {
        questions = [
            "Was the customer identity verified?",
            "Does the customer evidence match the disputed transaction?",
            "Was the receiver bank unavailable after all retry attempts?",
            "Should the refund be approved, rejected, or escalated?"
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
            span.className = 'badge badge-external'; 
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

    // Fraud Network Graph (SVG)
    const fnEl = document.getElementById('detail-fraud-network');
    fnEl.innerHTML = '';
    if (data.fraud_network && data.fraud_network.nodes) {
        let svg = '<svg width="100%" height="250" style="background:var(--bg-inner); border-radius:8px;">';
        const positions = {
            'customer': {x: 50, y: 125},
            'transaction': {x: 160, y: 125},
            'receiver_account': {x: 270, y: 125},
            'bank': {x: 380, y: 125},
            'risk_signal': {x: 380, y: 50},
            'control': {x: 215, y: 200}
        };
        
        let nodePos = {};
        data.fraud_network.nodes.forEach(n => {
            let pos = positions[n.type] || {x: Math.random()*300+50, y: Math.random()*200+50};
            nodePos[n.id] = pos;
        });

        // Draw edges
        data.fraud_network.edges.forEach(e => {
            const p1 = nodePos[e.from];
            const p2 = nodePos[e.to];
            if(p1 && p2) {
                svg += `<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="#475569" stroke-width="2"/>`;
                svg += `<text x="${(p1.x+p2.x)/2}" y="${(p1.y+p2.y)/2 - 5}" fill="#94a3b8" font-size="10" text-anchor="middle">${e.label}</text>`;
            }
        });

        // Draw nodes
        data.fraud_network.nodes.forEach(n => {
            const p = nodePos[n.id];
            let color = '#3b82f6';
            if (n.risk === 'critical') color = '#ef4444';
            else if (n.risk === 'high') color = '#f59e0b';
            
            svg += `<circle cx="${p.x}" cy="${p.y}" r="15" fill="${color}" stroke="#0f172a" stroke-width="2"/>`;
            svg += `<text x="${p.x}" y="${p.y + 25}" fill="#f8fafc" font-size="10" text-anchor="middle">${n.label}</text>`;
        });
        
        svg += '</svg>';
        fnEl.innerHTML = svg;
    } else {
        fnEl.innerHTML = '<p>No network graph available.</p>';
    }

    // Evidence Checklist
    const evEl = document.getElementById('detail-evidence-checklist');
    if (data.evidence_checklist && data.evidence_checklist.evidence_items) {
        let evHtml = `<div style="margin-bottom:10px;"><strong>Score: ${data.evidence_checklist.evidence_score}</strong></div><ul style="list-style:none; padding:0;">`;
        for (const [key, val] of Object.entries(data.evidence_checklist.evidence_items)) {
            let badgeClass = 'badge-external';
            if (val.status === 'present') badgeClass = 'badge-human';
            else if (val.status === 'missing') badgeClass = 'badge-retry';
            else if (val.status === 'failed') badgeClass = 'badge-retry'; 
            
            evHtml += `<li style="margin-bottom:8px; padding:8px; background:rgba(255,255,255,0.02); border-radius:4px; border-left:2px solid var(--border-color);">
                <span class="badge ${badgeClass}">${val.status}</span>
                <strong>${key}:</strong> <span style="color:#94a3b8; font-size:0.85em;">${val.note}</span>
            </li>`;
        }
        evHtml += '</ul>';
        evEl.innerHTML = evHtml;
    } else {
        evEl.innerHTML = '<p>No evidence checklist.</p>';
    }

    // Decision Simulator
    const dsEl = document.getElementById('detail-decision-simulator');
    if (data.decision_simulator) {
        let dsHtml = '<div style="display:flex; flex-direction:column; gap:10px;">';
        for (const [dec, impact] of Object.entries(data.decision_simulator)) {
            dsHtml += `
                <div style="border-left: 3px solid #3b82f6; padding-left: 10px; background: rgba(0,0,0,0.2); padding: 10px;">
                    <strong>${dec}</strong>
                    <ul style="font-size: 0.85em; color: #cbd5e1; margin-left: 20px; margin-top: 5px;">
                        <li>Impact: ${impact.customer_impact}</li>
                        <li>Financial: ${impact.financial_impact_cop} COP</li>
                        <li>Operational: ${impact.operational_impact}</li>
                        <li>Risk: ${impact.risk}</li>
                    </ul>
                </div>
            `;
        }
        dsHtml += '</div>';
        dsEl.innerHTML = dsHtml;
    } else {
        dsEl.innerHTML = '<p>No simulator available.</p>';
    }

    // Linked Signals
    const lsEl = document.getElementById('detail-linked-signals');
    if (data.linked_case_signals) {
        let lsHtml = '<ul style="list-style:none; padding:0;">';
        for (const [key, sig] of Object.entries(data.linked_case_signals)) {
            let statusBadge = sig.active ? '<span class="badge badge-retry">ACTIVE</span>' : '<span class="badge badge-external">INACTIVE</span>';
            lsHtml += `<li style="margin-bottom:10px; padding:8px; background:rgba(255,255,255,0.02); border-radius:4px;">
                <div style="margin-bottom:4px;">${statusBadge} <strong>${key}</strong></div>
                <div style="color:#94a3b8; font-size:0.85em;">${sig.note}</div>
            </li>`;
        }
        lsHtml += '</ul>';
        lsEl.innerHTML = lsHtml;
    } else {
        lsEl.innerHTML = '<p>No linked signals.</p>';
    }

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
