
function makeLogTreeElement(log) {
    // create the wrapper that it will all go in
    const logWrapper = document.createElement('div');
    logWrapper.classList.add('column-container');
    // create the element that will hold the log
    const logElement = document.createElement('div');
    logElement.classList.add('row-cluster');
    logElement.classList.add('log-element');
    logElement.dataset.log_id = log.id;
    logElement.style.color = getColor(log);
    logWrapper.appendChild(logElement);
    // get the collapsed ids
    const treeDiv = document.getElementById('log-tree');
    if (!treeDiv.dataset.collapsed) {
        treeDiv.dataset.collapsed = '';
    }
    const collapsedIds = treeDiv.dataset.collapsed.split(',');
    // create the elements that will go in the log element
    // id element
    const logIdElement = document.createElement('p');
    logIdElement.innerHTML = `<b>${log.id}</b>: `;
    logIdElement.style.cursor = 'pointer';
    if (log.complete) {
        logIdElement.style.color = 'green';
    }
    logIdElement.addEventListener('click', collapseChildren);
    // duration element
    const logDurationElement = document.createElement('p');
    logDurationElement.classList.add('duration');
    logDurationElement.innerHTML = formatSeconds(log.time_spent);
    logDurationElement.dataset.time_spent = log.time_spent;
    logDurationElement.dataset.total_time_spent = log.total_time_spent;
    // comment element
    const logCommentElement = document.createElement('p');
    logCommentElement.innerHTML = log.comment;
    logCommentElement.style.flexGrow = 1;
    // remove margins and padding
    logIdElement.style.margin = '0';
    logIdElement.style.padding = '0';
    logIdElement.style.marginRight = '15px';
    logDurationElement.style.margin = '0';
    logDurationElement.style.padding = '0';
    logDurationElement.style.marginLeft = '15px';
    logCommentElement.style.margin = '0';
    logCommentElement.style.padding = '0';
    // append the elements to the log element
    logElement.appendChild(logIdElement);
    logElement.appendChild(logCommentElement);
    logElement.appendChild(logDurationElement);
    
    // determine if it has children, add them recursively
    if (log.children) {
        // if it has children, make a div for them and populate it
        const childrenDiv = document.createElement('div');
        childrenDiv.classList.add('children');
        log.children.forEach(child => {
            childrenDiv.appendChild(makeLogTreeElement(child));
        });
        logWrapper.appendChild(childrenDiv);
    }

    if (collapsedIds.includes(log.id.toString())) {
        collapseChildrenHelper(logWrapper);
    }
    return logWrapper;
}


function get_children(log, todayData) {
    const children = todayData.filter(item => item.parent_id === log.id);
    children.forEach(child => {
        child.children = get_children(child, todayData);
    });
    return children;
}


function sum_time(tree_log) {
    let time = tree_log.time_spent;
    if (tree_log.children) {
        tree_log.children.forEach(child => {
            sum_time(child);
            time += child.total_time_spent;
        });
    }
    tree_log.total_time_spent = time;
}


function get_orphans(todayData) {
    const orphans = [];
    todayData.forEach(log => {
        // if no parent id, or parent id not in data
        if (!log.parent_id || !todayData.find(item => item.id === log.parent_id)) {
            orphans.push(log);
        }
    }
    );
    return orphans;
}


function make_into_tree(todayData) {
    const tree = get_orphans(todayData);
    tree.forEach(log => {
        log.children = get_children(log, todayData);
    });
    // loop through again, getting cumulative time
    tree.forEach(log => {
        sum_time(log);
    });
    return tree;
}


function populateTree(todayData) {
    const treeDiv = document.getElementById('log-tree');
    const collapsed = document.querySelectorAll('.children.hidden');
    const collapsedIds = [];
    collapsed.forEach(element => {
        collapsedIds.push(element.parentElement.querySelector('.log-element').dataset.log_id);
    });
    treeDiv.innerHTML = '';
    treeDiv.dataset.collapsed = collapsedIds;
    console.log(collapsedIds)
    treeData = make_into_tree(todayData);
    treeData.forEach(log => {
        treeDiv.appendChild(makeLogTreeElement(log));
    });
}


function collapseChildrenHelper(element) {
    children = element.querySelector('.children');
    // if its hidden, show it and set the time to be the non-cumulative time
    logDurationElement = element.querySelector('.duration');
    if (children.classList.contains('hidden')) {
        logDurationElement.innerHTML = formatSeconds(logDurationElement.dataset.time_spent);
    } else {
        logDurationElement.innerHTML = formatSeconds(logDurationElement.dataset.total_time_spent);
    }
    children.classList.toggle('hidden');
    element.classList.toggle('bordered');
}


function collapseChildren(event) {
    // get the parent element
    const parent = event.target.parentElement.parentElement.parentElement;
    collapseChildrenHelper(parent);
}