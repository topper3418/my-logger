// Function to return the data from the overlay
function getOverlayData() {
    const parent_id = document.querySelector('#parent-id').value;
    const log_type = document.querySelector('#edit-log-type-dropdown').value;
    const comment = document.querySelector('#comment').value;
    const log_id = getOverlayElement().dataset.log_id;
    return { comment, log_type, parent_id, log_id };
}

// Function to populate the overlay with data
function populateOverlayData(data={}) {
    document.querySelector('#parent-id').value = data.parent_id;
    document.querySelector('#edit-log-type-dropdown').value = data.log_type;
    document.querySelector('#comment').value = data.comment;
    getOverlayElement().dataset.log_id = data.id;
}

// Function to hide the overlay
function hideOverlay() {
    getOverlayElement().style.display = 'none';
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
    await fetch(`/edit_log`, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    hideOverlay();
    refreshViews();
}