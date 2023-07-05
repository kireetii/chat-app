var socketio = io();

const messages = document.getElementById("messages")

const create_msg = (name, msg, time) => {
    const content = `
    <div class="msg-card">
        <span>
            <strong>${name}</strong>: ${msg}
        </span>
        <span class = "muted">
            ${time}
        </span>
    </div>
    `;
    messages.innerHTML += content;
};

socketio.on("message", (data) => {
    create_msg(data.name, data.message, data.time);
});

const send_msg = () => {
    const message = document.getElementById("message");
    if (message.value == "") return;
    socketio.emit("new_message", {data: message.value});
    message.value = "";
};

