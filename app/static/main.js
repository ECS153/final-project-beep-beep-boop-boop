let socket = io.connect('https://' + document.domain + ':' + location.port);
var username;
var nickname_prev;
var nickname;
var keys;
var server_public_key = null;
var online_users = null;
var current_recipient;
var message_history = {};
var unread = {};


// EXAMPLE USE OF FUNCTIONS
async function testEncryptDecrypt(){
    console.log("Creating keys")
    keys = await createKeys()
    message = "hi bby"
    encoded = await encodeMessage(message)
    encrypted = await encryptData(encoded, keys.publicKey)
    decrypted = await decryptData(encrypted, keys.privateKey)
    decoded = await decodeMessage(decrypted)
    console.log("Printing decrypted message")
    console.log(decoded)
}

function createKeys(){
    return crypto.subtle.generateKey(
        {
            name: "RSA-OAEP",
            modulusLength: 2048, //can be 1024, 2048, or 4096
            publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
            hash: {name: "SHA-256"}, //can be "SHA-1", "SHA-256", "SHA-384", or "SHA-512"
        },
        false, //whether the key is extractable (i.e. can be used in exportKey)
        ["encrypt", "decrypt"] //must be ["encrypt", "decrypt"] or ["wrapKey", "unwrapKey"]
    )
}

function encryptData(data, publicKey){
    return crypto.subtle.encrypt(
        {
            name: "RSA-OAEP",
            //label: Uint8Array([...]) //optional
        },
        publicKey, //from generateKey or importKey above
        data //ArrayBuffer of data you want to encrypt
    )
}

function decryptData(data, privateKey){
    return crypto.subtle.decrypt(
        {
            name: "RSA-OAEP",
            //label: Uint8Array([...]) //optional
        },
        privateKey, //from generateKey or importKey above
        data //ArrayBuffer of the data
    )
}

function encodeMessage(message){
    let encoder = new TextEncoder();
    return encoder.encode(message);
}

function decodeMessage(message){
    let decoder = new TextDecoder();
    return decoder.decode(message)
}




// Event Listeners
document.getElementById("submit").addEventListener("click", handle_login);
document.getElementById("login_view").children[0].children[1].addEventListener("keyup", function(e) {
    if (e.keyCode == 13)
        document.getElementById("login_view").children[0].children[3].focus();
});
document.getElementById("login_view").children[0].children[3].addEventListener("keyup", function(e) {
    if (e.keyCode == 13)
        handle_login();
});
document.getElementById("nickname").addEventListener("keydown", function(e) {
    if (e.keyCode == 13) {
        document.getElementById("nickname").blur();
        e.preventDefault();
        return false;
    }
});
document.getElementById("nickname").addEventListener("paste", function(e) {  // disable pasting to prevent newline
    e.preventDefault();
    return false;
});
document.getElementById("nickname").addEventListener("focus", function(e) {
    nickname_prev = nickname;
});
document.getElementById("nickname").addEventListener("blur", function(e) {
    nickname = document.getElementById("nickname").innerHTML;
    if (nickname != nickname_prev) {
        socket.emit('update', {
            username : username,
            nickname : nickname
        });
    }
});
document.getElementById("chat_input").children[0].addEventListener("keydown", function(e) {
    if (e.keyCode == 13) {
        send_message();
        e.preventDefault();
        return false;
    }
});
document.getElementById("chat_input").children[1].addEventListener("click", send_message);





// Sockets
socket.on('connect', function() {
});

socket.on('disconnect', function(){
    login_view = document.getElementById("login_view");
    login_view.children[0].children[6].innerHTML = '... Session expired (new login detected) ...';
    login_view.children[0].children[6].classList.remove("invisible");
    login_view.classList.remove("hidden")
    color_strip = document.getElementsByClassName("color_strip")[0];
    color_strip.classList.add("yellow");
    color_strip.classList.remove("green");
});

socket.on('user list', function(user_list) {
    online_users = user_list;
    update_user_list();

    setTimeout(function(){
        socket.emit('request user list');
    }, 5000);
});

socket.on('public key', function(data){
    console.log(data);
    server_public_key = data['public_key'];
    login_view = document.getElementById("login_view");
    login_view.classList.add("hidden");
    login_view.children[0].children[5].classList.remove("lds-ellipsis");
    login_view.children[0].children[5].addEventListener("click", handle_login);
    color_strip = document.getElementsByClassName("color_strip")[0];
    color_strip.classList.add("green");
    color_strip.classList.remove("yellow");
});

