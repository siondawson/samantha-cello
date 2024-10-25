document.addEventListener('DOMContentLoaded', () => {
    const faqsContainer = document.getElementById('faqs');

    fetch('assets/json/faq.json')
        .then(response => response.json())
        .then(data => {
            for (const [question, answer] of Object.entries(data)) {
                const faqItem = document.createElement('div');
                faqItem.innerHTML = `
                    <h3>${question}</h3>
                    <hr class="faq-hr">
                    <p>${answer}</p>
                `;
                faqsContainer.appendChild(faqItem);
            }
        })
        .catch(error => console.error('Error fetching data:', error));
});


