// OBSOLETE NO LONGER IN USE

document.addEventListener("DOMContentLoaded", function () {
    const videoList = document.getElementById('videoList');
    const loadedVideoContainer = document.getElementById('loadedVideo');


    // Fetch video data from 'assets/json/videos.json'
    fetch('static/json/videos.json')
        .then(response => response.json())
        .then(data => {
            // Display video thumbnails in the list
            displayVideoGallery(data);

            // Load the first video
            if (data.length > 0) {
                loadVideo(data[0].videoId, data[0].title);
            }
        })
        .catch(error => console.error('Error fetching videos:', error));

    function displayVideoGallery(videos) {
        // Display video thumbnails in the list
        videos.forEach(video => {
            const listItem = document.createElement('li');
            listItem.classList.add('custom-list-item', 'd-flex', 'justify-content-between', 'align-items-center', 'border-bottom');

            const thumbnailContainer = document.createElement('div');
            thumbnailContainer.classList.add('d-flex', 'align-items-center', 'position-relative'); // Added position-relative class

            const thumbnail = document.createElement('img');
            thumbnail.src = video.thumbnail;
            thumbnail.alt = video.title;
            thumbnail.classList.add('img-thumbnail', 'video-thumbnail');

            const playIcon = document.createElement('i');
            playIcon.classList.add('fas', 'fa-play-circle', 'play-icon');

            const contentContainer = document.createElement('div');
            contentContainer.classList.add('d-flex', 'flex-column', 'ms-3', 'flex-grow-1'); // Added Bootstrap classes

            const title = document.createElement('span');
            title.textContent = video.title;
            title.classList.add('text-start'); // Bootstrap class for left alignment

            // Attach click event to load the video
            listItem.addEventListener('click', function () {
                // Remove 'selected-video' class from the previously selected item
                const previouslySelectedItem = videoList.querySelector('.custom-list-item.selected-video');
                if (previouslySelectedItem) {
                    previouslySelectedItem.classList.remove('selected-video');
                }

                // Add 'selected-video' class to the clicked item
                listItem.classList.add('selected-video');

                // Load the video
                loadVideo(video.videoId, video.title);
            });

            thumbnailContainer.appendChild(thumbnail);
            thumbnailContainer.appendChild(playIcon);

            contentContainer.appendChild(title);

            listItem.appendChild(thumbnailContainer);
            listItem.appendChild(contentContainer);

            videoList.appendChild(listItem);
        });
    }

    // Function to load the video
    function loadVideo(videoId, videoTitle) {
        loadedVideoContainer.innerHTML = `
        <div class="container pt-5">
          <div class="video-wrapper embed-responsive embed-responsive-16by9 d-flex justify-content-center align-items-center">
            <iframe class="embed-responsive-item" 
                    src="https://www.youtube.com/embed/${videoId}" 
                    title="YouTube video player" frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture;" 
                    allowfullscreen>
            </iframe>
          </div>
          <div>
            <p class="text-center">Now Playing: ${videoTitle}</p>
          </div>
        </div>`;
    }
});
