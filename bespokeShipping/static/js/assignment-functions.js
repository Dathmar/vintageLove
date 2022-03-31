let shippingID = $('#shipping_id').attr('value');
let pickup_elem = $('#pickup_id');
let pickup_id = pickup_elem.attr('value');
let delivery_elem = $('#delivery_id');
let delivery_id = delivery_elem.attr('value');

function delivery_change() {
    let driver = $('#id_delivery_driver').val();
    let scheduled_date = $('#id_delivery_date').val();

    post_assignment(delivery_id, driver, scheduled_date, false);
}

function pickup_change() {
    let driver = $('#id_pickup_driver').val();
    let scheduled_date = $('#id_pickup_date').val();

    post_assignment(pickup_id, driver, scheduled_date, true);
}

function post_assignment(id, driver, scheduled_date, pickup) {
    if (new Date(scheduled_date) instanceof Date && !isNaN(new Date(scheduled_date)) && driver != '' && driver!='Driver') {
        let url;
        let body;
        if (id != '') {
            url = `/api/v1/update-assignment/${id}/`;
            body = {
                'id': id,
                'shipping_id': shippingID,
                'driver': driver,
                'scheduled_date': scheduled_date,
                'pickup': pickup
            };
        } else {
            url = '/api/v1/create-assignment/';
            body = {
                'shipping_id': shippingID,
                'driver': driver,
                'scheduled_date': scheduled_date,
                'pickup': pickup
            };
        }
        let promise = fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(body)
        }).then(response => response.json()).then(data => {
            if (data.assignment) {
                if (pickup) {
                    pickup_elem.attr('value', data.assignment);
                    pickup_elem.val(data.assignment);
                    pickup_id = data.assignment;
                } else {
                    delivery_elem.attr('value', data.assignment);
                    delivery_elem.val(data.assignment);
                    delivery_id = data.assignment;
                }

            } else {
                console.log(data.error);
            }
        });
    } else {
        console.log('Date and/or Driver is invalid');
    }

}