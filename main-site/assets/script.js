// --- Feature Flags ---
const featureFlags = {
    showAboutMe: false // Default setting
};

// --- Toggle Logic ---
document.addEventListener('DOMContentLoaded', () => {
    // Check for URL override
    const urlParams = new URLSearchParams(window.location.search);
    const aboutMeOverride = urlParams.get('showAboutMe');

    const aboutMeSection = document.getElementById('about-me-section');

    // Show if the default is true OR if the URL override is 'true'
    if (featureFlags.showAboutMe || aboutMeOverride === 'true') {
        aboutMeSection.classList.remove('hidden');
    }
});
