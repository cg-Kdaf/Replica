
var calendars = [];
var today = new Date();
const calendar = document.getElementById("calendar");
var timeline = document.createElement("div");
timeline.className = "timeline";
var time_marker = document.createElement("div");
time_marker.className = "time-marker";
for (var i = 0; i < 24; i++) {
    var marker = time_marker.cloneNode();
    marker.textContent = i.toLocaleString()+":00";
    if (i<10) {
        marker.textContent = "0" + marker.textContent;
    }
    timeline.appendChild(marker);
}

var dateline = document.createElement("div");
dateline.className = "dateline";
var weekday = document.createElement("div");
weekday.className = "weekday-marker";
var days_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
for (var i = 0; i < 7; i++) {
    var marker = weekday.cloneNode();
    marker.textContent = days_list[i].slice(0, 3) + " 00";
    dateline.appendChild(marker);
}

var days = document.createElement("div");
days.className = "days";
var time_grid = document.createElement("div");
time_grid.className = "timegrid";
var grid_case = document.createElement("div");
grid_case.className = "gridcase";
for (var i = 0; i < 7; i++) {
    for (var j = 0; j < 24; j++) {
        var grid_case_ = grid_case.cloneNode(deep=true);
        grid_case_.style.gridColumn = i+1;
        grid_case_.style.gridRow = j+1;
        time_grid.appendChild(grid_case_);
    }
}
var events = document.createElement("div");
events.className = "events";
for (var i = 0; i < 7; i++) {
    var event_ = events.cloneNode(deep=true);
    days.appendChild(event_);
}
calendar.appendChild(dateline);
calendar.appendChild(timeline);
calendar.appendChild(time_grid);
calendar.appendChild(days);


var day = new Date(today.getTime());
if (day.getDay() != 1) {
    day.setDate(day.getDate() - ((day.getDay()+6)%7));
}
var start_day = new Date(day.getTime());
start_day.setHours(0);
start_day.setMinutes(0);
start_day.setMilliseconds(0);
var days_streak = 7;


var dates = document.getElementsByClassName("weekday-marker");
function update_dateline() {
    var day = new Date(start_day.getTime());
    for (var i = 0; i < dates.length; i++) {
        dates[i].innerHTML = dates[i].innerHTML.slice(0, 4) + day.getDate();
        day.setDate(day.getDate() + 1);
    }
}
update_dateline();

var socket = io();
function request_events() {
    socket.emit('get_events', start_day.getTime().toLocaleString()+" "+days_streak.toLocaleString());
}
function request_calendars() {
    socket.emit('get_calendars', "");
}
request_calendars();
request_events();
socket.on('message', function(event) {
    console.log(`Data received from server: ${event}`);
});

function change_view_range(start_day_, days_streak_) {
    start_day = start_day_;
    days_streak = days_streak_;
}

function draw_events(events_list) {
    var days = document.getElementsByClassName("days")[0].childNodes;
    for (var i = 0; i < days.length; i++) {
        days[i].innerHTML="";
    }
    for (var i = 0; i < events_list.length; i++) {
        var event_ = events_list[i];
        var event_color = 'var(--calendar-color-'+event_["cal_id"].toLocaleString()+")";
        var start = new Date(event_["dt_start"]);
        var end = new Date(event_["dt_end"]);
        var day = (start.getDay()+6)%7;
        var time_start = start.getHours() * 60 + start.getMinutes();
        var time_end = end.getHours() * 60 + end.getMinutes();
        var event_elt = document.createElement("div");
        event_elt.className = "event";
        event_elt.dataset.cal_id = event_["cal_id"];
        var event_title = document.createElement("p");
        event_title.className = "title";
        event_title.textContent = event_["summary"];
        event_elt.appendChild(event_title);
        event_elt.style.top = (time_start/1440*100).toLocaleString()+"%";
        event_elt.style.height = ((time_end-time_start)/1440*100).toLocaleString()+"%";
        event_elt.style.backgroundColor = event_color;
        days[day].appendChild(event_elt);
    }
    update_events_visibility();
}

socket.on('json', function(event) {
    console.log(`Data received from server: ${event["title"]}`);
    data = event["data"];
    switch(event["title"]) {
        case "events":
            draw_events(data);
            break;
        case "calendars":
            calendars = data;
            update_calendar_list();
            break;
    }
});


var next_button = document.getElementById("next-week-bt");
var previous_button = document.getElementById("previous-week-bt");

next_button.onclick = function() {
    start_day.setDate(start_day.getDate() + 7);
    update_dateline();
    request_events();
};

previous_button.onclick = function() {
    start_day.setDate(start_day.getDate() - 7);
    update_dateline();
    request_events();
};

var refresh_cal_button = document.getElementById("refresh-calendars");

refresh_cal_button.onclick = function() {
    socket.emit('refresh_calendars', "");
};


