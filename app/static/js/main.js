// Main JavaScript for Flask Betting App

document.addEventListener('DOMContentLoaded', function () {
    // Flash message auto-hide
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function (message) {
        setTimeout(function () {
            message.style.opacity = '0';
            setTimeout(function () {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Form validation helpers
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const requiredFields = form.querySelectorAll('[required]');
            let hasErrors = false;

            requiredFields.forEach(function (field) {
                if (!field.value.trim()) {
                    field.classList.add('error');
                    hasErrors = true;
                } else {
                    field.classList.remove('error');
                }
            });

            if (hasErrors) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
});

// Utility functions
function showLoading(button) {
    button.disabled = true;
    button.textContent = 'Loading...';
}

function hideLoading(button, originalText) {
    button.disabled = false;
    button.textContent = originalText;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message flash-${type}`;
    notification.textContent = message;

    const container = document.querySelector('.flash-messages') ||
        document.querySelector('main .container');

    if (container) {
        container.insertBefore(notification, container.firstChild);

        setTimeout(function () {
            notification.style.opacity = '0';
            setTimeout(function () {
                notification.remove();
            }, 300);
        }, 5000);
    }
}
