// Main application script for the sycophancy demo
// This file handles client-side interactivity and enhancements

// Smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Log when the app loads
console.log('[v0] Sycophancy Demo app loaded successfully');
