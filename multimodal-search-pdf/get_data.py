import csv
import os

import weasyprint

blog_file = 'toy_data/blog-pdf.csv'

try:
    os.makedirs('data')
except:
    pass

with open(blog_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        if row[0] == 'Name':
            continue
        name = 'data/' + row[0] + '.pdf'
        url = row[1]
        pdf = weasyprint.HTML(url).write_pdf()
        with open(name, 'wb') as outputStream:
            outputStream.write(pdf)