socket.on('message', function(data) {
    // TODO: decrypt into sender / message
    sender_id = data['sender'];
    message = data['message'];
    append_message_history(sender_id, sender_id, message);

    if (sender_id == current_recipient)
        load_messages();
    else {
        if (unread[sender_id] == null)
            unread[sender_id] = 0;

        unread[sender_id] += 1;
        update_user_list();
    }
});





// Handler functions
async function handle_login() {
    login_card = document.getElementById("login_view").children[0];
    username = login_card.children[1].value;
    nickname = login_card.children[3].value;

    if (username != "") {
        if (nickname == "")
            nickname = username;

        document.getElementById("nickname").innerHTML = nickname;
        keys = await createKeys();
        console.log(keys.publicKey);
        socket.emit('join', {
            username: username,
            nickname: nickname,
            public_key: ""
        });
        login_card.children[6].classList.add("invisible");
        login_card.children[5].classList.add("lds-ellipsis");
        login_card.children[5].removeEventListener("click", handle_login);  // prevent future clicks
        setTimeout(function(){
            if (login_card.children[5].classList.contains("lds-ellipsis")) {
                login_card.children[5].classList.remove("lds-ellipsis");
                login_card.children[5].addEventListener("click", handle_login);
                login_card.children[6].innerHTML = '... an error has occurred. Please try again ...';
                login_card.children[6].classList.remove("invisible");
            }
        }, 10000);
    } else {
        login_card.children[1].classList.add("error");
        setTimeout(function(){
            login_card.children[1].classList.remove('error');
        }, 500);
        login_card.children[1].focus();
    }
}

function update_user_list() {
    html = '';

    for (var user in online_users) {  // dynamically add user to user list on the side
        if (user == username)
            continue;

        html += '<div class="user unselectable" id="';
        html += user;
        html += '"><div class="flex-row"><img src="static/img/avatar.png"><div class="username">';
        html += online_users[user]['nickname'];
        html += '</div>';

        if (unread[user] != null && unread[user] != 0)
            html += '<div class="notification"></div>';

        html += '</div><div class="divider"></div></div>';
    }

    if (html == '') {
        html = '<p>...looks like no one is online...</p>';
    }

    user = document.getElementById("online_users");
    user.innerHTML = html;

    for (var user in online_users) {  // add event listener to each item after its being added to the html
        entry = document.getElementById(user);

        if (entry != null)
            entry.addEventListener("click", initiate_chat);
    }
}

function initiate_chat(event) {
    parent = event.srcElement;

    while (parent.id == "")
        parent = parent.parentElement;

    chat = document.getElementById("chat");
    recipient_nickname = chat.children[1].children[0].children[1];
    textfield = document.getElementById("chat_input").children[0];

    recipient_nickname.innerHTML = online_users[parent.id]['nickname'];
    textfield.dataset.recipient = parent.id;  // stores recipient's username in input tag for sending later
    current_recipient = parent.id;
    load_messages();
    chat.children[0].classList.add("hidden");  // hide placeholder
    chat.children[1].classList.remove("hidden");  // show actual chat area

    if (parent.children[0].children.length == 3) {  // hide notification
        console.log("hiding");
        unread[parent.id] = 0;
        parent.children[0].children[2].classList.add("hidden");
    }

    textfield.focus();
}

function send_message(){
    textfield = document.getElementById("chat_input").children[0];

    if (textfield.value != "") {
        recipient_id = textfield.dataset.recipient;
        append_message_history(recipient_id, username, textfield.value);
        load_messages(recipient_id);
//        TODO: encryption
//        recipient_public_key = online_users[recipient]["public_key"]
//        encrypts message and sender into a package with recipient_public_key
//        encrypts the package and recipient with server keys
//
//        socket.emit('message', {
//                recipient: recipient,
//                package: ...
//        })


        socket.emit('message', {
                sender: username,
                recipient: recipient_id,
                message: textfield.value
        })
        textfield.value = '';
        textfield.focus();
    }
}

function append_message_history(recipient_id, sender_id, message) {
    // message history is indexed by the recipient_id. send_id is used to keep track of who
    // send the message in this chat (you or the other person)
    if (message_history[recipient_id] == null) {
        message_history[recipient_id] = [];
    }

    message_history[recipient_id].push({
        sender: sender_id,
        message: message
    });
}


function load_messages() {
    chat_area = document.getElementById("chat").children[1].children[1];
    chat_area.innerHTML = "";

    for (i in message_history[current_recipient]) {
        data = message_history[current_recipient][i];

        if (data['sender'] == username)
            chat_area.innerHTML += '<div class="message right">' + data['message'] + '</div>';
        else
            chat_area.innerHTML += '<div class="message left">' + data['message'] + '</div>';
    }

    if (chat_area.children.length != 0)
        chat_area.lastChild.scrollIntoView();
}
