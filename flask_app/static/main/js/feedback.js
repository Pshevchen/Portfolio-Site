// JavaScript to toggle the feedback form
document.getElementById('feedback-button').onclick = function() {
    var feedbackButton = document.getElementById('feedback-button');
    var feedbackForm = document.getElementById('feedback-form');
    // Tracks the visibility state of the form
    var visible = false; 

    // Toggle the visibility state  
    feedbackButton.onclick = function() {
        visible = !visible;
        feedbackForm.style.display = visible ? 'block' : 'none';
    };
};