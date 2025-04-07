function updateCharCount(textarea, element_id, maxLength) {
    const remainingCharsElement = document.getElementById(element_id);
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
    const button_text_area = document.querySelector('textarea[name="button_text"]');
    const reply_text_area = document.querySelector('textarea[name="reply_text"]');
    updateCharCount(button_text_area, 'remainingCharsButtonText', 64);
    updateCharCount(reply_text_area, 'remainingCharsReplyText', 3000);
});