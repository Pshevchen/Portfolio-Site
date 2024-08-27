$(document).ready(function() {
    socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');

    socket.on('connect', function() {
        socket.emit('joined', {});
    });
    
    socket.on('status', function(data) {     
        let tag  = document.createElement("p");
        let text = document.createTextNode(data.msg);
        let element = document.getElementById("chat");
        tag.appendChild(text);
        tag.style.cssText = data.style;
        element.appendChild(tag);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);

    });      
    // Listen for 'new_message' event from the server
    socket.on('new_message', function(data) {
        let element = document.createElement("div");
        element.style.cssText = data.style;
        element.textContent = data.msg;
        document.getElementById("chat").appendChild(element);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    // Event listener for input field to detect the Enter key
    $('#message_input').keypress(function(e) {
        if(e.which == 13) { // Enter key is pressed
            e.preventDefault(); // Prevent the default action of the enter key
            var message = $(this).val(); // Get the message from the input
            if(message.trim().length > 0) { // Don't send an empty message  
                socket.emit('new_message', {message: message}); // Emit the correct event
                $(this).val(''); // Clear the input field
            }
        }
    });

    // Leave the chat when the "Leave Chat" button is clicked
    $('#leave').click(function() {
        document.getElementById('chat-container').style.display = 'none';
    });


    
});

// JavaScript to toggle the feedback form
document.getElementById('chat-button').onclick = function() {
    var chatButton = document.getElementById('chat-button');
    var chatForm = document.getElementById('chat-container');
    // Tracks the visibility state of the form
    var visible = false; 

    // Toggle the visibility state  
    chatButton.onclick = function() {
        visible = !visible;
        chatForm.style.display = visible ? 'block' : 'none';
    };
};