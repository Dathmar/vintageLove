function approve_quote(quote_id) {
    let promise = fetch(`/api/v1/approve-quote/${quote_id}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": getCookie("csrftoken")
        },
    }).then(response => response.json()).then(data => {
        if (data.quote) {
            let approve_button = document.getElementById('approve-button');
            approve_button.innerHTML = 'Approved';
            approve_button.disabled = true;
        } else {
            alert('Error approving quote');
        }
    });
}