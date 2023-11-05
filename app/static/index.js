
function populateCurrentActivity(activity) {
    //get the h2 with the id of current_activity
    const header = document.querySelector('#current_activity');
    header.innerHTML = 'Current Activity:';
    header.innerHTML += `<br>${activity}`;
}

async function refreshCurrentActivity() {
    const activity = await getCurrentactivity();
    populateCurrentActivity(activity);
}

async function refreshViews() { 
    refreshCurrentActivity();
    const target_date = document.getElementById('target-date').value;
    const tree_html = await getTreeHtml(target_date);
    const table_html = await getTableHtml(target_date);
    populateTree(tree_html);
    populateTable(table_html);
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