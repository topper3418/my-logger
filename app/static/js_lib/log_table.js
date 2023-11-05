function getTableBody() {
    return document.querySelector('#log-table tbody');
}


function populateTableOld(todayData) {
    const tableBody = getTableBody();
    tableBody.innerHTML = '';
    // reverse the order of logs
    todayData.reverse();
    todayData.forEach(log => {
        const row = document.createElement('tr');

        row.dataset.id = log.id;

        // on double cliek, open the edit popup
        row.addEventListener('dblclick', () => {
            renderOverlay(logId=log.id);
        });

        timestamp_cell = document.createElement('td');
        timestamp_cell.innerHTML = log.timestamp;
        timestamp_cell.style.textAlign = 'right';
        row.appendChild(timestamp_cell);

        parent_cell = document.createElement('td');

        comment_cell = document.createElement('td');
        comment_cell.innerHTML = log.comment;
        comment_cell.classList.add(`task-type-${log.task_type}`);
        row.appendChild(comment_cell);

        // add event listener to the 

        tableBody.appendChild(row);
    });
}


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