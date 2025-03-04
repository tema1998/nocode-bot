document.getElementById('showTokenBtn').addEventListener('click', function() {
    var tokenElement = document.getElementById('token');
    var button = this;

    if (tokenElement.style.display === 'none') {
        tokenElement.style.display = 'inline';
        button.textContent = 'Скрыть';
    } else {
        tokenElement.style.display = 'none';
        button.textContent = 'Показать';
    }
});