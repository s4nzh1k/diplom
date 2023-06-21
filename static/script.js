// JavaScript для открытия и закрытия модального окна
function openModal(modalId) {
    document.getElementById(modalId).style.display = "block";
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}

// Показать форму входа
function showLoginForm() {
    document.getElementById("loginModal").style.display = "block";
}

// Показать форму регистрации
function showRegisterForm() {
    document.getElementById("registerModal").style.display = "block";
}