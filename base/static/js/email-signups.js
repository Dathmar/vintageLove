
let email = document.getElementById("email-marketing-signup")
email.addEventListener("keydown", function (e) {
    if (e.code === "Enter") {  //checks whether the pressed key is "Enter"
        marketingSignupAsync();
    }
});

function marketingSignup() {
    let email_value = email.value
    let promise = fetch('/marketing-signup/', {
        method: 'POST',
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({'email': email_value })
    }).then(response => {
        return response.json()
    })
    return promise
}

async function marketingSignupAsync() {
    let marketing_response = await marketingSignup()
    let result_span = document.getElementById("result")
    if(marketing_response.status == "success"){
        result_span.innerHTML = "Success"
        result_span.classList.remove('d-none')
    } else {
        if(marketing_response.response.title == "Member Exists") {
            result_span.innerHTML = "You are already Subscribed!"
        } else {
            result_span.innerHTML = "Error, try again later."
        }

        result_span.classList.remove('d-none')
    }

}