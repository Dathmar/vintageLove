$('#list-tab a').on('click', function(e) {
    e.preventDefault();
    $(this).tab('show');
})

let this_size;
let ship_location;
let to_door;
let to_address;
let from_address;
let ship_error;
let ship_size;

function showTab(tabID){
    let triggerEl = $(tabID);
    bootstrap.Tab.getOrCreateInstance(triggerEl).show();
}

async function shipCost(ship_size, from_address, to_address, to_door) {
    return await fetch('/ship/ship-cost/', {
        method: 'POST',
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({'ship_size': ship_size, 'from_address': from_address, 'to_address': to_address, 'to_door': to_door})
    }).then(
        response => {
            return response.json()
    })
}

let form_container = $('#form-container')
let tabEl = $('#list-submit-list')
tabEl.on('shown.bs.tab', function (event) {
    if ($('#sq-card').length === 0) {
        let card = document.createElement('div')
        card.id = 'sq-card'
        form_container.append(card)
        setSquareAppID();
    }
})

tabEl.on('show.bs.tab', async function (event) {
    let ship_cost;

    if($('#id_size_0').is(':checked')) {
        this_size = 'small'
        ship_size = 'a small item';
    } else if($('#id_size_1').is(':checked')) {
        this_size = 'medium'
        ship_size = 'a medium item';
    } else if($('#id_size_2').is(':checked')) {
        this_size = 'large'
        ship_size = 'a large item';
    } else if($('#id_size_3').is(':checked')) {
        this_size = 'set'
        ship_size = 'a set of items';
    } else {
        this_size = null;
        ship_size = null;
    }

    if($('#id_level_0').is(':checked')) {
        ship_location = 'delivery to your door';
        to_door = true;
    } else if($('#id_level_1').is(':checked')) {
        ship_location = 'in home delivery and setup';
        to_door = false;
    } else {
        ship_location = null;
        to_door = null;
    }

    if(ship_size === null && ship_location === null) {
        ship_error = 'Please select a size and location';
    } else if (ship_size === null) {
        ship_error = 'Please select a size';
    } else if (ship_location === null) {
        ship_error = 'Please select a location';
    } else {
        ship_error = null;
    }


    let ship_error_el = $('#ship-error');
    let ship_text_el = $('#ship-text');
    if(ship_error !== null) {
        ship_error_el.text(ship_error);
        ship_error_el.show();
        ship_text_el.hide();
    } else {
        ship_error_el.hide();
        $('#ship_size').text(ship_size);
        $('#ship_location').text(ship_location);

        ship_text_el.show();
    }

    let to_errors = [];
    let first_name_val = $('#id_first_name').val();
    let last_name_val = $('#id_last_name').val();
    let address1_val = $('#id_address1').val();
    let city_val = $('#id_city').val();
    let state_val = $('#id_state').val();
    let postal_code_val = $('#id_postal_code').val();
    if (first_name_val === '') {
        to_errors.push('Please enter a first name');
    }
    if (last_name_val === '') {
        to_errors.push('Please enter a last name');
    }
    if (address1_val === '') {
        to_errors.push('Please enter an address');
    }
    if (city_val === '') {
        to_errors.push('Please enter a city');
    }
    if (state_val === '') {
        to_errors.push('Please enter a state');
    }
    if (postal_code_val === '') {
        to_errors.push('Please enter a postcode');
    }

    let to_error_el = $('#to-errors');
    let to_text_el = $('#to-text');
    if (to_errors.length > 0) {
        let error_text = "<p>" + to_errors.join("</p><p>") + "</p>";;
        to_error_el.html(error_text);
        to_error_el.show();
        to_text_el.hide();
    } else {
        to_address = get_to_address();
        to_error_el.hide();
        to_text_el.show() ;
    }

    let address2_val = $('#id_address2').val()

    $('#to_first_name').text(first_name_val);
    $('#to_last_name').text(last_name_val);
    $('#to_address_1').text(address1_val);
    $('#to_address_2').text(address2_val);
    $('#to_city').text(city_val);
    $('#to_state').text(state_val);
    $('#to_zip').text(postal_code_val);

    from_address = get_from_address();

    calculate_cost();
})


async function calculate_cost() {
    from_address = get_from_address();

    if(ship_error === null && to_address.length > 0 && from_address.length > 0) {
        let ship_cost = await shipCost(this_size, from_address.join(' '), to_address.join(' '), to_door);
        console.log(ship_cost);
        if(ship_cost.supported_state === false) {
            $('#cost').text('Sorry, we do not ship to your state.');
            $('#form-submit').prop('disabled', true);
        } else {
            $('#cost').text('Your shipping cost is $' + ship_cost.cost);
            $('#form-submit').prop('disabled', false);
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
