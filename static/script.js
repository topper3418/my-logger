
async function getLogs(start_time, end_time) {
    const response = await fetch(`/get_logs?start_time=${start_time}&end_time=${end_time}`);
    const logs = await response.json();
    console.log(logs);
    return logs;
}

async function getAllLogs() {
    const response = await fetch('/get_logs');
    const logs = await response.json();
    console.log(logs);
    return logs;
}

async function getCurrentactivity() {
    const response = await fetch('/current_activity');
    const activity = await response.json();
    console.log('current activity', activity);
    return activity;
}

function populateTable(logs) {
    const tableBody = document.querySelector('#log-table tbody');
    tableBody.innerHTML = '';
    logs.forEach(log => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${log.id}</td>
            <td>${log.timestamp}</td>
            <td>${log.log_type}</td>
            <td>${log.comment}</td>
            <td>${log.parent_id}</td>
        `;
        tableBody.appendChild(row);
    });
}

function populateCurrentActivity(activity) {
    //get the h2 with the id of current_activity
    const header = document.querySelector('#current_activity');
    header.innerHTML = 'Current Activity:';
    header.innerHTML += `<br>${activity}`;
}

async function refreshTable(start_time, end_time) {
    const logs = await getLogs(start_time, end_time);
    //const logs = await getAllLogs();
    populateTable(logs);
}

async function refreshCurrentActivity() {
    const activity = await getCurrentactivity();
    populateCurrentActivity(activity);
}

async function logClick() {
    await submitLog();
    const now = new Date();
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    refreshTable(startOfDay.getTime(), now.getTime());
    refreshCurrentActivity();
}

async function submitLog() {
    // get the text box and dropdown
    const textBox = document.getElementById('log-comment');
    const dropdown = document.getElementById('log-type');
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
    console.log(response);
    // clear the text box
    textBox.value = '';
    return response;
}

