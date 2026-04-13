// LocalMart Main JS
document.addEventListener('DOMContentLoaded', () => {
    console.log('LocalMart UI Initialized');

    // Auto-dismiss flash messages
    const flashMessages = document.querySelector('.flash-messages');
    if (flashMessages) {
        setTimeout(() => {
            flashMessages.style.transition = 'opacity 0.5s ease';
            flashMessages.style.opacity = '0';
            setTimeout(() => {
                flashMessages.remove();
            }, 500);
        }, 3000);
    }

    // Add search interaction
    const searchBtn = document.querySelector('.search-bar button');
    const searchInput = document.querySelector('.search-bar input');
    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', () => {
            if (searchInput.value.trim()) {
                alert(`Searching for: ${searchInput.value}`);
            }
        });
    }
});
