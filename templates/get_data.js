i=-1;
        $(document).ready(function() {
        console.log("{{value}}")
        $('#btn-start').click(function() {
            show(start);
            detector = setInterval(function(){
            $.get("{% url 'blinkcmmd' %}", function(data) { //passing command value if blinking
                var move = data.value;
                if (move==1){
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
                        }else{
                            current[i].className = current[i].className.replace("lines blurred", "lines unblur");
                            before[0].className = before[0].className.replace(" unblur"," blurred");
                            current[i].scrollIntoView({
                                behavior: 'smooth',
                                block: 'center',
                                inline: 'center'
                            });
                        }
                } //endof if .get 1
                if (move==2){
                // $("#btn-bck").click(function(){
                    // alert(i);
                var current = document.getElementsByClassName("lines");
                        if(i<=0){
                            current[0].className = current[0].className.replace("lines unblur", "lines blurred");
                        }else{
                            current[i].className = current[i].className.replace("lines unblur", "lines blurred");
                            current[i-1].className = current[i-1].className.replace(" blurred"," unblur");
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
        });

        });//document ready