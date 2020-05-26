// let socket = io.connect('https://' + document.domain + ':' + location.port, {secure: true});
// let socket = io.connect('https://64.227.56.166', {secure: true});
// let socket = io.connect()
let socket = io()
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
    encoded = await encode(message)
    encrypted = await encrypt(encoded, keys.publicKey)
    decrypted = await decrypt(encrypted, keys.privateKey)
    decoded = await decode(decrypted)
    console.log("Printing decrypted message")
    console.log(decoded)
}

function encrypt(data, publicKey){
    return crypto.subtle.encrypt(
        {
            name: "RSA-OAEP",
            //label: Uint8Array([...]) //optional
        },
        publicKey, //from generateKey or importKey above
        data //ArrayBuffer of data you want to encrypt
    )
}

function decrypt(data, privateKey){
    return crypto.subtle.decrypt(
        {
            name: "RSA-OAEP",
            //label: Uint8Array([...]) //optional
        },
        privateKey,
        data //ArrayBuffer of the data
    )
}

function encode(message){
    let encoder = new TextEncoder();
    return encoder.encode(message);
}

function decode(message){
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

socket.on('connected', function() {
    login_view = document.getElementById("login_view");
    login_view.classList.add("hidden");
    login_view.children[0].children[5].classList.remove("lds-ellipsis");
    login_view.children[0].children[5].addEventListener("click", handle_login);
    color_strip = document.getElementsByClassName("color_strip")[0];
    color_strip.classList.add("green");
    color_strip.classList.remove("yellow");
});

socket.on('public key', function(data){
    server_public_key = data['public_key'];
});

socket.on('message', function(data) {
    decrypt(data, keys.privateKey)
    .then (function (decryptedData) {
        decoded = decode(decryptedData);
        json = JSON.parse(decoded);
        append_message_history(json['sender'], json['sender'], json['message']);

        if (json['sender'] == current_recipient)
            load_messages();
        else {
            if (unread[json['sender']] == null)
                unread[json['sender']] = 0;

            unread[json['sender']] += 1;
            update_user_list();
        }
    })
});




// Handler functions
function handle_login() {
    login_card = document.getElementById("login_view").children[0];
    username = login_card.children[1].value;
    nickname = login_card.children[3].value;

    if (username != "") {
        if (nickname == "")
            nickname = username;

        crypto.subtle.generateKey(  // GENERATING RSA KEY-PAIR
            {
                name: "RSA-OAEP",
                modulusLength: 2048, //can be 1024, 2048, or 4096
                publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
                hash: {name: "SHA-256"}, //can be "SHA-1", "SHA-256", "SHA-384", or "SHA-512"
            },
            true, //whether the key is extractable (i.e. can be used in exportKey)
            ["encrypt", "decrypt"] //must be ["encrypt", "decrypt"] or ["wrapKey", "unwrapKey"]
        ).then(function(generated_keys) {
            keys = generated_keys;
            return window.crypto.subtle.exportKey('jwk', keys.publicKey);
        }).then (function(public_key){
            socket.emit('join', {
                username: username,
                nickname: nickname,
                public_key: public_key
            });
        });

        document.getElementById("nickname").innerHTML = nickname;
        login_card.children[6].classList.add("invisible");
        login_card.children[5].classList.add("lds-ellipsis");
        login_card.children[5].removeEventListener("click", handle_login);  // prevent future clicks

        setTimeout(function(){  // login request probably timed out, allow user to try again
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

        crypto.subtle.importKey('jwk', online_users[recipient_id]['public_key'], { // import recipient's public key
            name: 'RSA-OAEP',
            hash: {name: 'SHA-256'}
        }, true, ['encrypt'])
        .then (function (importedKey){  // encode it (UTF-8), then encrypt it
            encoded = encode(JSON.stringify({
                sender: username,
                message: textfield.value
            }));
            encrypt(encoded, importedKey)
            .then (function (encrypted) {
                socket.emit('message', {
                    encrypted: encrypted,
                    recipient: recipient_id
                })
                textfield.value = '';
                textfield.focus();
            });
        });

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
