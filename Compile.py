import os, os.path
import sys
import time
import datetime
import tarfile

from Templates import *
from Revision import *

import htmltools

import heplovespy26

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

        self.firmware_version  = "N/A"
        self.auxcommon_version = "N/A"

        self.extra_info = []
        
        self.firmware_log  = []
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

    def firmwareLogString( self ):
        return self.formatParagraph( self.firmware_log )

    def auxcommonLogString( self ):
        return self.formatParagraph( self.auxcommon_log )

    def process(self, db):
        """ process info from a database if an entry exists, otherwise from a file """
        cursor=db.cursor()

        # Check if project exists
        cursor.execute('SELECT * FROM projects WHERE name="%s"'%self.project_name)
        result=cursor.fetchone()
        project_id=None
        if result==None: # Create
            cursor.execute('INSERT INTO projects (name) VALUES ("%s")'%self.project_name)
            db.commit()
            project_id=cursor.lastrowid
        else:
            project_id=result[0]

        # Check if compile exists
        cursor.execute('SELECT * FROM compiles WHERE project_id=%d'%project_id)
        result=cursor.fetchone()
        compile_id=None
        if result==None:
            print('Load from file.')
            self.process_file()

            cursor.execute('INSERT INTO compiles (project_id,datetime,firmware_version,auxcommon_version,firmware_log,auxcommon_log) VALUES (%d,%d,"%s","%s",?,?)'%(project_id,time.mktime(self.date.timetuple()),self.firmware_version,self.auxcommon_version),('\n'.join(self.firmware_log),'\n'.join(self.auxcommon_log)))
            db.commit()
            compile_id=cursor.lastrowid

            for revision in self.revisions:
                cursor.execute('INSERT INTO revisions (compile_id,rev_path,compile_time,version,n_info,n_warnings,n_errors,n_other,ru_logicutil,ru_logicutil_total,ru_dspblocks,ru_dspblocks_total,ru_perphclocks,ru_perphclocks_total) VALUES (%d,"%s",%d,"%s",%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)'%(compile_id,revision.revpath,heplovespy26.total_seconds(revision.compile_time),revision.version,revision.n_info,revision.n_warnings,revision.n_errors,revision.n_other,revision.ru_logicutil,revision.ru_logicutil_total,revision.ru_dspblocks,revision.ru_dspblocks_total,revision.ru_perphclocks,revision.ru_perphclocks_total))
                db.commit()
                revision_id=cursor.lastrowid

                if revision.assignments.exists:
                    cursor.execute('INSERT INTO processinfo (revision_id,process,time,n_info,n_warnings,n_errors,n_other,errors) VALUES (%d,"%s",%d,%d,%d,%d,%d,?)'%(revision_id,"assignments" ,heplovespy26.total_seconds(revision.assignments.time),revision.assignments.n_info,revision.assignments.n_warnings,revision.assignments.n_errors,revision.assignments.n_other),('\n'.join(revision.assignments.errors),))
                if revision.analysis.exists:
                    cursor.execute('INSERT INTO processinfo (revision_id,process,time,n_info,n_warnings,n_errors,n_other,errors) VALUES (%d,"%s",%d,%d,%d,%d,%d,?)'%(revision_id,"analysis"   ,heplovespy26.total_seconds(revision.analysis.time),revision.analysis.n_info,revision.analysis.n_warnings,revision.analysis.n_errors,revision.analysis.n_other),('\n'.join(revision.analysis.errors),))
                if revision.fitter.exists:
                    cursor.execute('INSERT INTO processinfo (revision_id,process,time,n_info,n_warnings,n_errors,n_other,errors) VALUES (%d,"%s",%d,%d,%d,%d,%d,?)'%(revision_id,"fitter"     ,heplovespy26.total_seconds(revision.fitter.time),revision.fitter.n_info,revision.fitter.n_warnings,revision.fitter.n_errors,revision.fitter.n_other),('\n'.join(revision.fitter.errors),))
                if revision.assembler.exists:
                    cursor.execute('INSERT INTO processinfo (revision_id,process,time,n_info,n_warnings,n_errors,n_other,errors) VALUES (%d,"%s",%d,%d,%d,%d,%d,?)'%(revision_id,"assembler"  ,heplovespy26.total_seconds(revision.assembler.time),revision.assembler.n_info,revision.assembler.n_warnings,revision.assembler.n_errors,revision.assembler.n_other),('\n'.join(revision.assembler.errors),))
                if revision.timing.exists:
                    cursor.execute('INSERT INTO processinfo (revision_id,process,time,n_info,n_warnings,n_errors,n_other,errors) VALUES (%d,"%s",%d,%d,%d,%d,%d,?)'%(revision_id,"timing"     ,heplovespy26.total_seconds(revision.timing.time),revision.timing.n_info,revision.timing.n_warnings,revision.timing.n_errors,revision.timing.n_other),('\n'.join(revision.timing.errors),))

                for clock in revision.fmax_fit:
                    cursor.execute('INSERT INTO clocks (revision_id,clock,fmax_target,fmax) VALUES (%d,"%s",%f,%f)'%(revision_id,clock,revision.fmax_gen[clock],revision.fmax_fit[clock]))

                db.commit()
        else:
            compile_id=result[0]

            self.firmware_version =result[3]
            self.auxcommon_version=result[4]

            self.firmware_log =result[5].split('\n')
            self.auxcommon_log=result[6].split('\n')

            result=cursor.execute('SELECT * FROM revisions WHERE compile_id=%d'%compile_id)
            for row in result:
                rev=Revision(row[2])
                rev.compile_time=datetime.timedelta(seconds=row[3])
                rev.version=row[4]
                rev.n_info=row[5]
                rev.n_warnings=row[6]
                rev.n_errors=row[7]
                rev.n_other=row[8]

                rev.ru_logicutil=row[9]
                rev.ru_logicutil_total=row[10]
                rev.ru_dspblocks=row[11]
                rev.ru_dspblocks_total=row[12]
                rev.ru_perphclocks=row[13]
                rev.ru_perphclocks_total=row[14]

                result=cursor.execute('SELECT * FROM clocks WHERE revision_id=%d'%row[0])
                for row in result:
                    rev.fmax_gen[row[2]]=row[3]
                    rev.fmax_fit[row[2]]=row[4]

                result=cursor.execute('SELECT * FROM processinfo WHERE revision_id=%d'%row[0])
                for row in result:
                    process=row[2]
                    getattr(rev,process).exists=True
                    getattr(rev,process).failed=row[6]>0                    
                    getattr(rev,process).time=datetime.timedelta(seconds=row[3])
                    getattr(rev,process).n_info=row[4]
                    getattr(rev,process).n_warnings=row[5]
                    getattr(rev,process).n_errors=row[6]
                    getattr(rev,process).n_other=row[7]
                    getattr(rev,process).errors=row[8].split('\n')

                self.revisions.append(rev)

        self.build_extra_info()
                
    
    def process_file( self ):
        """ grab info from compile logs """

        fh=tarfile.open(self.compile_path,'r')
        members=fh.getmembers()
        for member in members:
            if not member.isdir() or not member.name.count('/'): continue
            self.revisions.append(Revision(member.name))
            self.revisions[-1].process(fh)

        # Common information
        self.firmware_log += [ '<h4 class="text-left">Firmware Git Logs</h4>' ]
        try: f = fh.extractfile( self.compile_name+'/processor.log' )
        except(KeyError): f = []

        for line in f:
            line=line.decode().strip()
            if line.startswith('commit '):
                self.firmware_log += [ '<hr>'+line ]
            else:
                self.firmware_log += [ line ]
            if self.firmware_version=='N/A':
                self.firmware_version=line.split()[1][:7]

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

    def build_extra_info(self):
        """ Build the extra_info (HTML) structure from properties """

        # Extra info
        self.extra_info += [ "Get files:" ]
        self.extra_info += [ " scp eshop1.uchicago.edu:/net/designs/FTK/Nightlies/"+self.compile_name+".tar.bz2 ." ]
        self.extra_info += [ "" ]
        
        if len(self.revisions):
            if not self.revisions[0].fitter.failed:
                # Table of resource usage
                self.extra_info += [ htmltools.maketable('Fitter Resource Usage Summary',None,[['Logic utilization (ALMs needed / total ALMs on device)','%d / %d'%(self.revisions[0].ru_logicutil,self.revisions[0].ru_logicutil_total),'%0.0f%%'%(self.revisions[0].ru_logicutil/self.revisions[0].ru_logicutil_total*100)],
                                                                                               ['Total DSP Blocks','%d / %d'%(self.revisions[0].ru_dspblocks,self.revisions[0].ru_dspblocks_total),'%0.0f%%'%(self.revisions[0].ru_dspblocks/self.revisions[0].ru_dspblocks_total*100)],
                                                                                               ['Horizontal periphery clocks and Vertical periphery clocks','%d / %d'%(self.revisions[0].ru_perphclocks,self.revisions[0].ru_perphclocks_total),'%0.0f%%'%(self.revisions[0].ru_perphclocks/self.revisions[0].ru_perphclocks_total*100)]]) ]

            # Error messages
            if self.revisions[0].assignments.exists and self.revisions[0].assignments.failed:
                self.extra_info += [ '<h4 class="text-left">Assignments Errors</h4>' ]
                for errorline in self.revisions[0].assignments.errors:
                    self.extra_info += [ errorline+'\n' ]            
            if self.revisions[0].analysis.exists and self.revisions[0].analysis.failed:
                self.extra_info += [ '<h4 class="text-left">Analysis Errors</h4>' ]
                for errorline in self.revisions[0].analysis.errors:
                    self.extra_info += [ errorline+'\n' ]
            if self.revisions[0].fitter.exists and self.revisions[0].fitter.failed:
                self.extra_info += [ '<h4 class="text-left">Fitter Errors</h4>' ]
                for errorline in self.revisions[0].fitter.errors:
                    self.extra_info += [ errorline+'\n' ]
            if self.revisions[0].assembler.exists and self.revisions[0].assembler.failed:
                self.extra_info += [ '<h4 class="text-left">Assembler Errors</h4>' ]
                for errorline in self.revisions[0].assembler.errors:
                    self.extra_info += [ errorline+'\n' ]
            if self.revisions[0].timing.exists and self.revisions[0].timing.failed:
                self.extra_info += [ '<h4 class="text-left">Timing Errors</h4>' ]
                for errorline in self.revisions[0].timing.errors:
                    self.extra_info += [ errorline+'\n' ]

        else:
            self.extra_info += [ '<h4 class="text-left">Warning: no revisions found.</h4>' ]

            
