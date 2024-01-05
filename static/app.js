$(document).ready(function() {

    let table_data = []
    let my_table

    const fields = [
        'shipment_status', 'weight', 'volume', 'sender_name', 'sender_address',
        'recipient_name', 'recipient_address', 'expedition_date', 
        'desired_delivery_date', 'perishable', 
        'high_value', 'fragile'
    ];

    function createOrupdateTable(data){

        //const rows = data.map(shipment => fields.map(key => shipment[key]));

        let rows = Object.keys(data).map(key => 
            fields.map(field => JSON.parse(data[key])[field] || "")
        );



        const header = fields.map(function(key) {
            return { title: key }
        })


        if (my_table == null) {
            my_table = $('#my_table').DataTable(
                {
                columns: header,
                data: rows,
                columnDefs: [{
                    targets: fields.indexOf("shipment_status"),
                    createdCell: function(td, cellData, rowData, row, col) {
                        switch (cellData) {
                            case "Completed":
                                $(td).css('background-color', "green").css('color', "White")
                                break;
                            default:
                                $(td).css('background-color', "LightYellow")

                        }
                    }
                }
                ]
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