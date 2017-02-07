def maketable(title,columns,rows):
    tabletext = '<h4 class="text-left">'+title+'</h4>\n'
    tabletext += '<div>\n<table class="table table-bordered">\n<tbody>\n'

    for row in rows:
        print(['<td>'+data+'</td>' for data in row])
        rowtext='\n'.join(['<td>'+data+'</td>' for data in row])
        tabletext += '<tr>\n\n'+rowtext+'</tr>\n'
    tabletext += '</tbody>\n</table>\n</div>'
    return tabletext
