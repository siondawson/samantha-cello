document.addEventListener("DOMContentLoaded", function() {
    const galleryImages = document.querySelectorAll('.gallery-img');
    const fullImgBox = document.getElementById("fullImgBox");
    const fullImg = document.getElementById("fullImg");
    
    // Add click event listeners to each gallery image
    galleryImages.forEach(function(img) {
        img.addEventListener('click', function() {
            fullImg.src = img.dataset.fullImg;  // Use data attribute for the full image source
            fullImgBox.style.display = "flex";   // Show the full image box with flex for centering
        });
    });
    
    // Close button functionality
    const closeBtn = document.getElementById("close");
    closeBtn.addEventListener('click', function() {
        fullImgBox.style.display = "none"; // Hide the full image box
    });
});