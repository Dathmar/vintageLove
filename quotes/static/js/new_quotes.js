let to_address = $(`#id_to_address`)[0];
let designer_toggle = $(`#id_allow_designer`)[0];
let designer_name = $(`#id_designer_name`);
let designer_pays = $(`#id_designer_pays`)[0];
let quote_button = $(`#id_generate_quote`)[0];
let whole_form = $(`#id_whole_form`)[0];
let has_quote = false;
let review_quote = $('#id_review_quote')[0];

function initialize_form(form_number) {
    let seller_name = $(`#id_form-${form_number}-from_seller`);
    let custom_from_address = $(`#id_form-${form_number}-custom_from_address`)[0];
    let from_address = $(`#id_form-${form_number}-from_address`)[0];
    let pickup_toggle = $(`#id_form-${form_number}-pickup`)[0];
    let receiving_toggle = $(`#id_form-${form_number}-receiving`)[0];
    let storage_toggle = $(`#id_form-${form_number}-storage`)[0];
    let length = $(`#id_form-${form_number}-length`)[0];
    let width = $(`#id_form-${form_number}-width`)[0];
    let height = $(`#id_form-${form_number}-height`)[0];
    let copy_form = $(`#id_form-${form_number}-copy_form`)[0];

    seller_name.select2({
        disabled: 'true',
    });
    seller_name.val(null).trigger('change');
    copy_form.value = '';
    storage_toggle.addEventListener("change", function () {
        if (storage_toggle.checked) {
            length.disabled = false;
            width.disabled = false;
            height.disabled = false;
        } else {
            length.disabled = true;
            width.disabled = true;
            height.disabled = true;
            length.value = null;
            width.value = null;
            height.value = null;
        }
    });

    custom_from_address.addEventListener("change", function() {
        seller_pickup_toggle();
    });

    pickup_toggle.addEventListener("change", function() {
        if (pickup_toggle.checked) {
            receiving_toggle.checked = false;
        }
        seller_pickup_toggle();
    });

    receiving_toggle.addEventListener("change", function() {
        if (receiving_toggle.checked) {
            pickup_toggle.checked = false;
        }
        seller_pickup_toggle();
    });

    copy_form.addEventListener("change", function () {
        let from_val = parseInt(copy_form.value) - 1;
        if (from_val != '' && form_number != from_val) {
            copy_form_content(from_val, form_number)
            copy_form.value = '';
        }
    })

    function seller_pickup_toggle() {
        if (custom_from_address.checked && pickup_toggle.checked) {
            seller_name.prop("disabled", true);
            seller_name.val(null).trigger('change');
            from_address.disabled = false;
        } else if (custom_from_address.checked && !pickup_toggle.checked) {
            custom_from_address.disabled = true;
            custom_from_address.checked = false;
            seller_name.prop("disabled", true);
            seller_name.val(null).trigger('change');
            from_address.disabled = true;
            from_address.value = null;
        } else if (!custom_from_address.checked && pickup_toggle.checked) {
            custom_from_address.disabled = false;
            seller_name.prop("disabled", false);
            from_address.disabled = true;
            from_address.value = null;
        } else if (!pickup_toggle.checked) {
            custom_from_address.disabled = true;
            seller_name.prop("disabled", true);
            seller_name.val(null).trigger('change');
            from_address.disabled = true;
        }
    }

    custom_from_address.disabled = true;
    length.disabled = true;
    width.disabled = true;
    height.disabled = true;
    from_address.disabled = true;

    let from_address_autocomplete = new google.maps.places.Autocomplete(from_address, {
        componentRestrictions: { country: ["us"], state: ["tx"] },
        fields: ["address_components", "geometry"],
        types: ["address"],
    });

    let forms = $('.quote-item-row');
    let form = $(forms[form_number])
    let inputs = form.find(':input')
    for (let i=0, input_count=inputs.length; i<input_count; i++) {
        inputs[i].addEventListener("change", function() {
            if (has_quote) {
                review_quote.innerHTML = null;
            }
        })
    }
}

