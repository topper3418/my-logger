class TableObject {
    constructor(tableContainerId) {
        this.container = document.getElementById(tableContainerId);
        this.data = [];
        this.rowTemplate = null;
        this.fetchRowTemplate();
    }

    async refreshLogData(logIds) {
        try {
            const response = await fetch('/get_logs', {
                method: 'POST',
                body: JSON.stringify(logIds),
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch logs');
            }

            const logs = await response.json();
            this.data = logs; // Assign the log data to the table object's .data attribute
            return logs;
        } catch (error) {
            console.error(error);
        }
    }

    async fetchRowTemplate() {
        try {
            const response = await fetch('/get_row_template');

            if (!response.ok) {
                throw new Error('Failed to fetch row template');
            }

            const template = await response.text();
            this.rowTemplate = template; // Assign the row template to the table object's .rowTemplate attribute
        } catch (error) {
            console.error(error);
            return null;
        }
    }

    redraw() {
        // Redraw the table
        this.container.innerHTML = ''; // Clear the table
        // Iterate over the table data and create new rows
        for (const row of this.data) {
            const rowObject = new RowObject(row);
            this.container.appendChild(rowObject.rowElement);
        }
    }
}

class RowObject {
    constructor(data) {
        this.rowElement = document.createElement('tr');
        this.timeStampElement = document.createElement('td');
        this.messageElement = document.createElement('td');
        this.rowElement.appendChild(this.timeStampElement);
        this.rowElement.appendChild(this.messageElement);
        this.data = data;
        this.populate();
    }
    
    populate() {
        this.timeStampElement.textContent = this.data.timeStamp;
        this.messageElement.textContent = this.data.message;
        this.rowElement.id = `log-table-${this.data.id}`
        this.rowElement.classList.add(`task-type-${this.data.taskType}`);
        this.rowElement.addEventListener('ondblclick', renderOverlay(logId=(this.data.id)));
    }

}

// Usage example
const table = new TableObject();
const logIds = [1, 2, 3];
table.refreshLogs(logIds);

const rowTemplate = await table.fetchRowTemplate();
if (rowTemplate) {
    const row = new RowObject(rowTemplate);
    // Use the row object
}
