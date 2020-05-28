import pandas as pd 
import os
import numpy as np 

os.chdir('Customer Export')

# f = "2017 Customer Data - Keegan's Copy.xlsx"

# df = pd.read_excel(f)

# df = df[:522]

# del df['Service Provided']
# del df['Date']
# del df['Start Time']
# del df['End Time']
# del df['Price Info']
# del df['Month']
# del df['Year']
# del df['Duration']
# del df['VLU']
# del df['Referral Source']
# del df["Add'l  Comment"]
# del df['Created by']

# df.fillna("", inplace = True)
# df['Zip Code'] = df['Zip Code'].astype(str)
# df['Address'] = df['Street Address'].map(str) + ' ' + df['City'].map(str) + ' ' + df['State'].map(str) + ' ' + df['Zip Code']

# for _ in df.columns:
#     print(_)

def parse_ods(source_file):
    doc = ezodf.opendoc(source_file)

    sheet = doc.sheets[0]
    df_dict = {}
    for i, row in enumerate(sheet.rows()):
        # row is a list of cells
        # assume the header is on the first row
        if i == 0:
            # columns as lists in a dictionary
            df_dict = {cell.value: [] for cell in row}
            # create index for the column headers
            col_index = {j: cell.value for j, cell in enumerate(row)}
            continue
        for j, cell in enumerate(row):
            # use header instead of column index
            df_dict[col_index[j]].append(cell.value)
    df = pd.DataFrame(df_dict)
    return df


for source_file in os.listdir():

    file_name = source_file.split(".")[0]
    file_ext = source_file[:-4]

    if "ods" in file_ext:
        df = parse_ods(source_file)
    elif 'csv' in file_ext:
        df = pd.read_csv(source_file)
    elif "xls" or "xlsx" in file_ext:
        try:
            df = pd.read_excel(source_file)
        except:
            df = pd.read_html(source_file)
            df = pd.concat(df)

    with open('columns.txt', 'a+') as f:
        f.write(source_file + '\n' + df.colmuns + '\n\n')