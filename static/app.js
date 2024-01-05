$(document).ready(function() {

    let table_data = []

    let my_table

    const fields = [
        'Shipment_id', 'Weight', 'Volume', 'Emitter', 'Recipient', 
        'Emitter_Address', 'Recipient_Address', 'Expedition_Date', 
        'Estimated_Arrival_Date', 'Shipment_distance', 'Perishable', 
        'High_Value', 'Fragile', 'Includes_Air_Transportation', 
        'Includes_Water_Transportation', 'Includes_Ground_Transportation', 
        'Shipment_Status'
    ];



    

    function createOrupdateTable(data){

        const rows = data.map(shipment => fields.map(key => shipment[key]));
        const header = fields.map(function(key) {
            return { title: key }
        })


        if (my_table == null) {
            my_table = $('#my_table').DataTable(
                {
                columns: header,
                data: rows
            });
        }
        else{
            my_table.clear()
            my_table.rows.add(rows)
            my_table.draw()
        }
    }

    function fetchDataAndUpdateTable() {
        $.get("/api", function (data, status) {
            //step 1 -> save the retrieved data
            table_data = data
            
            // step 2 -> create/update html table
            createOrupdateTable(table_data)

        });

    }
    fetchDataAndUpdateTable()
    setInterval(fetchDataAndUpdateTable, 1000);


});