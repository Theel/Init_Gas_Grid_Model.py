import csv
from pathlib import Path
import os

def table_converter(filename, directory="files"):
    rows = []

    with open(directory+ "/" +filename+ ".csv", 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for line in csvreader:
            rows.append(line)
    dym_filename = fr'{str(Path.cwd())}\files\{filename}_dym.txt'
    f = open("files" + "/" + filename + "_dym.txt", 'w')

    f.write(f'#1\n'
            f'double {filename}({len(rows)-1},{len(rows[0])})\n')  # ampassen an Tabellen
    c = 1

    for i in range(1, len(rows)):                                   # ampassen an Tabellen
        for j in range(len(rows[i])):
            if c % 2 == 0:
                f.write(f'{rows[i][j]}')
            else:
                f.write(f'{rows[i][j]},')
            c += 1
        f.write(f'\n')
    f.close()
    return(dym_filename.replace('\\','/'))
