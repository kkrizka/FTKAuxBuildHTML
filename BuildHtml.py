#!/usr/bin/env python 


import sys
import os
import datetime
import glob

from Compile import *
from Templates import *
from RunTimer import *


""" Grab info for all of the compiles and then generate an html summary """

# List of directories containing compiles
compileDirs = ['/home/kkrizka/tmp/fw'] #[ '/net/designs/FTK/Nightlies/' ]
# 'd:/Projects/ftk/Nightlies/BuildHtml' ]

#
# First grab all the compile information
#

compiles  = [ Compile(result)  for compileDir in compileDirs for result in glob.glob('%s/compile_*2016[0-9]*.tar.bz2'%(compileDir)) ]
runtimers = [ RunTimer(result) for compileDir in compileDirs for result in glob.glob('%s/compileStartTime_*.null'%(compileDir)) ]

for c in compiles: c.process()

#
# split up the compiles based on project name and sort by date
#

projects = list( set( [ x.project_name for x in compiles ] ) )
projects.sort()

compile_dict  = {}
runtimer_dict = {}
for p in projects:
    compile_dict[p]  = [ x for x in compiles  if x.project_name == p ]
    runtimer_dict[p] = [ x for x in runtimers if x.project_name == p ]
    compile_dict[p].sort( key=lambda x: x.compile_name, reverse=True )


#
# Open the output file
#
f = open( "nightlies.html" , 'w' )

writeLines( f , PageHeader )

# In the <body> line we need to load all of the compile timers
runTimerLoadString = ''
for p in projects:
    if len(runtimer_dict[p]) > 0:
        runtimer = runtimer_dict[p][0]
        runTimerLoadString += 'upCounter( '+runtimer.java_tag+' , \'timer_'+p+'\'); '

writeLines( f , [ '<body onload="'+runTimerLoadString+'">' ] )

writeLines( f , TitleHeader )
writeLines( f , [ '<li class="active"><a href="index.html">Home</a></li>' ] )
writeLines( f , [ '<li class="activesmall"><a href="#'+x+'">'+x+'</a></li>' for x in projects ] )
writeLines( f , TitleTrailer )

writeLines( f , [ '<br>' ,
                  '<p>Html last updated '+str(datetime.datetime.now())+'</p>' ] )

for p in projects:

    writeLines( f , [ '<br><br>' ,
                      '<div class="col-md-10 col-md-offset-1">' ,
                      '<h1 class="text-left">'+p+'</h1>' ,
                      '<section id="'+p+'"></section>' ] )
                      #'<div class="col-md-12 img-timing"><img src="nightlies_'+p+'_fmax.png"></div>' ] )

    # Check if there is a compile currently running
    if len(runtimer_dict[p]) > 0:
        runtimer = runtimer_dict[p][0]
        writeLines( f , [ '<table class="table table-redheader">' ,
                          '<thead>' ,
                          '<tr>' ,
                          '<th>Compile Running &nbsp <div style="display:inline" id="timer_'+p+'"></div></th>' ,
                          '</tr>' ,
                          '</thead>' ,
                          '</table>' ] )

    writeLines( f , [ '<table class="table table-striped" style="border-collapse:collapse;">' ,
                      '<thead>' ,
                      '<tr>' ,
                      '<th>Date</th>' ,
                      '<th>Duration</th>' ,
                      '<th>Processor</th>' ,
                      '<th>AUXCommon</th>' ,
                      '<th>Version</th>' ,
                      '<th>nInfo</th>' ,
                      '<th>nWarnings</th>' ,
                      '<th>nErrors</th>' ,
                      '<th><a href="javascript::void(0)" data-toggle="tooltip" data-placement="bottom" title="Esimation for outclk_wire[0] from Slow 1100mV 85C Model">fMax[0]</a></th>' ,
                      '<th><a href="javascript::void(0)" data-toggle="tooltip" data-placement="bottom" title="Esimation for outclk_wire[1] from Slow 1100mV 85C Model">fMax[1]</a></th>' ,
                      '<th>Revision</th>' ,
                      '</tr>' ,
                      '</thead>' ,
                      '<tbody>' ] )

    # lists to keep track of compile speeds
    list_fmax0 = []
    list_fmax1 = []
    list_dates = []
    
    for c in compile_dict[p]:

        print("processing:",c.compile_name,"...")

	if not len(c.revisions):

          writeLines( f , [ '<tr>' ,
                            '<td>'+str(c.date)+'</td>', '<td> <font color="red">FAILED</font> </td>' ,
                            '<td></td>', '<td></td>', '<td></td>', '<td></td>', '<td></td>',
                            '<td></td>', '<td></td>', '<td></td>', '<td></td>', '</tr>' ] )

	else:

          #list_dates += [ dates.date2num( c.compile_start_time ) ]
          list_fmax0 += [ c.revisions[0].numeric_fMax('outclk_wire[0]') ]
          list_fmax1 += [ c.revisions[0].numeric_fMax('outclk_wire[1]') ]

          writeLines( f , [ '<tr data-toggle="collapse" data-target="#'+c.compile_name+'" class="accordion-toggle">' ,
                            '<td>'+str(c.date)+'</td>' ,
                            '<td>'+str(c.revisions[0].compile_time)+'</td>' ,
                            '<td>'+c.processor_version+'</td>' ,
                            '<td>'+c.auxcommon_version+'</td>' ,
                            '<td>'+c.revisions[0].version+'</td>' ,
                            '<td>'+str(c.revisions[0].n_info)+'</td>' ,
                            '<td>'+str(c.revisions[0].n_warnings)+'</td>' ,
                            c.revisions[0].markup_nError() ,
                            c.revisions[0].markup_fMax('outclk_wire[0]') ,
                            c.revisions[0].markup_fMax('outclk_wire[1]') ,
                            '<td>'+c.revisions[0].rev_name+'</td>' ,
                            '</tr>' ,
                            '<tr>' ,
                            '<td colspan="11" class="hiddenRow">' ,
                            '<div class="accordian-body collapse" id="'+c.compile_name+'">' ,
                            '<div class="container">' ,
                            c.extraInfoString() ,
                            '<br>' ,
                            '<div class="row">' ,
                            '<div class="col-md-6">' ,
                            c.processorLogString() ,
                            '</div>' ,
                            '<div class="col-md-6">' ,
                            c.auxcommonLogString() ,
                            '</div>' ,
                            '</div>' ,
                            '<br>' ,
                            '</div>' ,
                            '</div>' ,
                            '</td>' ,
                            '</tr>' ] )
                            

    writeLines( f , [ '</tbody>' ,
                      '</table>' ,
                      '</div>' ] )


    #
    #  Create plots of timing
    #

    #save_timing_plot( list_dates , list_fmax0 , list_fmax1 , p )

    


writeLines( f , PageTrailer )
f.close()

#os.system( 'scp -r nightlies.html jsaxon@hep.uchicago.edu:/local/web/hep/atlas/ftk/nightlies/')

print("done.")
