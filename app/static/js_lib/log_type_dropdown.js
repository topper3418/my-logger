function getLogTypeDropdown(dropdown_id='log-type-dropdown') {
    return document.getElementById(dropdown_id);
}


async function populateLogTypeDropdown(log_type_data, dropdown_id='log-type-dropdown') {
    dropdown = getLogTypeDropdown(dropdown_id);
    dropdown.innerHTML = '';
    dropdown.dataset.log_types = JSON.stringify(log_type_data);
    log_type_data.forEach(type => {
        const option = document.createElement('option');
        option.value = type.log_type;
        option.innerHTML = type.log_type;
        dropdown.appendChild(option);
    });
}


function getColor(log, dropdown_element=getLogTypeDropdown()) {
    storedTypes = JSON.parse(dropdown_element.dataset.log_types);
    const logType = log.log_type;
    const typeColor = storedTypes.find(item => item.log_type === logType).color;
    return typeColor;
}