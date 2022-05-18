
var calendars = [];
var events_by_id = {};
const today = new Date();
var days_streak;
var start_day;
var callpicker;
var socket = io();

function calendar_init() {
    const calendar = document.getElementById("calendar");
    const event_details = document.getElementById("event-details");
    event_details.onclick = function(self) {self.stopPropagation();};
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
    
    var multi_day_events = document.createElement("div");
    multi_day_events.className = "multiday-events";
    
    var day_grid = document.createElement("div");
    day_grid.className = "day-grid";
    var grid_case = document.createElement("div");
    grid_case.className = "gridcase";
    for (var i = 0; i < 7; i++) {
        var grid_case_ = grid_case.cloneNode(deep=true);
        grid_case_.style.gridColumn = i+1;
        day_grid.appendChild(grid_case_);
    }
    
    var days = document.createElement("div");
    days.className = "days";
    var time_grid = document.createElement("div");
    time_grid.className = "timegrid";
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
    
    calendar.appendChild(day_grid);
    calendar.appendChild(dateline);
    calendar.appendChild(multi_day_events);
    calendar.appendChild(timeline);
    calendar.appendChild(time_grid);
    calendar.appendChild(days);

    var day = new Date(today.getTime());
    if (day.getDay() != 1) {
        day.setDate(day.getDate() - ((day.getDay()+6)%7));
    }
    start_day = new Date(day.getTime());
    start_day.setHours(0);
    start_day.setMinutes(0);
    start_day.setSeconds(0);
    start_day.setMilliseconds(0);
    days_streak = 7;
    draw_prev_next_btn();
    update_dateline();
    init_socket_receiver();
    request_calendars();
    request_events();
    init_calendar_settings();
}



