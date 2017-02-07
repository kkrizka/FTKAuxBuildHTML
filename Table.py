class Table:
    def __init__(self):
        self.rows=[]
        self.columns=[]
        self.title=None

    def process(self, fh):
        lineidx=0
        for line in fh:
            line=line.decode().strip()
            if line[0]=='+': continue
            elif lineidx==0: # title
                self.title=line[1:-1].strip()
            elif lineidx==1: # columns
                self.columns=[title.strip() for title in line[1:-1].split(';')]
            else:
                self.rows.append([title.strip() for title in line[1:-1].split(';')])
            lineidx+=1
