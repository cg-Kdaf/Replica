var socket = io();
var list_shown = "contacts";

function request_strava_athletes() {
    list_shown = "strava";
    var items_nb = 20;
    var page = 0;
    socket.emit('get_strava_athletes', items_nb.toLocaleString() + " " + page.toLocaleString());
}

function request_contacts() {
    list_shown = "contacts";
    var items_nb = 20;
    var page = 0;
    socket.emit('get_contacts', items_nb.toLocaleString() + " " + page.toLocaleString());
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

function draw_contacts_strava(contacts_list) {
    function strava_to_contact(self) {
        self.stopPropagation();
        var id = this.parentNode.parentNode.dataset.id;
        socket.emit('create_contact_from_strava', id);
    }
    function draw_activity_common(parent, activity) {
        var new_row = parent.cloneNode(deep=true);
        var link = new_row.getElementsByClassName("link")[0];
        link.setAttribute('href', 'https://www.strava.com/activities/' + activity["activity_id"]);
        new_row.className = "common-activity contact-item";
        var date = new_row.getElementsByClassName("date")[0];
        var date_ = new Date(activity["start_date"]*1000);
        date.textContent = date_.toLocaleDateString("en-us", {month: 'long', year: 'numeric', day: 'numeric', hour: 'numeric', minute:'2-digit'});
        var type = new_row.getElementsByClassName("type")[0];
        type.textContent = activity["type"];
        var name = new_row.getElementsByClassName("name")[0];
        name.textContent = activity["name"];
        var distance = new_row.getElementsByClassName("distance")[0];
        value = activity["distance"];
        if (value < 3000) {
            value = value + " m";
        }else{
            value = (value/1000).toFixed(2) + " km";
        }
        distance.textContent = value;
        var elevation = new_row.getElementsByClassName("elevation")[0];
        elevation.textContent = activity["total_elevation_gain"].toFixed(2) + " m D+";
        parent.parentNode.appendChild(new_row);
    }
    var no_contact_elt = document.getElementsByClassName("no-contact contact-item")[0];
    if (contacts_list.length == 0) {
        no_contact_elt.className = "no-contact contact-item";
        return;
    }
    no_contact_elt.className = "no-contact contact-item hidden";

    var contact_elt = document.getElementsByClassName("strava-contact contact-item hidden")[0];
    var all_contacts_elts = {};
    var elts = document.getElementsByClassName("strava-contact contact-item");
    for (var i = 0; i < elts.length; i++)
    {
        all_contacts_elts[elts[i].dataset.id] = elts[i];
    }

    for (var i = 0; i < contacts_list.length; i++) {
        var element;
        if (all_contacts_elts[contacts_list[i]["id"]] == undefined) {
            element = contact_elt.cloneNode(deep=true);
        }else{
            element = all_contacts_elts[contacts_list[i]["id"]];
        }
        element.dataset.id = contacts_list[i]["id"];
        element.className = "strava-contact contact-item";
        var name_field = element.getElementsByClassName("full-name")[0];
        name_field.textContent = contacts_list[i]["firstname"] + " " + contacts_list[i]["lastname"];
        name_field.parentNode.setAttribute('href', "https://www.strava.com/athletes/" + contacts_list[i]["id"]);
        var image = element.getElementsByClassName("profile")[0];
        image.src = contacts_list[i]["picture_medium"];
        var location = element.getElementsByClassName("location")[0];
        location.textContent = contacts_list[i]["city"];
        var add_btn = element.getElementsByClassName("plus-btn")[0];
        if (contacts_list[i]["contact_id"] == null) {
            add_btn.className = "plus-btn";
            add_btn.onclick = strava_to_contact;
        }else{
            add_btn.className = "plus-btn hidden";
            var contact_name = element.getElementsByClassName("people-name")[0];
            contact_name.textContent = contacts_list[i]["contact_first_name"] + " " + contacts_list[i]["contact_last_name"];
        }
        var details = element.getElementsByClassName("details")[0];
        details.style.display = "none";
        if (contacts_list[i]["activities"]) {
            for (var j = 0; j < contacts_list[i]["activities"].length; j++) {
                draw_activity_common(details.getElementsByClassName("common-activity hidden")[0], contacts_list[i]["activities"][j]);
            }
        }
        var header = element.getElementsByClassName("header")[0];
        header.addEventListener("click", function() {
            var details = this.parentNode.getElementsByClassName("details")[0];
            if (details.style.display == "none") {
                var detail_elts = this.parentNode.parentNode.getElementsByClassName("details");
                for (var j = 0; j < detail_elts.length; j++) {
                    detail_elts[j].style.display = "none";
                }
                details.style.display = "block";
            }else{
                details.style.display = "none";
            }
        });
        if (all_contacts_elts[contacts_list[i]["id"]] == undefined) {
            contact_elt.parentNode.appendChild(element);
        }
    }
}

function draw_contacts(contacts_list) {
    function remove_contact() {
        var id = this.parentNode.parentNode.dataset.id;
        socket.emit('remove_contact', id);
    }
    var no_contact_elt = document.getElementsByClassName("no-contact contact-item")[0];
    if (contacts_list.length == 0) {
        no_contact_elt.className = "no-contact contact-item";
        return;
    }
    no_contact_elt.className = "no-contact contact-item hidden";

    var contact_elt = document.getElementsByClassName("people-contact contact-item hidden")[0];
    var all_contacts_elts = {};
    var elts = document.getElementsByClassName("people-contact contact-item");
    for (var i = 0; i < elts.length; i++)
    {
        all_contacts_elts[elts[i].dataset.id] = elts[i];
    }

    for (var i = 0; i < contacts_list.length; i++) {
        var element;
        if (all_contacts_elts[contacts_list[i]["id"]] == undefined) {
            element = contact_elt.cloneNode(deep=true);
        }else{
            element = all_contacts_elts[contacts_list[i]["id"]];
        }
        element.dataset.id = contacts_list[i]["id"];
        element.className = "people-contact contact-item";
        var name_field = element.getElementsByClassName("full-name")[0];
        name_field.textContent = contacts_list[i]["first_name"] + " " + contacts_list[i]["last_name"];
        var image = element.getElementsByClassName("profile")[0];
        image.src = contacts_list[i]["picture"];
        var details = element.getElementsByClassName("details")[0];
        details.style.display = "none";
        var remove_contact_elt = element.getElementsByClassName("remove-contact")[0];
        remove_contact_elt.onclick = remove_contact;
        var header = element.getElementsByClassName("header")[0];
        header.addEventListener("click", function() {
            var details = this.parentNode.getElementsByClassName("details")[0];
            if (details.style.display == "none") {
                var detail_elts = this.parentNode.getElementsByClassName("details");
                for (var j = 0; j < detail_elts.length; j++) {
                    detail_elts[j].style.display = "none";
                }
                details.style.display = "block";
            }else{
                details.style.display = "none";
            }
        });
        if (all_contacts_elts[contacts_list[i]["id"]] == undefined) {
            contact_elt.parentNode.appendChild(element);
        }
    }
}

function contacts_lists_change_view() {
    var contacts_radio_btn = document.getElementById("contactChoice1");
    var strava_radio_btn = document.getElementById("contactChoice2");
    var google_radio_btn = document.getElementById("contactChoice3");
    contacts_radio_btn.onchange = request_contacts;
    strava_radio_btn.onchange = request_strava_athletes;
}

function init_socket_receiver() {
    socket.on('json', function(event) {
        data = event["data"];
        switch(event["title"]) {
            case "refresh":
                if (list_shown == "contacts") {
                    draw_contacts(data);
                }else if (list_shown == "strava") {
                    draw_contacts_strava(data);
                }
                break;
            case "strava_athletes":
                var contacts_list_elt = document.getElementsByClassName("contact-list")[0];
                remove_child_except_hidden(contacts_list_elt, "contact-item");
                draw_contacts_strava(data);
                break;
            case "contacts":
                var contacts_list_elt = document.getElementsByClassName("contact-list")[0];
                remove_child_except_hidden(contacts_list_elt, "contact-item");
                draw_contacts(data);
                break;
        }
    });
}

function main() {
    init_socket_receiver();
    contacts_lists_change_view();
    request_contacts();
}

main();