function update_dateline() {
    var dates = document.getElementsByClassName("weekday-marker");
    var day = new Date(start_day.getTime());
    for (var i = 0; i < dates.length; i++) {
        dates[i].innerHTML = dates[i].innerHTML.slice(0, 4) + day.getDate();
        if (day.getDate() == today.getDate() && day.getMonth() == today.getMonth()) {
            dates[i].style.border = "solid 0.5rem deepskyblue";
            dates[i].style.backgroundColor = "deepskyblue";
        }else{
            dates[i].style.border = "";
            dates[i].style.backgroundColor = "";
        }
        day.setDate(day.getDate() + 1);
    }
}
function request_events() {
    socket.emit('get_events', start_day.getTime().toLocaleString()+" "+days_streak.toLocaleString());
}
function request_calendars() {
    socket.emit('get_cal_list', "");
}
function init_socket_receiver() {
    socket.on('json', function(event) {
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

function event_strava_details(event, strava_details) {

    function hide_null(data, container) {
        if (data==0) {
            container.style.display = "none";
        }else{
            container.style.display = "block";
        }
    }

    if (event["strava_act_id"] != null) {
        strava_details.style.display = "block";
        var value = 0;
        var kudos_count = strava_details.getElementsByClassName("kudos")[0].getElementsByClassName("count")[0];
        kudos_count.innerHTML = event["kudos_count"];
        var comments_count = strava_details.getElementsByClassName("comments")[0].getElementsByClassName("count")[0];
        comments_count.innerHTML = event["comment_count"];
        var athletes_count = strava_details.getElementsByClassName("athletes")[0].getElementsByClassName("count")[0];
        athletes_count.innerHTML = event["athlete_count"] - 1;

        var distance = strava_details.getElementsByClassName("distance")[0].querySelectorAll("strong")[0];
        value = event["distance"];
        if (value < 3000) {
            distance.innerHTML = value + " m";
        }else{
            distance.innerHTML = (value/1000).toFixed(2) + " km";
        }
        hide_null(value, strava_details.getElementsByClassName("distance")[0]);

        var time = strava_details.getElementsByClassName("time")[0].querySelectorAll("strong")[0];
        value = event["moving_time"];
        if (value < 3600) {
            time.innerHTML = (value/60).toFixed(0) + " min";
        }else{
            time.innerHTML = Math.floor(value/3600) + ":" + (value/60 - Math.floor(value/3600)*60).toFixed(0);
        }
        hide_null(value, strava_details.getElementsByClassName("time")[0]);

        var elevation = strava_details.getElementsByClassName("elevation")[0].querySelectorAll("strong")[0];
        elevation.innerHTML = event["total_elevation_gain"] + " m";
        hide_null(event["total_elevation_gain"], strava_details.getElementsByClassName("elevation")[0]);

        var power = strava_details.getElementsByClassName("avg-power")[0].querySelectorAll("strong")[0];
        power.innerHTML = event["average_watts"] + " W";
        hide_null(event["average_watts"], strava_details.getElementsByClassName("avg-power")[0]);

        var energy = strava_details.getElementsByClassName("energy")[0].querySelectorAll("strong")[0];
        energy.innerHTML = event["kilojoules"] + " kJ";
        hide_null(event["kilojoules"], strava_details.getElementsByClassName("energy")[0]);

        var energy = strava_details.getElementsByClassName("speed")[0].querySelectorAll("strong")[0];
        value = event["average_speed"];
        energy.innerHTML = (value*3.6).toFixed(1) + " km/h";
        hide_null(value, strava_details.getElementsByClassName("speed")[0]);

        var activity_link = strava_details.getElementsByClassName("link")[0];
        activity_link.setAttribute('href', 'https://www.strava.com/activities/' + event["strava_id"]);
    }else{
        strava_details.style.display = "none";
    }
}


function event_details_draw(self) {
    var event_data = events_by_id[this.dataset.id];
    self.stopPropagation();
    const event_details = document.getElementById("event-details");
    var infos = event_details.getElementsByClassName("event-informations")[0];
    var summary = infos.getElementsByClassName("summary")[0];
    var date = infos.getElementsByClassName("date")[0];
    var description = infos.getElementsByClassName("description")[0];
    summary.innerHTML = event_data['name'];
    var start = new Date(event_data["dt_start"]*1000);
    var end = new Date(event_data["dt_end"]*1000);
    if (start.getDate() == end.getDate()) {
        date.innerHTML = start.toLocaleDateString("en-us", { weekday: 'long', month: 'long', day: 'numeric' }) + " - " + start.toLocaleTimeString("en-us", {hour: 'numeric', minute:'2-digit'}) + " - " + end.toLocaleTimeString("en-us", {hour: 'numeric', minute:'2-digit'});
    }else{
        date.innerHTML = start.toLocaleString("en-us", { weekday: 'long', month: 'long', day: 'numeric', hour: 'numeric', minute:'2-digit'}) + " - " + end.toLocaleString("en-us", { weekday: 'long', month: 'long', day: 'numeric', hour: 'numeric', minute:'2-digit'});
    }
    description.innerHTML = event_data['description'];
    event_strava_details(event_data, infos.getElementsByClassName("strava-details")[0]);
    var actual_pos = this.getBoundingClientRect();
    var details_pos = event_details.getBoundingClientRect();
    if (event_details.style.display != "block") {
        event_details.style.display = "block";
        details_pos = event_details.getBoundingClientRect();
        event_details.style.display = "none";
    }
    var day = this.parentNode;
    var days = day.parentNode;
    var day_pos = day.getBoundingClientRect();
    var days_pos = days.getBoundingClientRect();
    if (day.className == "multiday-events") {
        if (actual_pos.left+details_pos.width < day_pos.right) {
            event_details.style.left = actual_pos.left.toLocaleString().replace(",", "") + "px";
        }else{
            event_details.style.left = (actual_pos.right - details_pos.width).toLocaleString().replace(",", "") + "px";
        }
        event_details.style.top = day_pos.bottom.toLocaleString().replace(",", "") + "px";
    }else{
        if (day_pos.left-days_pos.left < days_pos.right-day_pos.right) {
            event_details.style.left = day_pos.right.toLocaleString().replace(",", "") + "px";
        }else{
            event_details.style.left = (day_pos.right - day_pos.width - details_pos.width).toLocaleString().replace(",", "") + "px";
        }
        if (actual_pos.top+details_pos.height > day_pos.bottom) {
            event_details.style.top = (day_pos.bottom - details_pos.height).toLocaleString().replace(",", "") + "px";
        }else{
            event_details.style.top = actual_pos.top.toLocaleString().replace(",", "") + "px";
        }
    }
    event_details.style.display = "block";
}

function draw_events(events_list) {
    var cals_by_id = {};
    events_by_id = {};
    for (var i=0;i<calendars.length; i++) {
        cals_by_id[calendars[i]["id"]] = calendars[i];
    }
    var days = document.getElementsByClassName("days")[0].children;
    var multiday_events = document.getElementsByClassName("multiday-events")[0];
    var enddate = new Date(start_day.getTime());
    enddate.setDate(start_day.getDate() + days_streak);
    for (var i = 0; i < days.length; i++) {
        multiday_events.innerHTML="";
        days[i].innerHTML="";
        if (start_day<today && today<enddate && (((today.getDay()+6)%7) == i)) {
            var time_now = today.getHours() * 60 + today.getMinutes();
            var cursor_now = document.createElement("div");
            cursor_now.className = "cursor-now";
            cursor_now.style.top = (time_now/1440*100).toLocaleString()+"%";
            days[i].appendChild(cursor_now);
        }
    }
    for (var i = 0; i < events_list.length; i++) {
        var event_ = events_list[i];
        events_by_id[event_["id"]] = event_;
        var event_color = 'var(--calendar-color-'+event_["cal_id"].toLocaleString()+")";
        var start = new Date(event_["dt_start"]*1000);
        var end = new Date(event_["dt_end"]*1000);
        var day = (start.getDay()+6)%7;
        var time_start = start.getHours() * 60 + start.getMinutes();
        var time_end = end.getHours() * 60 + end.getMinutes();
        var event_elt = document.createElement("div");
        event_elt.className = "event";
        event_elt.dataset.cal_id = event_["cal_id"];
        event_elt.dataset.id = event_["id"];
        event_elt.onclick = event_details_draw;
        var event_title = document.createElement("p");
        event_title.className = "title";
        event_title.textContent = event_["name"];
        event_elt.appendChild(event_title);
        event_elt.style.backgroundColor = event_color;
        var cal = cals_by_id[event_elt.dataset.cal_id]
        if (cal["shown"] == 1 && cal["activated"] == 1)
        {
            event_elt.style.display = "block";
        } else {
            event_elt.style.display = "none";
        }
        var col_start = -1;
        var col_end = -1;
        var before = false;
        var after = false;
        if (start < start_day && end > enddate) {
            before = true;
            after = true;
            col_start = 1;
            col_end = 8;
        }
        else if (start < start_day) {
            before = true;
            col_start = 1;
            end.setMilliseconds(end.getMilliseconds()-1);
            col_end = (end.getDay()+6)%7+2;
        }
        else if (end > enddate) {
            after = true;
            col_start = day+1;
            col_end = 8;
        }
        else if ((time_start == 0) && (time_end == 0)) {
            col_start = day+1;
            end.setMilliseconds(end.getMilliseconds()-1);
            col_end = (end.getDay()+6)%7+2;
        }
        else if ((end.getTime() - start.getTime()) > (24*60*60*1000)) {
            col_start = day+1;
            col_end = (end.getDay()+6)%7+2;
        }
        if (col_start != -1) {
            event_elt.style.gridColumnStart = col_start;
            event_elt.style.gridColumnEnd = col_end;
            if (before == true && after == true) {
                event_elt.style.clipPath = "polygon(1rem 0%, calc(100% - 1rem) 0%, 100% 50%, calc(100% - 1rem) 100%, 1rem 100%, 0% 50%)";
                event_elt.style.paddingLeft = "1rem";
                event_elt.style.paddingRight = "1rem";
            }else if (before == true) {
                event_elt.style.clipPath = "polygon(1rem 0%, 100% 0%, 100% 50%, 100% 100%, 1rem 100%, 0% 50%)";
                event_elt.style.paddingLeft = "1rem";
            }else if (after == true) {
                event_elt.style.clipPath = "polygon(0% 0%, calc(100% - 1rem) 0%, 100% 50%, calc(100% - 1rem) 100%, 0% 100%, 0% 50%)";
                event_elt.style.paddingRight = "1rem";
            }
            multiday_events.appendChild(event_elt);
            continue;
        }
        event_elt.style.top = (time_start/1440*100).toLocaleString()+"%";
        event_elt.style.height = ((end-start)/60000/1440*100).toLocaleString()+"%";
        event_elt.style.marginLeft = "0%";
        event_elt.style.borderLeft = "0";
        var event_start = parseInt(event_elt.style.top);
        var event_end = event_start + parseInt(event_elt.style.height);
        var other_events = days[day].getElementsByClassName("event");
        for (var j = 0; j < other_events.length; j++) {
            var j_event = other_events[j];
            if (j_event.classList.contains('hidden')) {
                continue;
            }
            var j_event_start = parseInt(j_event.style.top);
            var j_event_end = j_event_start + parseInt(j_event.style.height);
            if (j_event_start < event_end && event_start < j_event_end) {
                event_elt.style.marginLeft = Math.max(parseInt(j_event.style.marginLeft) + 10,
                parseInt(event_elt.style.marginLeft)).toLocaleString()+"%";
                event_elt.style.borderLeft = event_elt.style.border;
            }
        }
        days[day].appendChild(event_elt);
    }
    update_dateline();
}

function draw_prev_next_btn() {
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
    update_calendar_list();
    socket.emit('set_cal_shown', cal_id.toLocaleString()+" "+checked.toLocaleString());
}

function init_calendar_settings() {
    var view_desactivated_btn = document.getElementsByClassName('calendar-list-view-desactivated')[0];
    var show_desactivated = false;

    view_desactivated_btn.onchange = function () {
        show_desactivated = this.checked;
        update_calendar_list();
    }

    var colorList = [ '000000', '993300', '333300', '003300', '003366', '000066', '333399',
                      '333333', '660000', 'FF6633', '666633', '336633', '336666', '0066FF',
                      '666699', '666666', 'CC3333', 'FF9933', '99CC33', '669966', '66CCCC',
                      '3366FF', '663366', '999999', 'CC66FF', 'FFCC33', 'FFFF66', '99FF66',
                      '99CCCC', '66CCFF', '993366', 'CCCCCC', 'FF99CC', 'FFCC99', 'FFFF99',
                      'CCffCC', 'CCFFff', '99CCFF', 'CC99FF', 'FFFFFF' ];
    var settings_panel = document.getElementById('calendar-settings');
    settings_panel.onclick = function(self) {self.stopPropagation();};
    var settings_desactivate_btn = document.getElementById('desactivate-cal-btn');
    var settings_title_field = settings_panel.getElementsByClassName('name')[0];
    var picker = document.getElementById('color-picker');
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
    const event_details = document.getElementById("event-details");
    document.body.onclick = function () {
        settings_panel.style.display = "none";
        event_details.style.display = "none";
    };
    
    settings_desactivate_btn.onclick = function () {
        var cal_id = callpicker.parentNode.id.toLocaleString();
        var cals_by_id = {};
        for (var i=0;i<calendars.length; i++) {
            cals_by_id[calendars[i]["id"]] = calendars[i];
        }
        if (cals_by_id[cal_id]["activated"]) {
            cals_by_id[cal_id]["activated"] = 0;
        } else {
            cals_by_id[cal_id]["activated"] = 1;
        }
        socket.emit('set_cal_activated', cal_id+" "+cals_by_id[cal_id]["activated"].toLocaleString());
        update_events_visibility();
        update_calendar_list();
    };
    
    settings_title_field.onchange = function (self) {
        var cal_id = callpicker.parentNode.id.toLocaleString();
        var cals_by_id = {};
        for (var i=0;i<calendars.length; i++) {
            cals_by_id[calendars[i]["id"]] = calendars[i];
        }
        cals_by_id[cal_id]["title"] = self.target.value;
        socket.emit('set_cal_title', cal_id+" "+self.target.value);
        update_calendar_list();
    }
}


function update_calendar_list() {
    var calendar_list = document.getElementById("calendar-list");
    remove_child_except_hidden(calendar_list, "calendar-item");
    var cal_elt_template = document.getElementsByClassName("calendar-item hidden")[0];
    var view_desactivated_btn = document.getElementsByClassName('calendar-list-view-desactivated')[0];
    show_desactivated = view_desactivated_btn.checked;
    var settings_panel = document.getElementById('calendar-settings');
    var settings_title_field = settings_panel.getElementsByClassName('name')[0];

    for (var i = 0; i < calendars.length; i++) {
        var cal = calendars[i];
        var color_var_name = '--calendar-color-'+cal["id"].toLocaleString();
        document.documentElement.style.setProperty(color_var_name, cal["color"]);
        var cal_elt = cal_elt_template.cloneNode(deep=true);
        cal_elt.className = "calendar-item";
        cal_elt.id = cal["id"];
        if (cal["activated"] == 0) {
            if (show_desactivated) {
                cal_elt.style.backgroundColor = "rgba(150,150,150, 25)";
            }else{
                cal_elt.style.display = "none";
            }
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
            settings_title_field.value = this.parentNode.children[1].innerHTML;
            settings_panel.style.top = actual_pos.top.toLocaleString() + "px";
            settings_panel.style.left = (actual_pos.right).toLocaleString() + "px";
        };
        calendar_list.appendChild(cal_elt);
    }
}

function main() {
    calendar_init();
}

main();
