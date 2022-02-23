function menu_toggle() {
    let popup_menu = document.getElementById("popup-menu");
    if (popup_menu.classList.contains('d-none') ){
        popup_menu.classList.remove('d-none');
    } else {
        popup_menu.classList.add('d-none');
    }
}