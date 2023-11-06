async function getCurrentactivity() {
    const response = await fetch('/current_activity');
    const activity = await response.json();
    return activity;
}



// this needs to be split into getting the values and submitting them. 
async function submitLog() {
    // get the text box and dropdown
    const textBox = document.getElementById('log-comment');
    const dropdown = document.getElementById('log-type-dropdown');
    // get the value of the text box and dropdown
    const comment = textBox.value;
    const logType = dropdown.value;
    // send the value of the text box and dropdown to the server
    const response = await fetch(`/submit`, {
        method: 'POST',
        body: JSON.stringify({ 'log-comment': comment, 'log-type': logType }),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    // clear the text box
    textBox.value = '';
    // refresh the table
    refreshViews();
    return response;
}


async function getLogTypes() {
    const response = await fetch('/get_log_types');
    const types = await response.json();
    return types;
}

async function getDataForDate(date) {
    const response = await fetch(`/get_logs?target_date=${date}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
}


async function getLog(log_id) {
    const response = await fetch(`/log/${log_id}`);
    return await response.json();
}






