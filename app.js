$(document).ready(function() {

    let table_data = []

    let my_table

    function createOrupdateTable(data){
        if (my_table == null) {
            my_table = $('#my_table').DataTable(
                {
                columns: [
                    { title: 'Shipment_id' },
                    { title: 'Weight' },
                    { title: 'Volume' },
                    { title: 'Emitter' },
                    { title: 'Recipient' },
                    { title: 'Emitter_Address' },
                    { title: 'Recipient_Address' },
                    { title: 'Expedition_Date' },
                    { title: 'Estimated_Arrival_Date' },
                    { title: 'Shipment_distance' },
                    { title: 'Perishable' },
                    { title: 'High_Value' },
                    { title: 'Fragile' },          
                    { title: 'Includes_Air_Transportation' },
                    { title: 'Includes_Water_Transportation' },
                    { title: 'Includes_Ground_Transportation' },
                    { title: 'Shipment_Status' }
                    
                
                ],
                data: data
            });
        }
        else{
            my_table.clear()
            my_table.rows.add(data)
            my_table.draw()
        }
    }

    function fetchDataAndUpdateTable() {
        $.get("/api/shipments", function (data, status) {
            //step 1 -> save the retrieved data
            table_data = data
            
            // step 2 -> create/update html table
            createOrupdateTable(table_data)

        });

    }
    fetchDataAndUpdateTable()
    setInterval(fetchDataAndUpdateTable, 1000);


});