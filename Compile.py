import os, os.path
import sys
import datetime
import tarfile

from Templates import *
from Revision import *


class Compile:

    """Class extracts and stores info for a single compile"""

    def __init__( self , compile_path ):

        self.compile_name = os.path.basename(compile_path)[:-8]
        self.compile_path = compile_path

        info=self.compile_name.split('_')
        self.fpga_name = info[1]
        self.type_name = '_'.join(info[2:-2])
        self.project_name = '%s_%s'%(self.fpga_name,self.type_name)

        self.revisions=[]

        self.date = datetime.datetime( int(self.compile_name[-15:-11]) ,
                                       int(self.compile_name[-11:-9]) ,
                                       int(self.compile_name[-9:-7]) ,
                                       int(self.compile_name[-6:-4]) ,
                                       int(self.compile_name[-4:-2]) ,
                                       int(self.compile_name[-2:]) )

        self.processor_version = "N/A"
        self.auxcommon_version = "N/A"

        self.diff = "N/A"
        self.extra_info = []
        self.fitter_effort = "-"
        self.top_failing_paths_link = ""
        
        self.processor_log = []
        self.auxcommon_log = []

    def formatParagraph( self , li ):
        s = ""
        for l in li:
            if len(l.strip()) == 0:
                s += '<br>\n'
            elif l[0] == ' ':
                s += '<div>&nbsp;&nbsp;'+l.strip()+'</div>\n'
            else:
                s += '<div>'+l.strip()+'</div>\n'
        return s

    def extraInfoString( self ):
        return self.formatParagraph( self.extra_info )

    def processorLogString( self ):
        return self.formatParagraph( self.processor_log )

    def auxcommonLogString( self ):
        return self.formatParagraph( self.auxcommon_log )
    
    def process( self ):
        """ grab info from compile logs """

        fh=tarfile.open(self.compile_path,'r')
        members=fh.getmembers()
        for member in members:
            if not member.isdir() or not member.name.count('/'): continue
            self.revisions.append(Revision(member.name))
            self.revisions[-1].process(fh)

        # Common information
        self.processor_log += [ '<h4 class="text-left">Processor Git Logs</h4>' ]
	try: f = fh.extractfile( self.compile_name+'/processor.log' )
        except(KeyError): f = []

        for line in f:
            line=line.decode().strip()
            if line.startswith('commit '):
                self.processor_log += [ '<hr>'+line ]
            else:
                self.processor_log += [ line ]
            if self.processor_version=='N/A':
                self.processor_version=line.split()[1][:7]

        self.auxcommon_log += [ '<h4 class="text-left">AUXCommon Git Logs</h4>' ]
	try: f = fh.extractfile( self.compile_name+'/auxcommon.log' )
	except(KeyError): f = []

        for line in f:
            line=line.decode().strip()
            if line.startswith('commit '):
                self.auxcommon_log += [ '<hr>'+line ]
            else:
                self.auxcommon_log += [ line ]
            if self.auxcommon_version=='N/A':
                self.auxcommon_version=line.split()[1][:7]

        # Extra info
        self.extra_info += [ "Get files:" ]
        self.extra_info += [ " scp eshop1.uchicago.edu:/net/designs/FTK/Nightlies/"+self.compile_name+".tar.bz2 ." ]
        self.extra_info += [ "" ]

        # if self.n_errors > 0 or not os.path.exists( os.path.join(self.compile_path,'Rx.fit.rpt') ):

        # Dump some of the error messages
	if len(self.revisions):

          if self.revisions[0].analysis.n_errors>0:
              self.extra_info += [ '<h4 class="text-left">Analysis Errors</h4>' ]
              for errorline in self.revisions[0].analysis.errors:
                  self.extra_info += [ errorline+'\n' ]
          if self.revisions[0].fitter.n_errors>0:
              self.extra_info += [ '<h4 class="text-left">Fitter Errors</h4>' ]
              for errorline in self.revisions[0].fitter.errors:
                  self.extra_info += [ errorline+'\n' ]
          if self.revisions[0].assembler.n_errors>0:
              self.extra_info += [ '<h4 class="text-left">Assembler Errors</h4>' ]
              for errorline in self.revisions[0].assembler.errors:
                  self.extra_info += [ errorline+'\n' ]
          if self.revisions[0].timing.n_errors>0:
              self.extra_info += [ '<h4 class="text-left">Timing Errors</h4>' ]
              for errorline in self.revisions[0].timing.errors:
                  self.extra_info += [ errorline+'\n' ]
              
          # Table of resource usage
          if self.revisions[0].resourceusage!=None:
              self.extra_info += [ self.revisions[0].resourceusage.html_rows([0,46,51]) ]

        else:

	  self.extra_info += [ '<h4 class="text-left">Warning: no revisions found.</h4>' ]
