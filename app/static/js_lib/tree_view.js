
function collapseChildrenHelper(element) {
    const children = element.querySelector('.children');
    const logElement = element.querySelector('.log-element');
    // if its hidden, show it and set the time to be the non-cumulative time
    logDurationElement = element.querySelector('.duration');
    if (children.classList.contains('hidden')) {
        logDurationElement.innerHTML = formatSeconds(logDurationElement.dataset.time_spent);
    } else {
        logDurationElement.innerHTML = formatSeconds(logDurationElement.dataset.total_time_spent);
    }
    children.classList.toggle('hidden');
    logElement.classList.toggle('bordered');
}


function collapseChildren(event) {
    // get the parent element
    collapseChildrenHelper(event.target.parentElement.parentElement);
}


function get_collapsed_ids() {
    const collapsed = document.querySelectorAll('.children.hidden');
    const collapsedIds = [];
    collapsed.forEach(element => {
        collapsedIds.push(element.parentElement.dataset.log_id);
    });
    console.log(collapsedIds)
    return collapsedIds;
}

function get_expanded_ids() {
    const expanded = document.querySelectorAll('.children:not(.hidden)');
    const expandedIds = [];
    expanded.forEach(element => {
        expandedIds.push(element.parentElement.dataset.log_id);
    });
    return expandedIds;
}


function populateTree(tree_html) {
    // this is where the tree will go
    const treeDiv = document.getElementById('log-tree');
    // non-rendered element to do our work on beforehand
    const tree = document.createElement('div');
    const collapsed_ids = get_collapsed_ids();
    const expanded_ids = get_expanded_ids();
    //treeDiv.innerHTML = tree_html;
    // turn the html string into an element
    tree.innerHTML = tree_html;
    collapsed_ids.forEach(id => {
        const element = tree.querySelector(`.log-element-container[data-log_id="${id}"]`);
        // if the element exists and is not already collapsed, collapse it
        if (element && !element.querySelector('.children').classList.contains('hidden')) {
            collapseChildrenHelper(element);
        }
    });
    expanded_ids.forEach(id => {
        const element = tree.querySelector(`.log-element-container[data-log_id="${id}"]`);
        // if the element exists and is collapsed, expand it. 
        if (element && element.querySelector('.children').classList.contains('hidden')) {
            collapseChildrenHelper(element);
        }
    });

    treeDiv.innerHTML = tree.innerHTML;
}


async function getTreeHtml(target_date) {
    const response = await fetch(`/log_tree?target_date=${target_date}`);
    return await response.text();
}


async function switchFocus(event) {
    const log_id = event.target.parentElement.parentElement.dataset.log_id;

    const response = await fetch(`/submit`, {
        method: 'POST',
        body: JSON.stringify({ 'log-comment': `[${log_id}]`}),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    refreshViews();
}


function centerTable(event) {
    const log_id = event.target.parentElement.parentElement.dataset.log_id;
    const element = getLogTableElement(log_id);
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    element.classList.add('pulse-highlight');
    setTimeout(() => {
        element.classList.remove('pulse-highlight');
    }, 2500);
}