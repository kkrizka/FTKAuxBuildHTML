/*
 * For a simple upward counter
 */

function upCounter( startTime , elementId )
{
    var currentTime = new Date();
    var deltaT	    = currentTime.getTime() - startTime.getTime();

    deltaT = Math.floor( deltaT / 1000 ); // converted to seconds
    var h  = Math.floor( deltaT / (60 * 60) );
    deltaT -= (h * 60 * 60);
    var m  = Math.floor( deltaT / (60) );
    deltaT -= (m * 60);
    var s  = deltaT;

    h = checkTime( h );
    m = checkTime( m );
    s = checkTime( s );
    document.getElementById(elementId).innerHTML = h+":"+m+":"+s;

    var t = setTimeout( function() { upCounter(startTime,elementId) } , 500 );
}

function checkTime( i )
{
    if( i < 10 ) { i = "0" + i };  // add zero in front of numbers < 10
    return i;
}
