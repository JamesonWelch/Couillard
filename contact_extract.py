import re
from bs4 import BeautifulSoup
import requests
import os
import pandas as pd

RAW_DATA = os.listdir(os.path.join(os.getcwd(), 'Customer Export'))

def main():
    for data in RAW_DATA:
        with open(data, 'r'):
    extract_address()
    extract_phone_numbers()
    extract_names()
    extract_email_addresses()

def extract_address():
    
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
        
        g = soup.find('div', class_='vk_sh vk_bk')
        print('__________________________________________________________')
        title_content = g.find('div', class_='desktop-title-content').text
        title_subcontent = g.find('span', class_='desktop-title-subcontent').text
        if title_content or title_subcontent:
            full_addr = title_content + ' ' + title_subcontent
        print(f'FULL ADDRESS: {full_addr}')
        print(full_addr)
        return full_addr

def extract_phone_numbers(string):
    r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    phone_numbers = r.findall(string)
    numbers =  [re.sub(r'\D', '', number) for number in phone_numbers]
    extracted_numbers = []
    [extracted_numbers.append(number) for number in numbers if number not in extracted_numbers]
    return extracted_numbers

def extract_names():
    pass

def extract_email_addresses(string):
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    emails = []
    [emails.append(item) for item in r.findall(string) if item not in emails]
    return emails



main()
