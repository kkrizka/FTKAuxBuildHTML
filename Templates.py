#import matplotlib.pyplot as plt
#import matplotlib.dates as dates
import os

def writeLines( f , li ):
    for line in li:
        f.write( "%s\n" % line )

PageHeader = [ '<!DOCTYPE html>' ,
               '<html lang="en">' ,
               '<head>' ,
               '<meta charset="utf-8">' ,
               '<meta http-equiv="X-UA-Compatible" content="IE=edge">' ,
               '<meta http-equiv="refresh" content="300">' ,
               '<meta name="viewport" content="width=device-width, initial-scale=1.0">' ,
               '<meta name="description" content="">' ,
               '<meta name="author" content="">' ,
               '<title>AUX Nightlies</title>' ,
               '<link href="assets/css/bootstrap.css" rel="stylesheet">' ,
               '<link href="assets/css/main.css" rel="stylesheet">' ,
               '<link href="assets/css/font-awesome.min.css" rel="stylesheet">' ,
               '</head>' ]


TitleHeader = [ '<div class="navbar navbar-default navbar-fixed-top">' ,
                '<div class="container">' ,
                '<div class="navbar-header">' ,
                '</div>' ,
                '<div class="navbar-collapse collapse">' ,
                '<ul class="nav navbar-nav navbar-right">' ]

TitleTrailer = [ '</ul>' ,
                 '</div>' ,
                 '</div>' ,
                 '</div>' ]

PageTrailer = [ '</body>' ,
                '<script src="https://code.jquery.com/jquery-2.1.3.min.js"></script>' ,
                '<script src="assets/js/bootstrap.js"></script>' ,
                '<script src="assets/js/main.js"></script>' ,
                '<script src="assets/js/countup.js"></script>' ,
                '</html>' ]

# Functions for executing bash commands in windows
def bunzip2( path ):
    # os.system( '\"\"C:\\Program Files (x86)\\Git\\bin\\bzip2\" -d '+path+'\"' )
    os.system("bzip2 -d " + path )

def bzip2( path ):
    # os.system( '\"\"C:\\Program Files (x86)\\Git\\bin\\bzip2\" -c '+path+'\"' )
    os.system("bzip2 -c " + path )

#def save_timing_plot( xdates , yfmax0 , yfmax1 , projectname ):
#
#    f , axarr = plt.subplots( 2 , sharex=True )
#
#    axarr[0].plot_date( xdates , [y[0] for y in yfmax1] , 'b-' )
#    axarr[0].plot_date( xdates , [y[1] for y in yfmax1] , 'r--' )
#    axarr[1].plot_date( xdates , [y[0] for y in yfmax0] , 'b-' )
#    axarr[1].plot_date( xdates , [y[1] for y in yfmax0] , 'r--' )
#
#    axarr[1].xaxis.set_major_locator( dates.DayLocator() )
#    axarr[1].xaxis.set_major_formatter( dates.DateFormatter('%Y-%m-%d') )
#    axarr[1].xaxis.set_minor_locator( dates.DayLocator() )
#    axarr[1].set_xlabel( 'Compile Start Time' )
#    
#    axarr[0].autoscale_view()
#    axarr[1].autoscale_view()
#    axarr[0].grid( True )
#    axarr[1].grid( True )
#
#    axarr[0].set_ylabel( 'fMax[1] [MHz]' )
#    axarr[1].set_ylabel( 'fMax[0] [MHz]' )
#    axarr[0].set_ylim( bottom=0 , top=250 )
#    axarr[1].set_ylim( bottom=0 , top=250 )
#
#    f.set_size_inches( 11.0 , 4.0 )
#    f.autofmt_xdate()
#
#    plt.tight_layout()
#    plt.savefig( 'nightlies_'+projectname+'_fmax.png' , facecolor='#f2f2f2' , transparent=False )
