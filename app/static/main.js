let socket = io.connect('http://' + document.domain + ':' + location.port);
var server_public_key = null;
var online_users = null;

//TODO: Check if key exists then import

// console.log("KEYS EXIST, GONNA IMPORT")
// window.crypto.subtle.importKey(
//     "jwk", //can be "jwk" (public or private), "spki" (public only), or "pkcs8" (private only)
//     {   //this is an example jwk key, other key types are Uint8Array objects
//         kty: "RSA",
//         e: "AQAB",
//         n: "vGO3eU16ag9zRkJ4AK8ZUZrjbtp5xWK0LyFMNT8933evJoHeczexMUzSiXaLrEFSyQZortk81zJH3y41MBO_UFDO_X0crAquNrkjZDrf9Scc5-MdxlWU2Jl7Gc4Z18AC9aNibWVmXhgvHYkEoFdLCFG-2Sq-qIyW4KFkjan05IE",
//         alg: "RSA-OAEP-256",
//         ext: true,
//     },
//     {   //these are the algorithm options
//         name: "RSA-OAEP",
//         hash: {name: "SHA-256"}, //can be "SHA-1", "SHA-256", "SHA-384", or "SHA-512"
//     },
//     false, //whether the key is extractable (i.e. can be used in exportKey)
//     ["encrypt"] //"encrypt" or "wrapKey" for public key import or
//                 //"decrypt" or "unwrapKey" for private key imports
// )
// .then(function(publicKey){
//     //returns a publicKey (or privateKey if you are importing a private key)
//     console.log(publicKey);
// })
// .catch(function(err){
//     console.error(err);
// });

console.log("KEYS DO NOT EXIST, GONNA GENERATE")
window.crypto.subtle.generateKey(
    {
        name: "RSA-OAEP",
        modulusLength: 2048, //can be 1024, 2048, or 4096
        publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
        hash: {name: "SHA-256"}, //can be "SHA-1", "SHA-256", "SHA-384", or "SHA-512"
    },
    true, //whether the key is extractable (i.e. can be used in exportKey)
    ["encrypt", "decrypt"] //must be ["encrypt", "decrypt"] or ["wrapKey", "unwrapKey"]
)
.then(function(key){
    //returns a keypair object
    console.log(key);
    console.log(key.publicKey);
    console.log(key.privateKey);
})
.catch(function(err){
    console.error(err);
});

// window.crypto.subtle.exportKey(
//     "jwk", //can be "jwk" (public or private), "spki" (public only), or "pkcs8" (private only)
//     key.publicKey //can be a publicKey or privateKey, as long as extractable was true
// )
// .then(function(keydata){
//     //returns the exported key data
//     console.log(keydata);
// })
// .catch(function(err){
//     console.error(err);
// });


socket.on('connect', function() {
    console.log("sending join now")
    socket.emit('join', {
        username: "b",
        public_key: ""
    })

    var form = $('form' ).on( 'submit', function( e ) {
        e.preventDefault()
        let user_name = $( 'input.username' ).val()
        let user_input = $( 'input.message' ).val()

        var usernames = []

        for (var username in online_users)  // this is extracting username (or key) from the json
            usernames.push(username)

        socket.emit( 'message', {
            sender : user_name,
            recipient : username[0],
            message : user_input
        } )
        $( 'input.message' ).val( '' ).focus()
    })
});

socket.on('user list', function(user_list) {
    console.log(user_list)
    online_users = user_list
});

socket.on('public key', function(data){
    console.log(data)
    server_public_key = data['public_key']
});

socket.on( 'message', function( msg ) {
    console.log( msg )
    if( typeof msg.sender !== 'undefined' ) {
    $( 'h3' ).remove()
    $( 'div.message_holder' ).append( '<div><b style="color: #000">'+msg.sender+'</b> '+msg.message+'</div>' )
    }
});