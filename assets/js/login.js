
/*
function passWord() {
    var testV = 1;
    var pass1 = prompt('Please Enter Your Password',' ');
    while (testV < 3) {
        if (!pass1)
            history.go(-1);
        if (pass1.toLowerCase() == "letmein") {
            alert('You Got it Right!');
            window.open('protectpage.html');
            break;
        }
        testV+=1;
        var pass1 =
            prompt('Access Denied - Password Incorrect, Please Try Again.','Password');
    }
    if (pass1.toLowerCase()!="password" & testV ==3)
        history.go(-1);
    return " ";
}
*/

/*
function Login(form) {

    var username = form.username.value;
    var password = form.password.value;
    var server   = "protected";

    if( username == "raptor" && password = "Kl2abinMvB" ) {
        location.href = "protected";
    } else {
        // do nothing?
    }

}
*/

function Login(form) {
    var username = form.username.value;
    var password = form.password.value;
    var server = form.server.value;
    if (username && password && server) {
	var htsite = "http://" + username + ":" + password + "@" + server;
	window.location = htsite;
    } /*else {
	alert( "wrong" );
    }
    */
}


    /*

function Login(form) {

    var username = form.username.value;
    var password = form.password.value;
    var server   = "protected";

    if( username == "test" && password = "test" ) {
        location.href = "protected";
    } else {
        // do nothing?
    }

}
*/


