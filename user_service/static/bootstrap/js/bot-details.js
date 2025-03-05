document.getElementById('showTokenBtn').addEventListener('click', function() {
    var tokenElement = document.getElementById('tokenInput'); // исправленное имя идентификатора
    var button = this;

    if (tokenElement.style.display === 'none') {
        tokenElement.style.display = 'inline'; // показываем поле
        button.textContent = 'Скрыть';
    } else {
        tokenElement.style.display = 'none'; // скрываем поле
        button.textContent = 'Показать';
    }
});