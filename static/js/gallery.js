document.addEventListener("DOMContentLoaded", function () {
    const photosContainer = document.getElementById("photos");
  
    // Fetch the gallery.json file
    fetch('assets/json/gallery.json')
      .then(response => response.json())
      .then(images => {
        // Shuffle the array to randomise image order.
        const shuffledImages = images.sort(() => Math.random() - 0.5);
  
        // Append each shuffled image to the container
        shuffledImages.forEach(image => {
          const img = document.createElement('img');
          img.src = image.src;
          img.alt = image.alt || ''; // Use provided alt text or an empty string
          photosContainer.appendChild(img);
        });
      })
      .catch(error => console.error('Error fetching gallery:', error));
  });
  