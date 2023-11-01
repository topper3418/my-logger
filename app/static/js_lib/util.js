
function formatSeconds(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const formattedHours = hours.toString().padStart(2, '0');
    const formattedMinutes = minutes.toString().padStart(2, '0');
    return `${formattedHours}:${formattedMinutes}`;
}


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