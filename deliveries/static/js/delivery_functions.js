async function process_delivery(elem) {
    let val = elem.value;
    $.ajax({
        url: val,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': getCookie('csrftoken')
        },
        success: function(data) {
            resolve(data);
            let par = elem.closest('td');
            if (data.new_url != null) {
                par.innerHTML = '<p>Non-Complete</p>';
            } else {
                par.innerHTML = '<p>Complete</p>';
            }
        },
        error: function(data) {
            reject(data);
        }
    });
}

function load_deliveries() {
    let start_date = $('#id_start_date').val();
    let end_date = $('#id_end_date').val();
    let url = '/api/v1/get-delivery-table/';

    $.ajax({
        url: url,
        type: 'GET',
        data: {
            'start_date': start_date,
            'end_date': end_date,
            'csrfmiddlewaretoken': getCookie('csrftoken')
        },
        success: function(data) {
            $('#delivery-table').html(data.table_html);
        },
        error: function(data) {
            console.log(data);
        }
    });
}