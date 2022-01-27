async function process_delivery(elem) {
    let val = elem.value;
    let promise = await new Promise(function(resolve, reject) {
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
    });
}