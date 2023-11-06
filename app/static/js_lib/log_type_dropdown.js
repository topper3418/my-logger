function setColor(event) {
    // value change script to set the class to the selected value
    const dropdown = event.target;
    const selected = dropdown.value;
    dropdown.classList = `task-type-${selected}`;
}