function remove_child_except_hidden(node, class_name) {
    for (var i = 0; i < node.children.length; i++) {
        var className = node.children[i].className;
        if (className.search("hidden") == -1 && className.search(class_name) != -1) {
            node.removeChild(node.children[i]);
        }
    }
}

function update_events_visibility() {
    var cals_by_id = {};
    for (var i=0;i<calendars.length; i++) {
        cals_by_id[calendars[i]["id"]] = calendars[i];
    }
    var events = document.getElementsByClassName("event");
    for (var i = 0; i < events.length; i++) {
        var cal = cals_by_id[events[i].dataset.cal_id]
        if (cal["shown"] == 1 && cal["activated"] == 1)
        {
            events[i].style.display = "block";
        } else {
            events[i].style.display = "none";
        }
    }
}

function update_cal_visibility() {
    var cals_by_id = {};
    for (var i=0;i<calendars.length; i++) {
        cals_by_id[calendars[i]["id"]] = calendars[i];
    }
    var checked = this.checked;
    var cal_id = this.parentNode.id.toLocaleString();
    if (checked) {
        cals_by_id[cal_id]["shown"] = 1;
    } else {
        cals_by_id[cal_id]["shown"] = 0;
    }
    update_events_visibility();
    socket.emit('set_cal_visibility', cal_id.toLocaleString()+" "+checked.toLocaleString());
}

// Colors

var colorList = [ '000000', '993300', '333300', '003300', '003366', '000066', '333399', '333333', 
'660000', 'FF6633', '666633', '336633', '336666', '0066FF', '666699', '666666', 'CC3333', 'FF9933', '99CC33', '669966', '66CCCC', '3366FF', '663366', '999999', 'CC66FF', 'FFCC33', 'FFFF66', '99FF66', '99CCCC', '66CCFF', '993366', 'CCCCCC', 'FF99CC', 'FFCC99', 'FFFF99', 'CCffCC', 'CCFFff', '99CCFF', 'CC99FF', 'FFFFFF' ];
var settings_panel = document.getElementById('calendar-settings');
var settings_desactivate_btn = document.getElementById('desactivate-cal-btn');
var picker = document.getElementById('color-picker');
var callpicker;
function send_color(cal_id, color) {
    socket.emit('set_cal_color', cal_id.toLocaleString()+" "+color);
}

for (var i = 0; i < colorList.length; i++ ) {
    picker.innerHTML += ('<li class="color-item" data-hex="' + '#' + colorList[i] + '" style="background-color:' + '#' + colorList[i] + ';"></li>');
}
var color_items = document.getElementsByClassName('color-item');
for (var i = 0; i < color_items.length; i++ ) {
    color_items[i].onclick = function () {
        var color_var_name = '--calendar-color-'+callpicker.parentNode.id.toLocaleString();
        document.documentElement.style.setProperty(color_var_name, this.style.backgroundColor);
        send_color(callpicker.parentNode.id, this.style.backgroundColor);
    };
}

document.body.onclick = function () {
    settings_panel.style.display = "none";
};

settings_desactivate_btn.onclick = function () {
    var cal_id = callpicker.parentNode.id.toLocaleString();
    var cals_by_id = {};
    for (var i=0;i<calendars.length; i++) {
        cals_by_id[calendars[i]["id"]] = calendars[i];
    }
    cals_by_id[cal_id]["activated"] = 0;
    socket.emit('set_cal_activation', cal_id+" false");
    update_events_visibility();
    update_calendar_list();
};


function update_calendar_list() {
    var calendar_list = document.getElementById("calendar-list");
    remove_child_except_hidden(calendar_list, "calendar-item");
    var cal_elt_template = document.getElementsByClassName("calendar-item hidden")[0];

    for (var i = 0; i < calendars.length; i++) {
        var cal = calendars[i];
        var color_var_name = '--calendar-color-'+cal["id"].toLocaleString();
        document.documentElement.style.setProperty(color_var_name, cal["color"]);
        var cal_elt = cal_elt_template.cloneNode(deep=true);
        cal_elt.className = "calendar-item";
        cal_elt.id = cal["id"];
        if (cal["activated"] == 0) {
            cal_elt.style.display = "none";
        }
        var checkbox = cal_elt.children[0];
        checkbox.onchange = update_cal_visibility;
        checkbox.checked = cal["shown"];
        var event_color = 'var('+color_var_name+")";
        checkbox.style.accentColor = event_color;
        checkbox.style.backgroundColor = event_color;
        var title = cal_elt.children[1];
        title.innerHTML = cal["title"].substring(0, 30);

        var settings = cal_elt.children[2];
        settings.onclick = function(event) {
            callpicker = this;
            event.stopPropagation();
            settings_panel.style.display = "block";
            var actual_pos = this.getBoundingClientRect();
            settings_panel.style.top = actual_pos.top.toLocaleString() + "px";
            settings_panel.style.left = (actual_pos.right).toLocaleString() + "px";
        };
        calendar_list.appendChild(cal_elt);
    }
}
