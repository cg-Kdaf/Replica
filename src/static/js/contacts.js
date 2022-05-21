var socket = io();

function request_strava_athletes() {
    var items_nb = 20;
    var page = 0;
    socket.emit('get_strava_athletes', items_nb.toLocaleString() + " " + page.toLocaleString());
}

function remove_child_except_hidden(node, class_name) {
    var elts = node.getElementsByClassName(class_name);
    var length = elts.length;
    for (var i = length-1; i > 0; i--) {
        if (!elts[i].classList.contains('hidden')) {
            elts[i].remove();
        }
    }
}

function strava_to_contact() {
    var id = this.parentNode.dataset.id;
    socket.emit('create_contact_from_strava', id);
}


function draw_contacts_strava(contacts_list) {
    var contact_elt = document.getElementsByClassName("strava-contact contact-item hidden")[0];
    for (var i = 0; i < contacts_list.length; i++) {
        var element = contact_elt.cloneNode(deep=true);
        element.dataset.id = contacts_list[i]["id"];
        element.className = "strava-contact contact-item";
        var name_field = element.getElementsByClassName("full-name")[0];
        name_field.textContent = contacts_list[i]["firstname"] + " " + contacts_list[i]["lastname"];
        var image = element.getElementsByClassName("profile")[0];
        image.src = contacts_list[i]["picture_medium"];
        var image = element.getElementsByClassName("location")[0];
        image.textContent = contacts_list[i]["city"];
        if (contacts_list[i]["contact_id"] == null) {
            var add_btn = element.getElementsByClassName("plus-btn")[0];
            add_btn.className = "plus-btn";
            add_btn.onclick = strava_to_contact;
        }else{
            var contact_name = element.getElementsByClassName("people-name")[0];
            contact_name.textContent = contacts_list[i]["contact_first_name"] + " " + contacts_list[i]["contact_last_name"];
        }
        contact_elt.parentNode.appendChild(element);
    }
}

function init_socket_receiver() {
    socket.on('json', function(event) {
        data = event["data"];
        switch(event["title"]) {
            case "strava_athletes":
                draw_contacts_strava(data);
                break;
        }
    });
}

function main() {
    init_socket_receiver();
    request_strava_athletes();
}

main();