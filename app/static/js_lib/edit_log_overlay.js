// Function to return the data from the overlay
function getOverlayData() {
    const parent_id = document.querySelector('#parent-id').value;
    const log_type = document.querySelector('#edit-log-type-dropdown').value;
    const comment = document.querySelector('#comment').value;
    const log_id = getOverlayElement().dataset.log_id;
    return { comment, log_type, parent_id, log_id };
}

async function renderOverlay(logId) {
    // get the log data
    const overlay_html = await fetch(`/edit_log/${logId}`).then(response => response.text());
    // set the overlay html
    getOverlayElement().innerHTML = overlay_html;
    // show the overlay
    console.log(getOverlayElement());
    showOverlay();
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

// function to get the submit button
function getSubmitButton() {
    let overlay_element = getOverlayElement();
    return overlay_element.querySelector('#submit-edit-button');
}

// Function to for the submit button
async function submitEdit() {
    const data = getOverlayData();
    console.log(data);
    log_id = data.log_id;
    await fetch(`/edit_log/${log_id}`, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    hideOverlay();
    refreshViews();
}