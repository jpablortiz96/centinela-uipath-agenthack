let currentCaseId = null;

async function checkHealth() {
    try {
        const res = await fetch('/api/services/health');
        const data = await res.json();
        
        document.getElementById('status-core').textContent = data.core_banking;
        document.getElementById('status-core').className = data.core_banking === 'ok' ? 'status-ok' : 'status-down';
        
        document.getElementById('status-receiver').textContent = data.receiver_bank;
        document.getElementById('status-receiver').className = data.receiver_bank === 'ok' ? 'status-ok' : 'status-down';
        
        document.getElementById('status-fraud').textContent = data.fraud_investigator;
        document.getElementById('status-fraud').className = data.fraud_investigator === 'ok' ? 'status-ok' : 'status-down';
        
        document.getElementById('status-orch').textContent = data.case_orchestrator;
        document.getElementById('status-orch').className = data.case_orchestrator === 'ok' ? 'status-ok' : 'status-down';
    } catch (e) {
        console.error("Health check failed", e);
    }
}

document.getElementById('btn-refresh-health').addEventListener('click', checkHealth);

async function runScenario(scenario) {
    try {
        const res = await fetch(`/api/scenarios/${scenario}`, { method: 'POST' });
        const data = await res.json();
        updateCasePanel(data);
    } catch (e) {
        alert("Error running scenario: " + e);
    }
}

async function humanDecision(decision) {
    if (!currentCaseId) {
        alert("No active case!");
        return;
    }
    
    const payload = {
        decision: decision,
        analyst: "human-analyst-demo",
        notes: `Refund decision: ${decision} after reviewing evidence, risk signals, and audit trail.`
    };
    
    try {
        const res = await fetch(`/api/cases/${currentCaseId}/human-decision`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        updateCasePanel(data);
    } catch (e) {
        alert("Error submitting human decision: " + e);
    }
}

async function exportAudit() {
    if (!currentCaseId) {
        alert("No active case!");
        return;
    }
    try {
        const res = await fetch(`/api/cases/${currentCaseId}/export`);
        const data = await res.json();
        
        document.getElementById('raw-json').textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        alert("Error exporting audit: " + e);
    }
}

function updateCasePanel(data) {
    currentCaseId = data.case_id;
    document.getElementById('val-case-id').textContent = data.case_id || '-';
    document.getElementById('val-stage').textContent = data.current_stage || '-';
    document.getElementById('val-status').textContent = data.status || '-';
    
    let finalDec = "-";
    if (data.human_decision) finalDec = data.human_decision.decision;
    else if (data.investigation_result) finalDec = data.investigation_result.recommended_action;
    document.getElementById('val-final').textContent = finalDec;
    
    const inv = data.investigation_result || {};
    document.getElementById('val-risk-score').textContent = inv.risk_score !== undefined ? inv.risk_score : '-';
    document.getElementById('val-risk-level').textContent = inv.risk_level || '-';
    document.getElementById('val-action').textContent = inv.recommended_action || '-';
    document.getElementById('val-human-review').textContent = inv.human_review_required !== undefined ? inv.human_review_required : '-';
    
    // Update timeline
    const timelineDiv = document.getElementById('audit-timeline');
    timelineDiv.innerHTML = '';
    if (data.audit_events) {
        data.audit_events.forEach(evt => {
            const div = document.createElement('div');
            div.className = 'timeline-item';
            div.innerHTML = `<strong>${evt.timestamp}</strong><br>
                             Stage: ${evt.stage} | Actor: ${evt.actor}<br>
                             Event: <em>${evt.event}</em><br>
                             Details: ${JSON.stringify(evt.details)}`;
            timelineDiv.appendChild(div);
        });
    }
    
    document.getElementById('raw-json').textContent = JSON.stringify(data, null, 2);
}

// Initial fetch
checkHealth();
