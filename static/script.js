
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
    // reverse the order of logs
    logs.reverse();
    logs.forEach(log => {
        const row = document.createElement('tr');

        timestamp_cell = document.createElement('td');
        timestamp_cell.innerHTML = log.timestamp;
        timestamp_cell.style.textAlign = 'right';
        row.appendChild(timestamp_cell);

        parent_cell = document.createElement('td');

        comment_cell = document.createElement('td');
        comment_cell.innerHTML = log.comment;
        comment_cell.style.color = getColor(log);
        row.appendChild(comment_cell);

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
    console.log('refreshing current activity')
    refreshCurrentActivity();
    console.log('refreshing dropdown')
    populateLogTypeDropdown();
    console.log('refreshing log table')
    refreshTable(startOfDay.getTime(), now.getTime());
    console.log('refreshing log tree')
    refreshLogTree(startOfDay.getTime(), now.getTime());
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

function collapseChildren(event) {
    // get the parent element
    const parent = event.target.parentElement.parentElement;
    // get the element with the class of children
    const children = parent.querySelector('.children');
    // toggle the class of hidden
    children.classList.toggle('hidden');
    parent.classList.toggle('bordered');
}

function getColor(log) {
    const dropdown = document.getElementById('log-type-dropdown');
    storedTypes = JSON.parse(dropdown.dataset.log_types);
    const logType = log.log_type;
    const typeColor = storedTypes.find(item => item.log_type === logType).color;
    return typeColor;
}

function makeLogTreeElement(log) {
    const logElement = document.createElement('p');
    logElement.classList.add('log-element');
    logElement.dataset.log_id = log.id;
    logElement.style.color = getColor(log);

    const treeDiv = document.getElementById('log-tree');
    const collapsedIds = treeDiv.dataset.collapsed.split(',');
    
    const logTypeElement = document.createElement('span');
    logTypeElement.innerHTML = `<b>${log.id}</b>: `;
    logTypeElement.addEventListener('click', collapseChildren);
    
    const logCommentElement = document.createElement('span');
    logCommentElement.innerHTML = log.comment;
    
    logElement.appendChild(logTypeElement);
    logElement.appendChild(logCommentElement);
    
    // determine if it has children
    if (log.children) {
        // if it has children, make a div for them and populate it
        const childrenDiv = document.createElement('div');
        childrenDiv.classList.add('children');
        log.children.forEach(child => {
            childrenDiv.appendChild(makeLogTreeElement(child));
        });
        logElement.appendChild(childrenDiv);
    }

    if (collapsedIds.includes(log.id.toString())) {
        logElement.querySelector('.children').classList.toggle('hidden');
        logElement.classList.toggle('bordered');
    }
    
    return logElement;
}


function populateLogTree(tree) {
    const treeDiv = document.getElementById('log-tree');
    // get the log id's of collapsed elements
    const collapsed = document.querySelectorAll('.children.hidden');
    const collapsedIds = [];
    collapsed.forEach(element => {
        collapsedIds.push(element.parentElement.dataset.log_id);
    });
    treeDiv.innerHTML = '';
    treeDiv.dataset.collapsed = collapsedIds;
    tree.forEach(log => {
        treeDiv.appendChild(makeLogTreeElement(log));
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
        item.style.color = type.color; // set the color of the list item
        item.addEventListener('click', highlightItem);
        list.appendChild(item);
    });
}

async function populateLogTypeDropdown() {
    dropdown = document.getElementById('log-type-dropdown');
    dropdown.innerHTML = '';
    const types = await getLogTypes();
    dropdown.dataset.log_types = JSON.stringify(types);
    console.log(types);
    console.log(dropdown.dataset.log_types);
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

