$('#list-tab a').on('click', function(e) {
    e.preventDefault();
    $(this).tab('show');
})

let ship_sizes;
let ship_location;
let to_door;
let to_address;
let from_address;
let ship_error;
let ship_small;
let ship_medium;
let ship_large;
let ship_set;
let insurance;

const shipping_timeline_elem = $('#shipping-timeline')
const loading_elem = $('#load')
const cost_elem = $('#cost')

function showTab(tabID){
    let triggerEl = $(tabID);
    bootstrap.Tab.getOrCreateInstance(triggerEl).show();
}

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
    let ship_text;
    ship_small = $('#id_size_small')
    ship_medium = $('#id_size_medium')
    ship_large = $('#id_size_large')
    ship_set = $('#id_size_set')

    if (ship_small.val() === null || ship_small.val() === '' || ship_small.val() === 0) {
        ship_small.val(0)
    } else {
        ship_text = ship_small.val() + ' small items '
    }
    if (ship_medium.val() === null || ship_medium.val() === '' || ship_medium.val() === 0) {
        ship_medium.val(0)
    } else {
        ship_text = ship_text + ship_medium.val() + ' medium items '
    }
    if (ship_large.val() === null || ship_large.val() === '' || ship_large.val() === 0) {
        ship_large.val(0)
    } else {
        ship_text = ship_text + ship_large.val() + ' large items '
    }
    if (ship_set.val() === null || ship_set.val() === '' || ship_set.val() === 0) {
        ship_set.val(0)
    } else {
        ship_text = ship_text + ship_set.val() + ' sets'
    }

    ship_size = ship_text.trim().replace("  ", " ")

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
    let insurance_elem = $('#insurance')
    if($('#id_insure_level_0').is(':checked')) {
        insurance = false;
        insurance_elem.text("Your shipping is insured up to the value of the service.")
    } else if($('#id_insure_level_1').is(':checked')) {
        insurance = true;
        insurance_elem.text("Your shipping fully insured!")
    }

    if(ship_small === 0 && ship_medium === 0 && ship_large === 0 && ship_set === 0 && ship_location === null) {
        ship_error = 'Please select a size and location';
    } else if (ship_small === 0 && ship_medium === 0 && ship_large === 0 && ship_set === 0) {
        ship_error = 'Please input an item to ship';
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

function delay(time) {
  return new Promise(resolve => setTimeout(resolve, time));
}

async function calculate_cost() {

    from_address = get_from_address();

    if(ship_error === null && to_address.length > 0 && from_address.length > 0) {
        shipping_timeline_elem.hide();
        cost_elem.hide();
        loading_elem.show()

        await delay(3000);

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
        loading_elem.hide()
        shipping_timeline_elem.show();
        cost_elem.show();
    } else {
        $('#cost').text('Cannot Calculate Shipping Costs');
        $('#form-submit').prop('disabled', true);
        loading_elem.hide()
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
