document.addEventListener('DOMContentLoaded', function () {
    // Function to handle menu toggle
    function handleMenuToggle() {
        var navbarHome = document.querySelector('.navbar-home-transparent');
        var navbarToggler = document.querySelector('.navbar-toggler');

        if (navbarToggler.getAttribute('aria-expanded') === 'true') {
            // Mobile menu is open
            navbarHome.classList.add('opaque-background');
        } else {
            // Mobile menu is closed
            navbarHome.classList.remove('opaque-background');
        }
    }

    // Event listener for menu toggle button
    document.querySelector('.navbar-toggler').addEventListener('click', function () {
        handleMenuToggle();
    });

    // Event listener for when the menu is closed outside the toggle button
    var navLinks = document.querySelectorAll('.navbar-nav a');
    navLinks.forEach(function (link) {
        link.addEventListener('click', function () {
            if (document.querySelector('.navbar-toggler').getAttribute('aria-expanded') === 'true') {
                // Mobile menu is open
                handleMenuToggle();
            }
        });
    });
});