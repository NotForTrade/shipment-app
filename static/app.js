$(document).ready(function() {

    let table_data = []
    let my_table

    const fields = [
        'shipment_status', 'weight', 'volume', 'sender_name', 'sender_address',
        'recipient_name', 'recipient_address', 'expedition_date', 
        'desired_delivery_date', 'perishable', 
        'high_value', 'fragile', 'shipment_id'
    ];

    function createOrupdateTable(data){

        //const rows = data.map(shipment => fields.map(key => shipment[key]));

        let rows = Object.keys(data).map(key => 
            fields.map(field => data[key][field] || "")
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
                            case "ACKNOWLEDGED":
                                $(td).css('background-color', "lightYellow").css('color', "Black")
                                break;
                            case "AT LOCAL PARCEL":
                                $(td).css('background-color', "lightGreen").css('color', "Black")
                                break;
                            case "IN TRANSIT":
                                $(td).css('background-color', "lightGreen").css('color', "Black")
                                break;
                            case "AT PARCEL CENTER":
                                $(td).css('background-color', "lightBlue").css('color', "Black")
                                break;
                            case "UNDERGOING INSPECTION":
                                $(td).css('background-color', "lightBlue").css('color', "Black")
                                break;
                            case "CLEARED BY CUSTOMS":
                                $(td).css('background-color', "lightBlue").css('color', "Black")
                                break;
                            case "APPROACHING DESTINATION":
                                $(td).css('background-color', "lightGreen").css('color', "Black")
                                break;
                            case "COMPLETED":
                                $(td).css('background-color', "darkGreen").css('color', "White")
                                break;
                            case "FAILED - DAMAGED":
                                $(td).css('background-color', "darkRed").css('color', "White")
                                break;
                            case "FAILED - LOST":
                                $(td).css('background-color', "darkRed").css('color', "White")
                                break;
                            default:
                                $(td).css('background-color', "lightYellow")

                        }
                    }
                }
                ]
            });

        }
        else{
            my_table.clear()
            my_table.rows.add(rows)
            my_table.draw(false)
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