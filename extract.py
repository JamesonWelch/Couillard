import pandas as pd 
import os
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
stop = stopwords.words('english')



ROOT_DIR = os.getcwd()
FINAL_FILE = os.path.join(ROOT_DIR, 'out', 'Customer Contact List v_11.csv')
FINAL_DF = pd.read_csv(FINAL_FILE)

print(FINAL_DF.shape)

FOR_LIST = []

with open('for_loop.txt', 'r') as f:
    for line in f:
        FOR_LIST.append(line.strip())



name_list = []
with open('NAMES.DIC', 'r') as f:
    for _ in f:
        name_list.append(_.strip())
os.chdir('Customer Data CLEANED CSV/subset')




def main():

    files = os.listdir()

    global_df = pd.DataFrame(columns=['First Name', 'Last Name', 'Email', 'Phone Number(s)', 'Address', 'Raw Data'])
    print(f'### global_df.shape: {global_df.shape}')
    for _ in range(len(files)):
        
        try:
            print(f'OPENING: {files[_]}')
            df = pd.read_csv('4-9 MASTER.csv')


            # df.fillna("  ", inplace = True)    
        


            # # df['Zip Code'] = df['Zip Code'].astype(str).replace('\.0', '', regex=True)

            # # df.rename(columns={"Where": "Address"}, inplace=True)

            # # df['Phone Number(s)'] = df['Mobile Number'].map(str) + " | " + df['Home Number'].map(str)


            # df['Phone Number(s)'] =  df.apply(lambda df: extract_phone_numbers(df['Description']), axis=1)
            # df['Phone Number(s)'] = df['Phone Number(s)'].apply(', '.join)
            # df['Email'] = df['Description'].apply(lambda x: extract_email_addresses(x))
            # # df['Email'] = df.Emails.apply(', '.join)
            # df.loc[:,'Email'] = df.loc[:,'Email'].astype(str)
            # df.rename(columns={"Where": "Address"}, inplace=True)
            # df.loc[:,'Email'] = df.loc[:,'Email'].apply(lambda x: literal_eval(x))
            # df['Email'] = df['Email'].str.get(0)
            # df.fillna("  ", inplace = True)  
            # # df['Name'] = df.apply(lambda df: extract_names(df['Description'], df['Addr"ess']), axis=1)
            # df['Title'] = df['Title'].apply(lambda x: x.strip(' - '))
            # df['Title'] = df['Title'].apply(lambda x: x.strip('windows'))
            # df['Title'] = df['Title'].apply(lambda x: x.strip('Windows'))
            # df['Title'] = df['Title'].apply(lambda x: x.strip('Clean'))
            # df['Title'] = df['Title'].apply(lambda x: x.strip('clean'))
            # df['Title'] = df['Title'].apply(lambda x: x.strip('wash'))
            # # df['Notes'] = df['Notes'].apply(lambda df: df.replace('<br>', '\n'))

            # df['Full Name'] = df['Title'].apply(lambda df: easy_name(df))
            # df['Last Name'] = df['Full Name'].apply(lambda df: last_name(df))
            # df['First Name'] = df['Full Name'].apply(lambda x: first_name(x))
            # df['extd Names'] = df['Description'].apply(lambda x: extract_names(x))

            # df['Raw Data'] =  df['Title'].map(str) + " | " + df['Description'].map(str)

            # # df['Name'] = df.Name.apply(', '.join)
            # # df.rename(columns={"Notes": "Raw Data"}, inplace=True)
            # # df.loc[:,'Phone Number(s)'] = df.loc[:,'Phone Number(s)'].apply(lambda x: literal_eval(x))
            # # df['Description'] = df['Description'].map(str) + " | " + df['Title'].map(str)



            # df = df.drop_duplicates(subset=['First Name', 'Last Name', 'Email', 'Address'], keep='first')

            df = df[['First Name', 'Last Name', 'Email', 'Phone Number(s)', 'Address', 'Raw Data']]


            print(f'df.shape: {df.shape}')

            print(f'global_df.shape: {global_df.shape}')
            global_df = pd.concat([global_df, df])

            print(f'global_df.shape: {global_df.shape}')
        except:
            print(f'**** Cannot Load {files[_]}')



    print(f'global_df DUPLICATES: {global_df.duplicated().sum()}')

    global_df = global_df.drop_duplicates(keep='first')

    print(f"global_df SHAPE AFTER DROP_DUPS: {global_df.shape}")

    global FINAL_DF

    if 'Raw Data' not in FINAL_DF:
        FINAL_DF['Raw Data'] = ''

    FINAL_DF = pd.concat([FINAL_DF, global_df])

    print(f'FINAL_DF DUPLICATES: {FINAL_DF.duplicated().sum()}')
    print(f'FINAL_DF SHAPE: {FINAL_DF.shape}')
    FINAL_DF = FINAL_DF.drop_duplicates(subset=['First Name', 'Last Name', 'Email', 'Phone Number(s)'], keep='first')


    print(f"FINAL_DF SHAPE AFTER DROP_DUPS: {FINAL_DF.shape}")



    make_sheet(FINAL_DF)




def make_sheet(df):

    os.chdir('../../out')

    df.to_csv("Customer Contact List.csv", index=False)


def extract_phone_numbers(string):

    r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    phone_numbers = r.findall(string)
    numbers =  [re.sub(r'\D', '', number) for number in phone_numbers]
    extracted_numbers = []
    [extracted_numbers.append(number) for number in numbers if number not in extracted_numbers]
    return extracted_numbers


def extract_email_addresses(string):

    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    emails = []
    [emails.append(item) for item in r.findall(string) if item not in emails]
    return emails


def ie_preprocess(document):

    document = ' '.join([i for i in document.split() if i not in stop])
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences


def extract_names(document):

    names = []
    sentences = ie_preprocess(document)
    for tagged_sentence in sentences:
        for chunk in nltk.ne_chunk(tagged_sentence):
            if type(chunk) == nltk.tree.Tree:
                if chunk.label() == 'PERSON':
                    names.append(' '.join([c[0] for c in chunk]))
    extracted_names = []
    [extracted_names.append(name) for name in names if name not in extracted_names]

    names_checked = []


    names_checked = []

    for name in name_list:
        for item in names:
            if name in item.lower():
                if item not in names_checked:
                    names_checked.append(item)

    first_names = [x.split()[0] for x in names_checked]
    # print(f'NAMES_CHECKED BEFORE CLEANING: {names_checked}')


    return extracted_names


def easy_name(cell):
    cell.replace('<br>', '\n')
    
    if cell.startswith('\n'):
        cell.lstrip('\n')
    name = cell.split('\n')[0]
    return name

def last_name(cell):
    cell = cell.split()
    if len(cell) > 1:
        last_name = cell[-1]
        return last_name
    
def first_name(cell):
    full = cell.split()
    first = ' '.join(full[: len(full) - 1])
    return first

main()
