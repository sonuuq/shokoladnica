const form = document.getElementById('booking-form');
const timeSelect = document.getElementById('time');
const statusMsg = document.getElementById('status');
const selectedTableText = document.getElementById('selected-table');

const tables = [
    { id: 'T1', capacity: 2 },
    { id: 'T2', capacity: 2 },
    { id: 'T3', capacity: 4 },
    { id: 'T4', capacity: 4 },
    { id: 'T5', capacity: 4 },
    { id: 'T6', capacity: 4 },
    { id: 'T7', capacity: 6 },
    { id: 'T8', capacity: 6 },
    { id: 'T9', capacity: 8 },
    { id: 'T10', capacity: 8 }
];

function loadTimeOptions() {
    timeSelect.innerHTML = '';
    for (let hour = 9; hour <= 22; hour++) {
        const timeStr = `${hour.toString().padStart(2, '0')}:00`;
        const opt = document.createElement('option');
        opt.value = timeStr;
        opt.textContent = timeStr;
        timeSelect.appendChild(opt);
    }
}

function loadTables() {
    const guestCount = parseInt(document.getElementById('guests').value) || 1;
    const tableMap = document.getElementById('tables');
    tableMap.innerHTML = '';

    const selectedTableId = form.dataset.selectedTable;
    let selectedTableStillAvailable = false;

    tables.forEach(t => {
        const tableDiv = document.createElement('div');
        tableDiv.classList.add('table', `size-${t.capacity}`);
        tableDiv.dataset.tableId = t.id;
        tableDiv.dataset.capacity = t.capacity;
        tableDiv.innerHTML = `${t.capacity} ${t.capacity <= 2 ? '👤' : '👥'}`;

        if (t.capacity < guestCount) {
            tableDiv.classList.add('disabled');
        } else {
            tableDiv.addEventListener('click', () => {
                selectTable(t.id);
                form.dataset.selectedTable = t.id;
            });

            // Если этот стол выбран и ещё подходит — подсветить
            if (t.id === selectedTableId) {
                selectedTableStillAvailable = true;
                tableDiv.classList.add('selected');
                selectedTableText.textContent = `You selected: ${t.id} (Seats ${t.capacity})`;
            }
        }

        tableMap.appendChild(tableDiv);
    });

    // Если выбранный стол теперь недоступен — сбрасываем выбор
    if (!selectedTableStillAvailable) {
        form.dataset.selectedTable = '';
        selectedTableText.textContent = '';
    }
}



function selectTable(tableId) {
    document.querySelectorAll('.table').forEach(table => {
        table.classList.remove('selected');
    });
    const selectedTable = document.querySelector(`.table[data-table-id='${tableId}']`);
    if (selectedTable) {
        selectedTable.classList.add('selected');
        const capacity = selectedTable.dataset.capacity;
        selectedTableText.textContent = `You selected: ${tableId} (Seats ${capacity})`;
        form.dataset.selectedTable = tableId;  // Добавил сюда
    }
}


document.getElementById('guests').addEventListener('input', loadTables);

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const booking = {
        name: document.getElementById('name').value,
        date: document.getElementById('date').value,
        time: document.getElementById('time').value,
        guests: document.getElementById('guests').value,
        table: form.dataset.selectedTable || ''
    };

    if (!booking.table) {
        statusMsg.textContent = "Please select a table from the map.";
        return;
    }

    const res = await fetch('/book_table', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(booking)
    });

    const result = await res.json();
    if (res.ok) {
        const query = new URLSearchParams(booking).toString();
        window.open(`/confirmation?${query}`, '_blank');
    } else {
        statusMsg.textContent = result.message;
    }
});

loadTimeOptions();
loadTables();




