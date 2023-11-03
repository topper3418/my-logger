
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
    const logTypeData = await getLogTypes();
    populateLogTypeDropdown(logTypeData, dropdown_id='log-type-dropdown');
    const todayData = await getTodayData();
    populateTree(todayData);
    populateTable(todayData);
}
