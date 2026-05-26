// ---------------- DATA TABLES START ----------------------
tbls = new DataTable('table.display');

tbls.on('click', 'tbody tr', (e) => {
    let classList = e.currentTarget.classList;

    if (classList.contains('selected')) {
        classList.remove('selected');
    }
    else {
        tbls.rows('.selected').nodes().each((row) => row.classList.remove('selected'));
        classList.add('selected');
    }
});
// ---------------- DATA TABLES END ----------------------