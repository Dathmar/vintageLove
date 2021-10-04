let myCarousels = document.getElementsByClassName('lazy');
let aCarousels = Array.from(myCarousels);

aCarousels.forEach((carousel) => {
    carousel.addEventListener("slide.bs.carousel", function (e) {
        let lazy = (e.relatedTarget).querySelector('img[data-src]');

        if (lazy !== null) {
            lazy.setAttribute('src', lazy.getAttribute('data-src'))
            lazy.removeAttribute('data-src')
        }
    })
})
