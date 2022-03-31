function $(x) { return document.getElementById(x)}

let paymentForm;

function fetchSquareAppId() {
    let sq_id = fetch('/orders/square-app-id/').then(
        response => {
            return response.json()
        })
    return sq_id;
};

async function setSquareAppID() {
    let app_id = await fetchSquareAppId();
    paymentForm = new SqPaymentForm(
        {
            // Initialize the payment form elements
            applicationId: app_id.square_app_id,
            autoBuild: false,
            // Initialize the credit card placeholders
            card: {
                elementId: 'sq-card',
                inputStyle: {
                    fontSize: '16px',
                    lineHeight: '24px',
                    padding: '16px',
                    autoFillColor: '#0A486A',
                    color: '#0A486A',
                    placeholderColor: '#0A486A',
                    backgroundColor: '#FFFFFF',
                    cardIconColor: '#A5A5A5',
                },
            },
            // SqPaymentForm callback functions
            callbacks: {
                /*
                * callback function: cardNonceResponseReceived
                * Triggered when: SqPaymentForm completes a card nonce request
                */
                cardNonceResponseReceived: async function (errors, nonce, cardData) {
                    if (errors) {
                        // Log errors from nonce generation to the browser developer console.
                        console.error('Encountered errors:');
                        errors.forEach(function (error) {
                            console.error('  ' + error.message);
                        });
                        alert('Encountered errors, check browser developer console for more details');
                        return;
                    }

                    await putNonce(nonce);
                    document.forms[0].submit();
                    return;
                }
            }
        });
    paymentForm.build();
}


 // onGetCardNonce is triggered when the "Pay $1.00" button is clicked
async function onGetCardNonce(event) {
    // Don't submit the form until SqPaymentForm returns with a nonce
    event.preventDefault();

    // Request a nonce from the SqPaymentForm object
    await paymentForm.requestCardNonce();
}

async function putNonce(nonce) {
    await fetch('/orders/order-nonce/', {
        method: 'POST',
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({'nonce': nonce})
    }).catch(err => console.log(err))
}
