import os, os.path
import sys
import datetime


class RunTimer:

    """Class determines the start time of a compile currently running"""

    def __init__( self , path ):

        self.path = path

        self.tag = os.path.basename(path).replace('.null','')

        self.project_name = self.tag[17:-16]
        
        self.start_time = datetime.datetime( int(self.tag[-15:-11]) ,
                                             int(self.tag[-11:-9]) ,
                                             int(self.tag[-9:-7]) ,
                                             int(self.tag[-6:-4]) ,
                                             int(self.tag[-4:-2]) ,
                                             int(self.tag[-2:]) )

        self.java_tag = 'new Date(%i,%i,%i,%i,%i,%i)' % (self.start_time.year,
                                                         self.start_time.month-1,
                                                         self.start_time.day,
                                                         self.start_time.hour,
                                                         self.start_time.minute,
                                                         self.start_time.second)


        
