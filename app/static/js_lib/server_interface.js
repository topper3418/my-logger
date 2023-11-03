async function getLogs(start_time, end_time) {
    const response = await fetch(`/get_logs?start_time=${start_time}&end_time=${end_time}`);
    const logs = await response.json();
    return logs;
}


async function getAllLogs() {
    const response = await fetch('/get_logs');
    const logs = await response.json();
    return logs;
}


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


async function getLogTree(start_time, end_time) {
    // paramaters are start_time and end_time, midnight to now
    const response = await fetch(`/get_log_tree?start_time=${start_time}&end_time=${end_time}`);
    const tree = await response.json();
    return tree;
}


async function getLogTypes() {
    const response = await fetch('/get_log_types');
    const types = await response.json();
    return types;
}


async function getTodayData() {
    const now = new Date();
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const start_time = startOfDay.getTime();
    const end_time = now.getTime();
    const response = await fetch(`/get_logs?start_time=${start_time}&end_time=${end_time}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
}

async function getDataForDate(date) {
    console.log(date);
    // const startOfDay = new Date(date);
    // set the start time to midnight
    // startOfDay.setHours(0, 0, 0, 0);
    // const start_time = startOfDay.getTime();
    // const end_time = start_time + 86400000;
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

