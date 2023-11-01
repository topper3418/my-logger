function getLogTypeList() {
    return document.getElementById('log-types-list');
}


async function populateLogTypeList() {
    list = getLogTypeList();
    list.innerHTML = '';
    const types = await getLogTypes();
    types.forEach(type => {
        const item = document.createElement('li');
        item.innerHTML = type.log_type;
        item.style.color = type.color; // set the color of the list item
        item.addEventListener('click', highlightItem);
        list.appendChild(item);
    });
}


