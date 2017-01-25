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

    def html_rows(self, rows):
        tabletext = '<h4 class="text-left">'+self.title+'</h4>\n'
        tabletext += '<div>\n<table class="table table-bordered">\n<tbody>\n'

        for row in rows:
            rowtext='\n'.join(['<td>'+data+'</td>' for data in self.rows[row]])
            tabletext += '<tr>\n\n'+rowtext+'</tr>\n'
        tabletext += '</tbody>\n</table>\n</div>'
        
        return tabletext
