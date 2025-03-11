function updateCharCount(textarea) {
    const maxLength = 3000; // Maximum number of characters allowed
    const remainingCharsElement = document.getElementById('remainingChars');
    const currentLength = textarea.value.length;

    // Update the character count display
    remainingCharsElement.textContent = maxLength - currentLength;

    // Change text color if few characters are remaining
    if (currentLength >= maxLength) {
        remainingCharsElement.style.color = 'red'; // Set color to red when max length is reached
    } else {
        remainingCharsElement.style.color = ''; // Reset color to default
    }
}

// Initialize character counter on page load
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.querySelector('textarea[name="welcome_message"]');
    updateCharCount(textarea); // Update counter for the current value
});