$(document).ready( async function() {
    designer_name.select2({
        disabled: true,
    });

    let item_forms = $(".quote-item-row");
    for (let i=0, formCount=item_forms.length; i<formCount-1; i++) {
        initialize_form(i);
    }

    designer_toggle.addEventListener("change", function() {
        if (designer_toggle.checked) {
            designer_name.prop("disabled", false);
            designer_pays.disabled = false;
        } else {
            designer_name.prop("disabled", true);
            designer_pays.disabled = true;
            designer_pays.checked = false;
            designer_name.val(null).trigger('change');
        }
    });

    quote_button.addEventListener("click", async function() {
        console.log('generating quote')
        let form_data = new FormData(whole_form);
        let quote_result = await fetch_quote(form_data);
        console.log(quote_result);
        review_quote.innerHTML = quote_result.html;
        has_quote = true;
    });

    designer_pays.disabled = true;
    designer_name.val(null).trigger('change');
});

/* Google autocomplete */
let to_address_autocomplete = new google.maps.places.Autocomplete(to_address, {
    componentRestrictions: { country: ["us"], state: ["tx"] },
    fields: ["address_components", "geometry"],
    types: ["address"],
});

async function fetch_quote(form_data) {
    let response = await fetch("/quotes/fetch-quote/", {
        method: "POST",
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
        body: form_data,
    }).then(response => response.json()).then(data => {
        console.log(data)
        if (data.success) {
            console.log(data);
            return data;
        } else {
            console.log("fetch error " + data.error);
            return data.error;
        }
    });
    return response;
}

function updateElementIndex(el, prefix, ndx) {
    let id_regex = new RegExp('(' + prefix + '-\\d+)');
    let replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function copy_form_content(from_form_no, to_form_no) {
    let forms = $('.quote-item-row');
    let from_form = $(forms[from_form_no])
    let to_form = $(forms[to_form_no])
    let from_inputs = from_form.find(':input')
    let to_inputs = to_form.find(':input')
    for (let i=0, input_count=from_inputs.length; i<input_count; i++) {
        if (from_inputs[i].type === "checkbox") {
            to_inputs[i].checked = from_inputs[i].checked
        } else {
            to_inputs[i].value = from_inputs[i].value
        }
        to_inputs[i].dispatchEvent(new Event('change'));
    }
}

function deleteForm(prefix, btn) {
    let total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total > 1){
        btn.closest('.quote-item-row').remove();
        let forms = $('.quote-item-row');
        let total_forms = forms.length - 1;
        let copy_form;
        $('#id_' + prefix + '-TOTAL_FORMS').val(total_forms);
        for (let i=0, formCount=total_forms; i<formCount-1; i++) {
            let form = $(forms[i]);
            form.find(':input').each(function() {
                updateElementIndex(this, prefix, i);
            });
            form.find("h4")[0].innerHTML = `Asset ${i+1}`;
            copy_form = form.find(`#id_form-${i}-copy_form`)[0];
            copy_form.options[copy_form.options.length-1] = null;
            copy_form.value = '';
        }

        let last_form = $(forms[total_forms])
        copy_form = last_form.find(`#id_form-__prefix__-copy_form`)[0];
        copy_form.options[copy_form.options.length-1] = null;
    }
    return false;
}

function add_form() {
    let form_idx = parseInt($('#id_form-TOTAL_FORMS').val());
    $('#form-set').append($('#empty-form').html().replace(/__prefix__/g, form_idx));
    $('#id_form-TOTAL_FORMS').val(form_idx + 1);

    let forms = $('.quote-item-row');
    let total_forms = forms.length;
    let copy_form;
    $('#id_' + form_idx + '-TOTAL_FORMS').val(total_forms);
    for (let i = 0, formCount = total_forms; i < formCount - 1; i++) {
        let form = $(forms[i]);
        form.find("h4")[0].innerHTML = `Asset ${i+1}`;

        copy_form = form.find(`#id_form-${i}-copy_form`)[0];
        copy_form.add(new Option(`${copy_form.options.length + 1}`, `${copy_form.options.length + 1}`), undefined);
        copy_form.value = '';
    }
    initialize_form(form_idx);

    let last_form = $(forms[total_forms-1])
    console.log(last_form)
    copy_form = last_form.find(`#id_form-__prefix__-copy_form`)[0];
    copy_form.add(new Option(`${copy_form.options.length + 1}`, `${copy_form.options.length + 1}`), undefined);
    copy_form.value = '';
}

$(document).on('click', '.clone-w', function(){
    add_form();
    let copy_idx = $('#id_form-TOTAL_FORMS').val() - 2;
    copy_form_content(copy_idx, copy_idx + 1);
})

$(document).on('click', '.add-w', function(e){
    add_form();
});

$(document).on('click', '.remove-form-row', function(e){
    deleteForm('form', $(this));
    return false;
});


