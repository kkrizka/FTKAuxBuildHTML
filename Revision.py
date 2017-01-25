import os, os.path
import sys
import re
import datetime
import tarfile

from Templates import *
from Table import *

class ProcessInfo:
    def __init__(self):
        self.n_info = -1
        self.n_warnings = -1 
        self.n_errors = -1
        self.n_other = -1

        self.errors = []

        self.time = datetime.timedelta(0)

    def process(self, fhlog):
        self.n_info = 0
        self.n_warnings = 0
        self.n_errors = 0
        self.n_other = 0

        re_elapsed=re.compile('Elapsed time: ([0-9]+):([0-9]+):([0-9]+)')
        for line in fhlog:
            line=line.decode().strip()

            if line.startswith('Info'): self.n_info+=1
            elif line.startswith('Warning'): self.n_warnings+=1
            elif line.startswith('Error'):
                self.n_errors+=1
                self.errors.append(line)
            else: self.n_other+=1

            match=re_elapsed.search(line)
            if match!=None:
                self.time=datetime.timedelta(hours=int(match.group(1)),minutes=int(match.group(2)),seconds=int(match.group(3)))
        

class Revision:

    """Class extracts and stores info for a single compile"""

    def __init__( self , revpath ):

        self.revpath=revpath

        parts0=revpath.split('/')        
        self.rev_name  = parts0[1]
        
        self.analysis = ProcessInfo()
        self.fitter = ProcessInfo()
        self.assembler = ProcessInfo()
        self.timing = ProcessInfo()
        self.compile_time = None

        self.version = "N/A"

        self.n_info = -1
        self.n_warnings = -1 
        self.n_errors = -1
        self.n_other = -1

        self.fmax_fit = { 'outclk_wire[0]' : '-' , 'outclk_wire[1]' : '-' , 'outclk_wire[2]' : '-' }
        self.fmax_gen = { 'outclk_wire[0]' : '-' , 'outclk_wire[1]' : '-' , 'outclk_wire[2]' : '-' }

        self.resourceusage=None
        
        self.extra_info = []
        
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

    def markup_nError( self ):
        if self.n_errors > 0:
            return '<td class="text-error">'+str(self.n_errors)+'</td>'
        else:
            return '<td class="text-success">'+str(self.n_errors)+'</td>'

    def numeric_fMax( self , k ):
        if self.fmax_gen[k] == '-' or self.fmax_fit[k] == '-':
            return [ 0. , 0. ]
        else:
            return [ self.fmax_fit[k], self.fmax_gen[k] ]

    def markup_fMax( self , k ):
        if self.fmax_gen[k] == '-' or self.fmax_fit[k] == '-':
            return '<td>-</td>'
        cl = 'text-success'
        if self.fmax_gen[k] > self.fmax_fit[k]:
            cl = 'text-error'
        return '<td class="%s">%0.1f/%0.1f</td>'%(cl,self.fmax_fit[k],self.fmax_gen[k])

    def extraInfoString( self ):
        return self.formatParagraph( self.extra_info )

    def processorLogString( self ):
        return self.formatParagraph( self.processor_log )

    def auxcommonLogString( self ):
        return self.formatParagraph( self.auxcommon_log )
    
    def process( self , fh ):
        """ grab info from compile logs """

        # Time information
        try:
            self.analysis.process(fh.extractfile(self.revpath+'/AnalysisLog.txt'))
            self.fitter.process(fh.extractfile(self.revpath+'/FitterLog.txt'))
            self.assembler.process(fh.extractfile(self.revpath+'/AssemblerLog.txt'))            
            self.timing.process(fh.extractfile(self.revpath+'/TimingLog.txt'))
        except KeyError:
            pass

        self.compile_time=self.analysis.time+self.fitter.time+self.assembler.time+self.timing.time

        self.n_info=self.analysis.n_info+self.fitter.n_info+self.assembler.n_info+self.timing.n_info
        self.n_warnings=self.analysis.n_warnings+self.fitter.n_warnings+self.assembler.n_warnings+self.timing.n_warnings
        self.n_errors=self.analysis.n_errors+self.fitter.n_errors+self.assembler.n_errors+self.timing.n_errors
        self.n_other=self.analysis.n_other+self.fitter.n_other+self.assembler.n_other+self.timing.n_other

        # Version information
        try:
            f = fh.extractfile(self.revpath+'/version.txt')
        except KeyError:
            pass
        else:
            self.version = f.readline().decode().strip() + f.readline().decode().strip()

        # fMax information
        try:
            f = fh.extractfile(self.revpath+'/fMax_Summary_post-fit.txt')
        except KeyError:
            pass
        else:
            modelidx=0
            for line in f:
                line=line.decode().strip()
                if line=='': continue
                parts=line.split()
                if len(parts)==1:
                    modelidx+=1
                    if modelidx==2: break
                    continue
                if len(parts)!=4: continue            
                fMax=float(parts[1])
                freq=float(parts[3])
                parts=parts[0].split('|')
                name=parts[-1]
                self.fmax_fit[name]=fMax
                self.fmax_gen[name]=freq

        # usage information
        try:
            f = fh.extractfile(self.revpath+'/ResourceUsageSummary.txt')
        except KeyError:
            pass
        else:
            self.resourceusage=Table()
            self.resourceusage.process(f)
