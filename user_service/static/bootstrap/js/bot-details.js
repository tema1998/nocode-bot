// Attach an event listener to the button with the ID 'showTokenBtn'
document.getElementById('showTokenBtn').addEventListener('click', function() {
    // Get the input element with the ID 'tokenInput'
    var tokenElement = document.getElementById('tokenInput'); // Corrected identifier name
    // Reference to the button that triggered the event
    var button = this;

    // Check if the token input element is currently hidden
    if (tokenElement.style.display === 'none') {
        tokenElement.style.display = 'inline'; // Show the input field
        button.textContent = 'Скрыть'; // Change button text to 'Hide'
    } else {
        tokenElement.style.display = 'none'; // Hide the input field
        button.textContent = 'Показать'; // Change button text to 'Show'
    }
});