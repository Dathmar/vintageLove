function $(x) { return document.getElementById(x)}

const tax_percent_elemt = $('tax_percent')
const tax_amount_elemt = $('tax_amount')
const order_cost_elemt = $('order_cost')
const shipping_amount_elemt = $('shipping_amount')

async function initializeCard(payments) {
    const card = await payments.card();
    await card.attach('#card-container');
    return card;
}

document.addEventListener('DOMContentLoaded', async function () {
    if (!window.Square) {
        throw new Error('Square.js failed to load properly');
    }
    let fetch_response = await fetchSquareAppId();
    const payments = window.Square.payments(fetch_response.square_app_id, fetch_response.square_location_id);
    let card;
    try {
        card = await initializeCard(payments);
    } catch (e) {
        console.error('Initializing Card failed', e);
        return;
    }

    // Checkpoint 2.
    async function handlePaymentMethodSubmission(event, paymentMethod) {
        event.preventDefault();

        try {
            // disable the submit button as we await tokenization and make a
            // payment request.
            cardButton.disabled = true;
            const token = await tokenize(paymentMethod);
            await nce(token);
            document.forms[0].submit();
        } catch (e) {
            cardButton.disabled = false;
            displayPaymentResults('FAILURE');
            console.error(e.message);
        }
    }

    const cardButton = document.getElementById(
        'card-button'
    );
    cardButton.addEventListener('click', async function (event) {
        await handlePaymentMethodSubmission(event, card);
    });
});

async function tokenize(paymentMethod) {
    const tokenResult = await paymentMethod.tokenize();
    if (tokenResult.status === 'OK') {
        return tokenResult.token;
    } else {
        let errorMessage = `Tokenization failed-status: ${tokenResult.status}`;
        if (tokenResult.errors) {
            errorMessage += ` and errors: ${JSON.stringify(
                tokenResult.errors
            )}`;
        }
        throw new Error(errorMessage);
    }
}

function fetchSquareAppId() {
    let sq_id = fetch('/orders/square-app-id/').then(
        response => {
            return response.json()
        })
    return sq_id;
};

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
