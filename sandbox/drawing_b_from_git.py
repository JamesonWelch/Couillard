from bs4 import BeautifulSoup, SoupStrainer
import requests
import time
import asyncio
import logging

_LOGGER = logging.get(__name__)

def google_address(address, state=' MN'):
    start = time.time()

    URL = f'https://www.google.com/search?q={address + state}'
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {'user-agent': USER_AGENT}

    strainer = SoupStrainer(attrs=['class:vk_sh vk_bk'])
    

    # async with bot.session.get(URL) as response:
    #         if response.status == 200:
    #             text = await response.read()
   
   
    URL = f'https://www.google.com/search?q={address + state}'
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {'user-agent': USER_AGENT}
    resp = requests.get(URL, headers=headers)
    
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'lxml', parse_only=strainer)
    else:
        print(f'Status Code != 200')
        raise Exception

    # g = soup.find('div', class_='vk_sh vk_bk')
    title_content = soup.find('div', class_='desktop-title-content').text
    title_subcontent = soup.find('span', class_='desktop-title-subcontent').text
    if title_content or title_subcontent:
        
        print(f'title_content: {title_content}')
        print(f'title_subcontent: {title_subcontent}')
        full_address = title_content + ' ' + title_subcontent
    print('__________________________________________________________')
    print(f'FULL ADDRESS: {full_address}')
    print(full_address)
    end = time.time() - start
    print(f'__________ELAPSED: {end}')
    print(f'9000 QUERIES: {end * 9000 / 60 /60}')
    return full_address


    # for g in soup.find_all('div', class_='r'):
    #     anchors = g.find_all('a')
    #     if anchors:
    #         link = anchors[0]['href']
    #         title = g.find('h3').text
    #         item = {
    #             'title': title,
    #             'link': link
    #         }
    #         results.append(item)


addrs = ["4170 137th Street West Rosemount, 55068", "529 6th St. Lake Elmo"]
# addr = "4170 137th Street West Rosemount"
for addr in addrs:
    print(f'Correcting {addr}...')
    google_address(addr)