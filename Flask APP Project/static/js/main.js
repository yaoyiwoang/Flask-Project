// Simple JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Flask app loaded!');
    
    // Some interactive behavior
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('input[type="submit"]');
            if (submitBtn) {
                submitBtn.value = 'Sending...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // API demo function
    window.loadUsers = function() {
        fetch('/api/users')
            .then(response => response.json())
            .then(data => {
                console.log('Users:', data);
                alert(`Loaded ${data.count} users. Check console for details.`);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading users');
            });
    };
});