// Get piano object for easy access
const piano = document.querySelector(".piano")
// Get all keys in list
const keys = document.querySelectorAll(".key");

piano.addEventListener("mouseover", displayNotes);
piano.addEventListener("mouseout", hideNotes);


function displayNotes() {
    keys.forEach(key => {
        key.querySelector(".letter").style.display = "block"
    });
}

function hideNotes() {
    keys.forEach(key => {
        key.querySelector(".letter").style.display = "none"
    });
}

// Get all the keys into a map for quick access
const keyMap = {};
document.querySelectorAll(".key").forEach(key => {
    const letter = key.dataset.letter;
    keyMap[letter] = key;
});

// Updated keyDown function to handle lowercase letters
function keyDown(letter) {
    const key = keyMap[letter]; // Convert back to uppercase for keyCode lookup
    if (key) {
        key.classList.add("active");
    }
}

// Function to remove active style
function keyUp(letter) {
    const key = keyMap[letter];
    if (key) {
        key.classList.remove("active");
    }
}

window.addEventListener("keyup", (pressed) => {
    keyUp(pressed.key);
    recordKeyPress(pressed);
});

// The sound object mapping keyCodes to sound URLs
const sound = {65:"http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
    87:"http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
    83:"http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
    69:"http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
    68:"http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
    70:"http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
    84:"http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
    71:"http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
    89:"http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
    72:"http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
    85:"http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
    74:"http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
    75:"http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
    79:"http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
    76:"http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
    80:"http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
    186:"http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav"};


// Function to play the sound associated with the key code
function playSound(keyCode) {
    const soundUrl = sound[keyCode];
    const audio = new Audio(soundUrl);
    audio.play();
}

function handleKeyDown(event) {
    const letter = event.key.toLowerCase(); // Convert to lower case once, for all functions
    keyDown(letter); // Add "active" class
    playSound(event.keyCode); // Play sound
    recordKeyPress(letter); // Record key press
}

function handleKeyUp(event) {
    keyUp(event.key);
}

document.addEventListener('keydown', handleKeyDown);
window.addEventListener('keyup', handleKeyUp);

// This will hold the sequence of pressed keys
let keySequence = [];

// This is the sequence that triggers the awakening
const triggerSequence = ["w", "e", "s", "e", "e", "y", "o", "u"];

// Function to check the sequence and trigger the event
function checkSequence() {
    // Check if the last entered keys match the trigger sequence
    if (keySequence.join("").includes(triggerSequence.join(""))) {

        const creepyAudio = new Audio("https://orangefreesounds.com/wp-content/uploads/2020/09/Creepy-piano-sound-effect.mp3?_=1");
        creepyAudio.play();

        // Fade out the piano image
        piano.style.transition = "opacity 2s";
        piano.style.opacity = 0;

        const title = document.querySelector(".piano-name")
        title.style.transition = "opacity 2s";
        title.style.opacity = 0;

        // Wait for the fade out
        setTimeout(() => {
            // Fade in the new image
            const img = document.querySelector(".piano-image");
            img.style.display = "block";
            img.style.transition = "opacity 5s";
            img.style.opacity = 1;
        }, 2000);

        // Remove event listeners to stop responding to key presses
        // Consolidated event listener for keydown event
        document.removeEventListener('keydown', handleKeyDown);
        window.removeEventListener('keyup', handleKeyUp);
    }
}

// Function to record key presses
function recordKeyPress(event) {
    // Push the pressed key to the sequence array
    const key = event.key.toLowerCase(); // Ensure its case-insensitive
    keySequence.push(key);

    // If the sequence gets too long, remove the first element
    if (keySequence.length > triggerSequence.length) {
        keySequence.shift();
    }

    // Check the sequence
    checkSequence();
}

