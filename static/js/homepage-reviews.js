        // reviews script

        let reviews = [];
        let currentReviewIndex = 0;

        function showReview(index) {
        const review = reviews[index];
        document.getElementById("clientName").innerText = review.client_name;

        // Add double quotes around the review text and make it italic
        const formattedReviewText = `"${review.text}"`;
        document.getElementById("reviewText").innerHTML = `<em>${formattedReviewText}</em>`;

        // Add Font Awesome stars
        const stars = '<i class="fas fa-star"></i>'.repeat(5);
        document.getElementById("reviewStars").innerHTML = stars;
    }



        function cycleReviews() {
            currentReviewIndex = (currentReviewIndex + 1) % reviews.length;
            showReview(currentReviewIndex);
        }

        function onPrevClick() {
            currentReviewIndex = (currentReviewIndex - 1 + reviews.length) % reviews.length;
            showReview(currentReviewIndex);
        }

        function onNextClick() {
            cycleReviews();
        }

        // Fetch reviews from JSON file
        fetch('static/json/reviews.json')
            .then(response => response.json())
            .then(data => {
                reviews = data;
                // Initial display
                showReview(currentReviewIndex);
                // Start cycling reviews
                setInterval(cycleReviews, 10000); // 10 seconds interval
            })
            .catch(error => console.error('Error fetching reviews:', error));

        // Attach event listeners to buttons
        document.getElementById("prevBtn").addEventListener("click", onPrevClick);
        document.getElementById("nextBtn").addEventListener("click", onNextClick);
