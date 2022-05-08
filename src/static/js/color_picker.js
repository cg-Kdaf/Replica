var colorList = [ '000000', '993300', '333300', '003300', '003366', '000066', '333399', '333333', 
'660000', 'FF6633', '666633', '336633', '336666', '0066FF', '666699', '666666', 'CC3333', 'FF9933', '99CC33', '669966', '66CCCC', '3366FF', '663366', '999999', 'CC66FF', 'FFCC33', 'FFFF66', '99FF66', '99CCCC', '66CCFF', '993366', 'CCCCCC', 'FF99CC', 'FFCC99', 'FFFF99', 'CCffCC', 'CCFFff', '99CCFF', 'CC99FF', 'FFFFFF' ];
var picker = document.getElementById('color-picker');
var callpicker;
var socket = io();
function send_color(cal_id, color) {
    socket.emit('set_cal_color', cal_id.toLocaleString()+" "+color);
}

for (var i = 0; i < colorList.length; i++ ) {
    picker.innerHTML += ('<li class="color-item" data-hex="' + '#' + colorList[i] + '" style="background-color:' + '#' + colorList[i] + ';"></li>');
}
var color_items = document.getElementsByClassName('color-item');
for (var i = 0; i < color_items.length; i++ ) {
    color_items[i].onclick = function () {
        callpicker.style.backgroundColor = this.style.backgroundColor;
        send_color(callpicker.dataset.id, this.style.backgroundColor);
    };
}

document.body.onclick = function () {
    picker.style.display = "none";
};

var callpickers = document.getElementsByClassName('call-picker');
for (var i = 0; i < callpickers.length; i++ ) {
    callpickers[i].onclick = function(event) {
        callpicker = this;
        event.stopPropagation();
        picker.style.display = "block";
        var actual_pos = this.getBoundingClientRect()
        picker.style.top = actual_pos.top.toLocaleString() + "px";
        picker.style.left = (actual_pos.right).toLocaleString() + "px";
    };
}


var restoring_btn = document.getElementsByClassName('restore-cal-button');
for (var i = 0; i < restoring_btn.length; i++ ) {
    restoring_btn[i].onclick = function() {
        cal_id = this.parentElement.id.split("-")[2];
        socket.emit('set_cal_activated', cal_id.toLocaleString()+" true");
    };
}
