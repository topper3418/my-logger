
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

async function refreshViews() { 
    const now = new Date();
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    refreshTable(startOfDay.getTime(), now.getTime());
    refreshLogTree(startOfDay.getTime(), now.getTime());
    refreshCurrentActivity();
    populateLogTypeDropdown();
}

async function submitLog() {
    // get the text box and dropdown
    const textBox = document.getElementById('log-comment');
    const dropdown = document.getElementById('log-type-dropdown');
    // get the value of the text box and dropdown
    const comment = textBox.value;
    const logTypeId = dropdown.value;
    // send the value of the text box and dropdown to the server
    const response = await fetch(`/submit`, {
        method: 'POST',
        body: JSON.stringify({ 'log-comment': comment, 'log-type-id': logTypeId }),
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
        treeDiv.appendChild(makeLogElement(log));
    });
}

async function refreshLogTree(start_time, end_time) {
    const tree = await getLogTree(start_time, end_time);
    populateLogTree(tree);
}

async function getLogTypes() {
    const response = await fetch('/get_log_types');
    const types = await response.json();
    return types;
}

async function populateLogTypeList() {
    list = document.getElementById('log-types-list');
    list.innerHTML = '';
    const types = await getLogTypes();
    types.forEach(type => {
        const item = document.createElement('li');
        item.innerHTML = type.log_type;
        item.dataset.type_id = type.id;
        item.addEventListener('click', highlightItem);
        list.appendChild(item);
    });
}

async function populateLogTypeDropdown() {
    dropdown = document.getElementById('log-type-dropdown');
    dropdown.innerHTML = '';
    const types = await getLogTypes();
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type.id;
        option.innerHTML = type.log_type;
        dropdown.appendChild(option);
    });
}

// event listener to add "highlighted" to the classlist of the item clicked
function highlightItem(event) {
    const item = event.target;
    item.classList.toggle('highlighted');
}

function deleteHighlighted() {
    const highlighted = document.querySelectorAll('.highlighted');
    highlighted.forEach(item => {
        const id = item.dataset.type_id;
        fetch(`/delete_log_type?id=${id}`, {
            method: 'POST'
        });
    });
    populateLogTypeList();
}