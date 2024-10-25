 // removes background of jumbotron when nav menu is opened
 document.addEventListener("DOMContentLoaded", function () {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const jumbotron = document.querySelector('.jumbotron');

    navbarToggler.addEventListener('click', function () {
        console.log('removing background')
        jumbotron.classList.toggle('remove-background');
    });
});