let ship_sizes;
let to_door;
let to_address;
let from_address;
let ship_small;
let ship_medium;
let ship_large;
let ship_set;
let insurance;

const shipping_timeline_elem = $('#shipping-timeline')
const cost_elem = $('#cost')

async function shipCost(ship_sizes, from_address, to_address, to_door, insurance) {
    return await fetch('/ship/ship-cost/', {
        method: 'POST',
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({'ship_sizes': ship_sizes, 'from_address': from_address, 'to_address': to_address, 'to_door': to_door, insurance: insurance})
    }).then(
        response => {
            return response.json()
    })
}

async function calculate_cost() {
    to_address = get_to_address()
    from_address = get_from_address();

    ship_small = $('#id_size_small')
    ship_medium = $('#id_size_medium')
    ship_large = $('#id_size_large')
    ship_set = $('#id_size_set')

    if (ship_small.val() === null || ship_small.val() === '' || ship_small.val() === 0 || ship_small.val() === '0') {
        ship_small.val(0)
    }
    if (ship_medium.val() === null || ship_medium.val() === '' || ship_medium.val() === 0 || ship_medium.val() === '0') {
        ship_medium.val(0)
    }
    if (ship_large.val() === null || ship_large.val() === '' || ship_large.val() === 0 || ship_large.val() === '0') {
        ship_large.val(0)
    }
    if (ship_set.val() === null || ship_set.val() === '' || ship_set.val() === 0 || ship_set.val() === '0') {
        ship_set.val(0)
    }

    if($('#id_level_0').is(':checked')) {
        to_door = 'door';
    } else if($('#id_level_1').is(':checked')) {
        to_door = 'placement';
    } else {
        to_door = null;
    }

    if($('#id_insure_level_0').is(':checked')) {
        insurance = false;
    } else if($('#id_insure_level_1').is(':checked')) {
        insurance = true;
    }

    if(to_address.length > 0 && from_address.length > 0) {
        ship_sizes = {
            small: ship_small.val(),
            medium: ship_medium.val(),
            large: ship_large.val(),
            set: ship_set.val()
        }

        let ship_cost = await shipCost(ship_sizes, from_address.join(' '), to_address.join(' '), to_door, insurance);
        console.log(ship_cost);
        if(ship_cost.supported_state === false) {
            cost_elem.text('Sorry, we do not ship to your state.');
            $('#form-submit').prop('disabled', true);
        } else {
            cost_elem.text('Your shipping cost is $' + ship_cost.cost);
            $('#form-submit').prop('disabled', false);
        }
        let distance = parseFloat(ship_cost.distance);

        if(distance < 51 && distance >= 0) {
            shipping_timeline_elem.text('You will receive your item within 1 week.');
        } else if (distance > 50 && distance < 151) {
            shipping_timeline_elem.text('You will receive your item within 2 weeks.');
        } else if (distance > 150) {
            shipping_timeline_elem.text('You will receive your item in 2 to 3 weeks.');
        }
    } else {
        $('#cost').text('Cannot Calculate Shipping Costs');
        $('#form-submit').prop('disabled', true);
    }
}

function get_to_address() {
    let address1_val = $('#id_address1').val();
    let address2_val = $('#id_address2').val();
    let city_val = $('#id_city').val();
    let state_val = $('#id_state').val();
    let postal_code_val = $('#id_postal_code').val();
    to_address = [];
    to_address.push(address1_val)

    if(address2_val !== '') {
        to_address.push(address2_val);
    }
    to_address.push(city_val);
    to_address.push(state_val);
    to_address.push(postal_code_val);
    return to_address;
}

function get_from_address(){
    from_address = [];
    if($('#from-form').length) {
        let from_errors = false;
        let from_address1_val = $('#id_store_address_1').val();
        let from_address2_val = $('#id_store_address_2').val();
        let from_city_val = $('#id_store_city').val();
        let from_state_val = $('#id_store_state').val();
        let from_postal_code_val = $('#id_store_postal_code').val();

        if (from_address1_val === '') {
            from_errors = true;
        }
        if (from_city_val === '') {
            from_errors = true;
        }
        if (from_state_val === '') {
            from_errors = true;
        }
        if (from_postal_code_val === '') {
            from_errors = true;
        }

        if(from_errors === false) {
            from_address.push(from_address1_val)
            if(from_address2_val !== '') {
                from_address.push(from_address2_val);
            }
            from_address.push(from_city_val);
            from_address.push(from_state_val);
            from_address.push(from_postal_code_val);
        }
    } else {
        from_address.push($('#seller-street').text());
        from_address.push($('#seller-city').text());
        from_address.push($('#seller-state').text());
        from_address.push($('#seller-postal-code').text());
    }

    return from_address;
}
