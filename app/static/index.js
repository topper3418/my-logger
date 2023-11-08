async function getCurrentActivityHtml() {
    const response = await fetch('/current_activity');
    const html = await response.text();
    return html;
}


function populateCurrentActivity(activity) {
    //get the h2 with the id of current_activity
    const CADiv = document.querySelector('#current_activity');
    //set the innerHTML of that div to the activity
    CADiv.innerHTML = activity;
}

async function refreshCurrentActivity() {
    const activity = await getCurrentActivityHtml();
    populateCurrentActivity(activity);
}

async function switchToParent(parent_id) {
    console.log(parent_id);
    const response = await fetch(`/submit`, {
        method: 'POST',
        body: JSON.stringify({ 'log-comment': `[${parent_id}]`}),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    refreshViews();
}

async function refreshViews() { 
    const target_date = document.getElementById('target-date').value;
    const tree_html = await getTreeHtml(target_date);
    const table_html = await getTableHtml(target_date);
    const activity = await getCurrentActivityHtml();
    populateTree(tree_html, document.getElementById('log-tree'));
    populateTable(table_html);
    populateCurrentActivity(activity);
}


// Function to hide the overlay
function hideOverlay() {
    getOverlayElement().style.display = 'none';
}

// Function to Remove the overlay
function removeOverlay() {
    getOverlayElement().innerHTML = '';
    hideOverlay();
}

// Function to show the overlay
function showOverlay() {
    getOverlayElement().style.display = 'block';
}

// Function to return the overlay element
function getOverlayElement() {
    return document.getElementById('overlay');
}