const shadow = document.querySelector('.mouse-shadow');

document.addEventListener('mousemove', (e) => {
    shadow.style.left = `${e.clientX}px`;
    shadow.style.top = `${e.clientY}px`;
});