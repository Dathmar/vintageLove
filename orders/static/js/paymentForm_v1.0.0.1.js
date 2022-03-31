function $(x) { return document.getElementById(x)}

let paymentForm_v1001;
const tax_percent_elemt = $('tax_percent')
const tax_amount_elemt = $('tax_amount')
const order_cost_elemt = $('order_cost')
const shipping_amount_elemt = $('shipping_amount')

function fetchSquareAppId() {
    let sq_id = fetch('/orders/square-app-id/').then(
        response => {
            return response.json()
        })
    return sq_id;
};

async function setSquareAppID() {
    let app_id = await fetchSquareAppId();
    paymentForm_v1001 = new SqPaymentForm(
        {
            // Initialize the payment form elements
            applicationId: app_id.square_app_id,
            autoBuild: false,
            // Initialize the credit card placeholders
            card: {
                elementId: 'sq-card',
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

                    await nce(nonce);
                    document.forms[0].submit();
                    return;
                }
            }
        });
    paymentForm_v1001.build();
}

setSquareAppID();

 // onGetCardNonce is triggered when the "Pay $1.00" button is clicked
async function onGetCardNonce(event) {
    // Don't submit the form until SqPaymentForm returns with a nonce
    event.preventDefault();

    // Request a nonce from the SqPaymentForm object
    await paymentForm_v1001.requestCardNonce();
}


function fetchCost() {
    let state = $('id_state').value
    let cst = fetch('/orders/order-cost/', {
        method: 'POST',
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({'product_id': product_id, 'state': state })
    }).then(response => {
        return response.json()
    })
    return cst
}

async function getCost() {
    let cost_info = await fetchCost()

    tax_percent_elemt.innerText = "Tax @ " + cost_info.tax_percent + "%"
    shipping_amount_elemt.innerText = "$" + cost_info.shipping_amount
    tax_amount_elemt.innerText = "$" + cost_info.tax_amount
    order_cost_elemt.innerText = "$" + cost_info.order_cost
}

async function nce(nonce) {
    await fetch('/orders/order-nonce/', {
        method: 'POST',
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({'nonce': nonce})
    }).catch(err => console.log(err))
}