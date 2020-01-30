import re
import os
import subprocess
import pandas as pd


def parse_bank_statement(filename):
    if filename.endswith('.pdf'):
        subprocess.call(['pdftotext', '-layout', filename])
        os.remove(filename)
    else:
        print('ERROR: not a pdf file')
        return

    with open(filename.strip('.pdf')+'.txt') as file:
        data = file.readlines()

    regex_date = "(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{2},\s\d{4}"
    regex_date_match = re.compile(regex_date + ' through ' + regex_date)
    if regex_date_match.match(data[0].strip()):
        year = re.findall('\d{4}', data[0].strip())
        year_end = True if len(set(year))>1 else False
    else:
        print('ERROR: date not found')
        return

    regex_debit_match = re.compile("[ \t]*([0-9]{2}/[0-9]{2})[ \t]*([\\w \\/\\.\\#\\:\\-\\*]+ )([0-9\\-\\,]+\\.[0-9]{2}) +")

    parsed = []
    for line in data:
        if regex_debit_match.match(line) is not None:
            parsed.append(regex_debit_match.split(line.strip())[1:])
    names = ['Date', 'Desc', 'Amount', 'Balance']
    df = pd.DataFrame(parsed, columns=names)

    def add_year_to_column(x):
        if year_end and x[0]=='0':
            return "{}/{}".format(year[1],x)
        return "{}/{}".format(year[0],x)
    
    df['Date'] = pd.to_datetime(df['Date'].apply(add_year_to_column), format='%Y/%m/%d').dt.date
    df['Desc'] = df['Desc'].apply(lambda x: x.strip('Card Purchase').strip())
    df['Amount'] = df['Amount'].apply(lambda x: float(x.replace(',', '')))
    df['Balance'] = df['Balance'].apply(lambda x: float(x.replace(',', '')))
    return df


def read_categorized_statement(filename):
    names = ['Date', 'Desc', 'Amount', 'Balance', 'Category']
    df = pd.read_csv(filename, names=names)
    df['Amount'] = df['Amount'].apply(lambda x: float(x.replace(',', '')))
    return df


def save_categorized_statement(df, filename):
    df.to_csv(filename)
