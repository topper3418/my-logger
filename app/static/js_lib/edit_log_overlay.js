// Function to return the data from the overlay
function getOverlayData() {
    const parent_id = document.querySelector('#edit-parent-id').value;
    const log_type = document.querySelector('#edit-log-type-dropdown').value;
    const comment = document.querySelector('#edit-comment').value;
    const log_id = document.querySelector('#edit-log-id').value;
    return { comment, log_type, parent_id, log_id };
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