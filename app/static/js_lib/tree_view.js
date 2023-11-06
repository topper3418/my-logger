
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
    collapseChildrenHelper(event.target.parentElement.parentElement);
}


function get_collapsed_ids() {
    const collapsed = document.querySelectorAll('.children.hidden');
    const collapsedIds = [];
    collapsed.forEach(element => {
        collapsedIds.push(element.parentElement.dataset.log_id);
    });
    return collapsedIds;
}


function populateTree(tree_html) {
    // this is where the tree will go
    const treeDiv = document.getElementById('log-tree');
    // non-rendered element to do our work on beforehand
    const tree = document.createElement('div');
    const collapsed_ids = get_collapsed_ids();
    //treeDiv.innerHTML = tree_html;
    // turn the html string into an element
    tree.innerHTML = tree_html;
    collapsed_ids.forEach(id => {
        const element = tree.querySelector(`.log-element-container[data-log_id="${id}"]`);
        if (element) {
            collapseChildrenHelper(element);
        }
    });

    treeDiv.innerHTML = tree.innerHTML;
}
