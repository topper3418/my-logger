
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
    refreshLogTree(startOfDay.getTime(), now.getTime());
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
    // clear the text box
    textBox.value = '';
    return response;
}

async function getLogTree(start_time, end_time) {
    // paramaters are start_time and end_time, midnight to now
    const response = await fetch(`/get_log_tree?start_time=${start_time}&end_time=${end_time}`);
    const tree = await response.json();
    console.log(tree);
    return tree;
}

// each parent is a div (flex column) wit a flex row at the top, giving the id and type and comment
//      make a function for returning an element with the proper nesting and class and text, given log data
//          that function should either return just the log, or wrap it in a div and recursively append children
//          That way I just iterate through the top level of the array and call the function on each one
// so it goes parent div (flex column) log element (just text) and then a flex row

function makeLogElement(log) {
    logText = `<b>${log.id}-${log.log_type}</b>: ${log.comment}`;
    const logElement = document.createElement('p');
    logElement.classList.add('log-element');
    logElement.innerHTML = logText;
    // determine if it has children
    if (log.children) {
        // if it has children, make a div for them and populate it
        const childrenDiv = document.createElement('div');
        childrenDiv.classList.add('children');
        log.children.forEach(child => {
            childrenDiv.appendChild(makeLogElement(child));
        });
        logElement.appendChild(childrenDiv);
    }
    return logElement;
}

function populateLogTree(tree) {
    const treeDiv = document.getElementById('log-tree');
    treeDiv.innerHTML = '';
    tree.forEach(log => {
        console.log(log);
        treeDiv.appendChild(makeLogElement(log));
    });
}

async function refreshLogTree(start_time, end_time) {
    const tree = await getLogTree(start_time, end_time);
    populateLogTree(tree);
}