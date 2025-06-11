// get elements
const hero = document.getElementById('hero-image');
const get_started = document.getElementById('get-started');

document.addEventListener('scroll', function () {
    let scroll_top = window.scrollY;
    hero_scroll(scroll_top);
    get_started_scroll(scroll_top);
})

//h3_animation();


function hero_scroll(scroll_top) {
    let speed = hero.dataset.speed || 0.5;
    hero.style.backgroundPositionY = -(scroll_top * speed) + "px";
}

function get_started_scroll(scroll_top) {
    const scroll_get_started = window.innerHeight + (window.innerHeight * 0.8); // hero height + section height
    let speed = get_started.dataset.speed || 0.25;
    get_started.style.backgroundPositionX = ((scroll_top - scroll_get_started) * speed) + "px";
}

/*
function h3_animation() {
    window.scrollX = 0;
    const title = document.querySelector('h1');
    const subtitle = document.querySelector('h3');
    const button = document.getElementById('start-button');
    let id = null;
    let pos = 10;
    id = setInterval(frame, 5);
    function frame() {
        if (pos <= 0) {
            clearInterval(id);
        } else {
            pos -= 0.1;
            title.style.marginLeft = pos + 'vh';
            subtitle.style.marginRight = pos + 'vh';
            //button.style.marginTop = pos + 'vh';
        }
    }
    window.scrollX = -100;
}
*/