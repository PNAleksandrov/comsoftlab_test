$(document).ready(function() {
    const socket = new WebSocket('ws://' + window.location.host + '/ws/email/' + account_id + '/');

    socket.onopen = function(e) {
        console.log("WebSocket connection established");
        startFetch();
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        switch(data.status) {
            case 'fetching':
                $('#status').text('Fetching emails...');
                $('#progress-bar').show();
                break;
            case 'processing':
                renderMessage(data.message);
                updateProgress(data.progress, data.total);
                break;
            case 'stopping':
                $('#status').text('Stopping...');
                break;
            case 'completed':
                $('#status').text('Completed!');
                break;
            case 'error':
                $('#status').text('Error: ' + data.message);
                break;
        }
    };

    function renderMessage(message) {
        $('#email-body').append(`
            <tr>
                <td>${message.id}</td>
                <td>${message.subject}</td>
                <td>${new Date(message.sent_date)}</td>
                <td>${new Date(message.received_date)}</td>
                <td>${message.content}</td>
                <td>${JSON.stringify(message.attachments)}</td>
            </tr>
        `);
    }

    function updateProgress(current, total) {
        const percent = Math.floor((current / total) * 100);
        $('#progress').css('width', `${percent}%`);
        $('#progress').text(`${percent}%`);
    }

    function startFetch() {
        socket.send(JSON.stringify({command: 'start'}));
    }

    function stopFetch() {
        socket.send(JSON.stringify({command: 'stop'}));
    }

    $('body').append(`
        <button onclick="startFetch()">Start Fetching</button>
        <button onclick="stopFetch()">Stop Fetching</button>
    `);
});