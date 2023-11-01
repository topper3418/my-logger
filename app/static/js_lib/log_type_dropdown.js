function getLogTypeDropdown() {
    return document.getElementById('log-type-dropdown');
}


async function populateLogTypeDropdown() {
    dropdown = getLogTypeDropdown();
    dropdown.innerHTML = '';
    const types = await getLogTypes();
    dropdown.dataset.log_types = JSON.stringify(types);
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type.log_type;
        option.innerHTML = type.log_type;
        dropdown.appendChild(option);
    });
}


function getColor(log) {
    const dropdown = getLogTypeDropdown();
    storedTypes = JSON.parse(dropdown.dataset.log_types);
    const logType = log.log_type;
    const typeColor = storedTypes.find(item => item.log_type === logType).color;
    return typeColor;
}