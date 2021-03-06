//button back to previous page
document.getElementById('go-back').addEventListener('click', () => {
    history.back();
});

//formula to count size of obj
Object.size = function(obj) {
    var size = 0,
        key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

// Get the container element
var lineZone = document.getElementById("zone");
// Get all buttons with class="btn" inside the zone
var lines = lineZone.getElementsByClassName("lines");
var totalLines = Object.size(lines);

//Get for alert div
var warning = document.getElementById("warning");
var start = document.getElementById("start");
var stops = document.getElementById("stop");
        // var noface = document.getElementById("danger");
function show (elements, specifiedDisplay) {
    elements = elements.length ? elements : [elements];
    for (var index = 0; index < elements.length; index++) {
        elements[index].style.display = specifiedDisplay || 'block';
    }
}

// Modal when the page start running
var modalToggle = new bootstrap.Modal(document.getElementById('modalstart'), {
                    keyboard: false
                });

//load sfx audio
var audio = new Audio("{% static 'assets/sfx.mp3' %}");
// Returns a Promise that resolves after "ms" Milliseconds
const timer = ms => new Promise(res => setTimeout(res, ms))

// Loop to get command value
i=-1;
$(document).ready(function() {
    modalToggle.show();
$('#btn-start').click(function() {
    show(start);
    modalToggle.hide();
    detector = setInterval(function(){
    $.get("{% url 'blinkcmmd' %}", function(data) { //passing command value if blinking
        var move = data.value;
        if (move==1) {
            i++;
            // alert(i);
        var current = document.getElementsByClassName("lines");
        var before = document.getElementsByClassName("unblur");
                if(i==totalLines){
                    show(warning);
                    clearInterval()
                    i=0;
                }
                if(i<=0){
                    current[0].className = current[0].className.replace("lines blurred", "lines unblur");
                    audio.play();
                }else{
                    current[i].className = current[i].className.replace("lines blurred", "lines unblur");
                    before[0].className = before[0].className.replace(" unblur"," blurred");
                    audio.play();
                    current[i].scrollIntoView({
                        behavior: 'smooth',
                        block: 'center',
                        inline: 'center'
                    });
                };
        } //endof if .get 1
        if (move==2){
        // $("#btn-bck").click(function(){
            // alert(i);
        var current = document.getElementsByClassName("lines");
                if(i<=0){
                    current[0].className = current[0].className.replace("lines unblur", "lines blurred");
                    audio.play();
                }else{
                    current[i].className = current[i].className.replace("lines unblur", "lines blurred");
                    current[i-1].className = current[i-1].className.replace(" blurred"," unblur");
                    audio.play();
                    current[i-1].scrollIntoView({
                        behavior: 'smooth',
                        block: 'center',
                        inline: 'center'
                    });
                }
            i--;
        } //endof if .get 2
        });//endof .get
    },250);//endof intervaltime
}); // endof btn-start

$('#btn-stop').click(function() {
    show(stops);
    clearInterval(detector);
    alert('You use the keyboard for '+presscount+' times!')
});

presscount=0;
//ADDITIONAL FEATURES WITH KEYBOARD KEY CODE
$(document).keydown(function(event) {
    presscount++;
    var key = (event.keyCode ? event.keyCode : event.which);
    if (key == '40'){
    i++;
            // alert(i);
        var current = document.getElementsByClassName("lines");
        var before = document.getElementsByClassName("unblur");
                if(i==totalLines){
                    show(warning);
                    clearInterval()
                    i=0;
                }
                if(i<=0){
                    current[0].className = current[0].className.replace("lines blurred", "lines unblur");
                    audio.play();
                }else{
                    current[i].className = current[i].className.replace("lines blurred", "lines unblur");
                    before[0].className = before[0].className.replace(" unblur"," blurred");
                    audio.play();
                    current[i].scrollIntoView({
                        behavior: 'smooth',
                        block: 'center',
                        inline: 'center'
                    });
                };
    } else if (key == '38'){
        var current = document.getElementsByClassName("lines");
                if(i<=0){
                    current[0].className = current[0].className.replace("lines unblur", "lines blurred");
                    audio.play();
                }else{
                    current[i].className = current[i].className.replace("lines unblur", "lines blurred");
                    current[i-1].className = current[i-1].className.replace(" blurred"," unblur");
                    audio.play();
                    current[i-1].scrollIntoView({
                        behavior: 'smooth',
                        block: 'center',
                        inline: 'center'
                    });
                }
            i--;
    }
});
});//document ready