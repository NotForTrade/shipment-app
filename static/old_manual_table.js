$(document).ready(function () {

    // Function to build the table
    function buildTable(data) {
        var table = $('<table/>').addClass('my-table');
        var thead = $('<thead/>');
        var tbody = $('<tbody/>');

        // Assuming all objects have the same keys, so use the first one to create headers
        var headers = Object.keys(data[0]);
        var headerRow = $('<tr/>');
        headers.forEach(function (header) {
            headerRow.append($('<th/>').text(header));
        });
        thead.append(headerRow);

        // Create table rows
        data.forEach(function (rowData) {
            var row = $('<tr/>');
            headers.forEach(function (header) {
                row.append($('<td/>').text(rowData[header]));
            });
            tbody.append(row);
        });

        table.append(thead).append(tbody);
        $('#table').append(table);
    }

    // Build the table with the data
    buildTable(data);
    setInterval(buildTable, 1000);

    /*
    function updateTable() {
            $.get("http://127.0.0.1:5000/api", function (data, status) {
                $("#my_value").text(data);
            });
    }
        updateTable()
        setInterval(updateValue, 1000);
        */

});