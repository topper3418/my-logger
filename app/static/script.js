
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
    refreshCurrentActivity();
    populateLogTypeDropdown();
    refreshTable(startOfDay.getTime(), now.getTime());
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
    refreshViewsV2();
    return response;
}

async function getLogTree(start_time, end_time) {
    // paramaters are start_time and end_time, midnight to now
    const response = await fetch(`/get_log_tree?start_time=${start_time}&end_time=${end_time}`);
    const tree = await response.json();
    return tree;
}

function collapseChildrenHelper(element) {
    children = element.querySelector('.children');
    // if its hidden, show it and set the time to be the non-cumulative time
    logDurationElement = element.querySelector('.duration');
    if (children.classList.contains('hidden')) {
        logDurationElement.innerHTML = formatSeconds(logDurationElement.dataset.time_spent);
    } else {
        logDurationElement.innerHTML = formatSeconds(logDurationElement.dataset.total_time_spent);
    }
    children.classList.toggle('hidden');
    element.classList.toggle('bordered');
}

function collapseChildren(event) {
    // get the parent element
    const parent = event.target.parentElement.parentElement.parentElement;
    collapseChildrenHelper(parent);
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
    
    const logIdElement = document.createElement('span');
    logIdElement.innerHTML = `<b>${log.id}</b>: `;
    logIdElement.style.cursor = 'pointer';
    if (log.complete) {
        logIdElement.style.color = 'green';
    }
    logIdElement.addEventListener('click', collapseChildren);
    
    const logCommentElement = document.createElement('span');
    logCommentElement.innerHTML = log.comment;
    
    logElement.appendChild(logIdElement);
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

async function getTodayData() {
    const now = new Date();
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const start_time = startOfDay.getTime();
    const end_time = now.getTime();
    const response = await fetch(`/get_logs_v2?start_time=${start_time}&end_time=${end_time}`);
    return await response.json();
}

function populateTableV2(todayData) {
    const tableBody = document.querySelector('#log-table tbody');
    tableBody.innerHTML = '';
    // reverse the order of logs
    todayData.reverse();
    todayData.forEach(log => {
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

function makeLogTreeElementV2(log) {
    // create the wrapper that it will all go in
    const logWrapper = document.createElement('div');
    logWrapper.classList.add('column-container');
    // create the element that will hold the log
    const logElement = document.createElement('div');
    logElement.classList.add('row-cluster');
    logElement.classList.add('log-element');
    logElement.dataset.log_id = log.id;
    logElement.style.color = getColor(log);
    logWrapper.appendChild(logElement);
    // get the collapsed ids
    const treeDiv = document.getElementById('log-tree');
    if (!treeDiv.dataset.collapsed) {
        treeDiv.dataset.collapsed = '';
    }
    const collapsedIds = treeDiv.dataset.collapsed.split(',');
    // create the elements that will go in the log element
    // id element
    const logIdElement = document.createElement('p');
    logIdElement.innerHTML = `<b>${log.id}</b>: `;
    logIdElement.style.cursor = 'pointer';
    if (log.complete) {
        logIdElement.style.color = 'green';
    }
    logIdElement.addEventListener('click', collapseChildren);
    // duration element
    const logDurationElement = document.createElement('p');
    logDurationElement.classList.add('duration');
    logDurationElement.innerHTML = formatSeconds(log.time_spent);
    logDurationElement.dataset.time_spent = log.time_spent;
    logDurationElement.dataset.total_time_spent = log.total_time_spent;
    // comment element
    const logCommentElement = document.createElement('p');
    logCommentElement.innerHTML = log.comment;
    logCommentElement.style.flexGrow = 1;
    // remove margins and padding
    logIdElement.style.margin = '0';
    logIdElement.style.padding = '0';
    logIdElement.style.marginRight = '15px';
    logDurationElement.style.margin = '0';
    logDurationElement.style.padding = '0';
    logDurationElement.style.marginLeft = '15px';
    logCommentElement.style.margin = '0';
    logCommentElement.style.padding = '0';
    // append the elements to the log element
    logElement.appendChild(logIdElement);
    logElement.appendChild(logCommentElement);
    logElement.appendChild(logDurationElement);
    
    // determine if it has children, add them recursively
    if (log.children) {
        // if it has children, make a div for them and populate it
        const childrenDiv = document.createElement('div');
        childrenDiv.classList.add('children');
        log.children.forEach(child => {
            childrenDiv.appendChild(makeLogTreeElementV2(child));
        });
        logWrapper.appendChild(childrenDiv);
    }

    if (collapsedIds.includes(log.id.toString())) {
        collapseChildrenHelper(logElement);
    }
    
    return logWrapper;
}

function get_children(log, todayData) {
    const children = todayData.filter(item => item.parent_id === log.id);
    children.forEach(child => {
        child.children = get_children(child, todayData);
    });
    return children;
}

function sum_time(tree_log) {
    let time = tree_log.time_spent;
    if (tree_log.children) {
        tree_log.children.forEach(child => {
            sum_time(child);
            time += child.total_time_spent;
        });
    }
    tree_log.total_time_spent = time;
}

function get_orphans(todayData) {
    const orphans = [];
    todayData.forEach(log => {
        // if no parent id, or parent id not in data
        if (!log.parent_id || !todayData.find(item => item.id === log.parent_id)) {
            orphans.push(log);
        }
    }
    );
    return orphans;
}

function make_into_tree(todayData) {
    const tree = get_orphans(todayData);
    tree.forEach(log => {
        log.children = get_children(log, todayData);
    });
    // loop through again, getting cumulative time
    tree.forEach(log => {
        sum_time(log);
    });
    console.log(tree);
    return tree;
}

function populateTreeV2(todayData) {
    const treeDiv = document.getElementById('log-tree');
    const collapsed = document.querySelectorAll('.children.hidden');
    const collapsedIds = [];
    collapsed.forEach(element => {
        collapsedIds.push(element.parentElement.querySelector('.log-element').dataset.log_id);
    });
    treeDiv.innerHTML = '';
    treeDiv.dataset.collapsed = collapsedIds;
    treeData = make_into_tree(todayData);
    treeData.forEach(log => {
        treeDiv.appendChild(makeLogTreeElementV2(log));
    });
}

async function refreshViewsV2() { 
    const now = new Date();
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    refreshCurrentActivity();
    populateLogTypeDropdown();
    const todayData = await getTodayData();
    populateTreeV2(todayData);
    populateTableV2(todayData);
}

function formatSeconds(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const formattedHours = hours.toString().padStart(2, '0');
    const formattedMinutes = minutes.toString().padStart(2, '0');
    return `${formattedHours}:${formattedMinutes}`;
}