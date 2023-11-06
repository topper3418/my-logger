function populateTable(table_html) {
    const tableDiv = document.getElementById('log-table');
    tableDiv.innerHTML = table_html;
}


async function renderOverlay(logId) {
    // get the log data
    const overlay_html = await fetch(`/edit_log/${logId}`).then(response => response.text());
    // set the overlay html
    document.getElementById('overlay').innerHTML = overlay_html;
    // show the overlay
    showOverlay();
}


async function getTableHtml(target_date) {
    const response = await fetch(`/log_table?target_date=${target_date}`);
    return await response.text();
}


function getLogTableElement(logId) {
    return document.querySelector(`tr[data-id="${logId}"]`);
}


