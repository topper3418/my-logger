function isCollapsed(element) {
    return element.querySelector('.children').classList.contains('hidden');
}


function collapseChildren(element) {
    // if its already collapsed, do nothing
    if (isCollapsed(element)) {
        return;
    }
    const logDurationElement = element.querySelector('.duration');
    const children = element.querySelector('.children');
    const logElement = element.querySelector('.log-element');
    logDurationElement.innerHTML = formatSeconds(logDurationElement.dataset.total_time_spent);
    children.classList.add('hidden');
    logElement.classList.add('bordered');
}

function hasChildren(element) {
    const childrenContainer = element.querySelector('.children');
    return childrenContainer.children.length > 0;
}


function expandChildren(element) {
    // if its already expanded, do nothing
    if (!isCollapsed(element)) {
        return;
    }
    const logDurationElement = element.querySelector('.duration');
    const children = element.querySelector('.children');
    const logElement = element.querySelector('.log-element');
    logDurationElement.innerHTML = formatSeconds(logDurationElement.dataset.time_spent);
    children.classList.remove('hidden');
    logElement.classList.remove('bordered');

}


function toggleCollapseHelper(element) {
    if (isCollapsed(element)) {
        expandChildren(element);
    } else {
        collapseChildren(element);
    }
}


function toggleCollapse(event) {
    // get the parent element
    toggleCollapseHelper(event.target.parentElement.parentElement);
}


function get_collapsed_ids(targetDiv) {
    const collapsed = targetDiv.querySelectorAll('.children.hidden');
    const collapsedIds = [];
    collapsed.forEach(element => {
        collapsedIds.push(element.parentElement.dataset.log_id);
    });
    console.log(collapsedIds)
    return collapsedIds;
}

function get_expanded_ids(targetDiv) {
    const expanded = targetDiv.querySelectorAll('.children:not(.hidden)');
    const expandedIds = [];
    expanded.forEach(element => {
        expandedIds.push(element.parentElement.dataset.log_id);
    });
    return expandedIds;
}


function getSiblings(logElement) {
    const parent = logElement.parentElement;
    const siblings = Array.from(parent.children).filter(child => child.classList.contains('log-element-container'));
    // print the sibling id's for debugging
    const siblingIds = [];
    siblings.forEach(sibling => {
        siblingIds.push(sibling.dataset.log_id);
    });
    console.log(siblingIds);
    return siblings;
}


function collapseSiblings(event) {
    const logElement = event.target.parentElement.parentElement;
    const siblings = getSiblings(logElement);
    siblings.forEach(sibling => {
        if (hasChildren(sibling)) {
            collapseChildren(sibling);
        }
    });
}


function populateTree(tree_html, targetDiv) {
    // non-rendered element to do our work on beforehand
    const tree = document.createElement('div');
    const collapsed_ids = get_collapsed_ids(targetDiv);
    const expanded_ids = get_expanded_ids(targetDiv);
    //treeDiv.innerHTML = tree_html;
    // turn the html string into an element
    tree.innerHTML = tree_html;
    collapsed_ids.forEach(id => {
        const element = tree.querySelector(`.log-element-container[data-log_id="${id}"]`);
        // if the element exists and is not already collapsed, collapse it
        if (element && !element.querySelector('.children').classList.contains('hidden')) {
            toggleCollapseHelper(element);
        }
    });
    expanded_ids.forEach(id => {
        const element = tree.querySelector(`.log-element-container[data-log_id="${id}"]`);
        // if the element exists and is collapsed, expand it. 
        if (element && element.querySelector('.children').classList.contains('hidden')) {
            toggleCollapseHelper(element);
        }
    });

    targetDiv.innerHTML = tree.innerHTML;
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


function navDaysAgo(event) {
    const daysAgo = event.target.dataset.days_ago;
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() - daysAgo);
    const dateSelector = document.querySelector('#target-date');
    const year = targetDate.getFullYear();
    const month = (targetDate.getMonth() + 1).toString().padStart(2, '0');
    const day = targetDate.getDate().toString().padStart(2, '0');
    const formattedDate = `${year}-${month}-${day}`;
    dateSelector.value = formattedDate;
    refreshViews();
}