function getTableBody() {
    return document.querySelector('#log-table tbody');
}


function populateTable(todayData) {
    const tableBody = getTableBody();
    tableBody.innerHTML = '';
    // reverse the order of logs
    todayData.reverse();
    todayData.forEach(log => {
        const row = document.createElement('tr');

        row.dataset.id = log.id;

        // on double cliek, open the edit popup
        row.addEventListener('dblclick', () => {
            populateOverlayData(data=log);
            showOverlay();
        });

        timestamp_cell = document.createElement('td');
        timestamp_cell.innerHTML = log.timestamp;
        timestamp_cell.style.textAlign = 'right';
        row.appendChild(timestamp_cell);

        parent_cell = document.createElement('td');

        comment_cell = document.createElement('td');
        comment_cell.innerHTML = log.comment;
        comment_cell.style.color = getColor(log);
        row.appendChild(comment_cell);

        // add event listener to the 

        tableBody.appendChild(row);
    });
}