# information-extraction.py

import re
import nltk
from nltk.corpus import stopwords
import time
from bs4 import BeautifulSoup
import requests

stop = stopwords.words('english')

string = """
Katie Troye
4170 137th Street West Rosemount, 55068
763-443-7823
katie@katietroye.com

8-10 am arrival

36 window panes = $126
14 screens = $14
Total = $140 plus tax

---
We didn't clean all windows this time. Only cleaned 31 panes this time
Rate at $3.5 per pane = $108.50 plus tax
Wrote check for $116.94
Katie Troye
4170 137th Street West Rosemount, 55068
763-443-7823
katie@katietroye.com

8-10 am arrival

36 window panes = $126
14 screens = $14
Total = $140 plus tax

---
We didn't clean all windows this time. Only cleaned 31 panes this time
Rate at $3.5 per pane = $108.50 plus tax
Wrote check for $116.94
Katie Troye
4170 137th Street West Rosemount, 55068
763-443-7823
katie@katietroye.com

8-10 am arrival

36 window panes = $126
14 screens = $14
Total = $140 plus tax

---
We didn't clean all windows this time. Only cleaned 31 panes this time
Rate at $3.5 per pane = $108.50 plus tax
Wrote check for $116.94
Katie Troye
4170 137th Street West Rosemount, 55068
763-443-7823
katie@katietroye.com
8174563721
817.456.3722
(817)4563723
(817)456-3724
(817) 456 3725
(817) 456-3726
817 456 3727
817 4563728
8-10 am arrival

36 window panes = $126
14 screens = $14
Total = $140 plus tax

---
We didn't clean all windows this time. Only cleaned 31 panes this time
Rate at $3.5 per pane = $108.50 plus tax
Wrote check for $116.94
Tus. 4/18  
529 6th St. Lake Elmo

58 panesTus. 4/18  
529 6th St. Lake Elmo

58 panes

"""

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
    return extracted_names

def google_address(address, state=' MN'):
    if state == False:
        print('** Need state in query')
        raise Exception
    URL = f'https://www.google.com/search?q={address + state}'
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {'user-agent': USER_AGENT}
    resp = requests.get(URL, headers=headers)
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html.parser')
    else:
        print(f'Status Code != 200')
        raise Exception
    
    results = []
    g = soup.find('div', class_='vk_sh vk_bk')
    print('__________________________________________________________')
    title_content = g.find('div', class_='desktop-title-content').text
    title_subcontent = g.find('span', class_='desktop-title-subcontent').text
    if title_content or title_subcontent:
        item = {
            'title_content': title_content,
            'title_subcontent': title_subcontent
        }
        results.append(item)
    full_addr = title_content + ' ' + title_subcontent
    print(f'FULL ADDRESS: {full_addr}')
    print(full_addr)
    return full_addr
    
print('_______________________________________________')
numbers = extract_phone_numbers(string)
emails = extract_email_addresses(string)
names = extract_names(string)
addrs = ["4170 137th Street West Rosemount, 55068", '529 6th St. Lake Elmo']



addresses = []
for addr in addrs:
    addresses.append(google_address(addr))

print(f'REGEX PHONE: {numbers}')
print(f'REGEX EMAIL: {emails}')
print(f'NLTK NAMES: {names}')
print(f'ADDRESSES: {addresses}')

names_checked = []
name_list = []
with open('NAMES.DIC', 'r') as f:
    for _ in f:
        name_list.append(_.strip())

names_checked = []
names_lower = [name.lower() for name in names]
for name in name_list:
    for item in names:
        if name in item.lower():
            if item not in names_checked:
                names_checked.append(item)
first_names = [x.split()[0] for x in names_checked]
print(f'NAMES_CHECKED BEFORE CLEANING: {names_checked}')
for name in names_checked:
    for address in addresses:
        if name in address:
            names_checked.remove(name)
for name in names_checked:
    if name in first_names:
        names_checked.remove(name)
    
print(f'NAMES_CHECKED AFTER CLEANING: {names_checked}')

def check_for_multiple_results():
    """
    Check to see if any of the cells have more than one value
    and HOW MANY have more than one value
    NAME = ['Katie', 'Street West Rosemount', 'Katie Troye']
    """
    # .split() each element of the address and compare street address line for dups
    pass