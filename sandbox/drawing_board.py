from bs4 import BeautifulSoup, SoupStrainer
import requests
import time
import asyncio
import pandas
import os
import ezodf
import logging
import nltk
from nltk.corpus import stopwords
import re
import address_extract
import pickle
from commonregex import CommonRegex
import string


stop = stopwords.words('english')

ROOT_DIR = os.getcwd()
DATA_DIR = os.path.join(ROOT_DIR, 'Customer Export')
RAW_DATA_LIST = os.listdir(os.path.join(os.getcwd(), 'Customer Export'))
OUT_FILE = os.path.join(ROOT_DIR, 'Customer Contact Information.csv')
NAME_LIST = os.path.join(ROOT_DIR, 'NAMES.DIC')
IOB_PICKLE = os.path.join(ROOT_DIR, 'dataset', 'IOB_tagged_addresses.pkl')
with open(IOB_PICKLE, 'rb') as fp:
        PICKLE_DATASET = pickle.load(fp)
_LOGGER = logging.getLogger(__name__)

PARSE_FILE = "2017 Customer Data - Keegan's Copy.xlsx"

def main():
    os.chdir(DATA_DIR)

    customer_extract(parse_df(PARSE_FILE))


    # skip_list = [
    #     'desktop.ini',
    #     "2017 Customer Data - Keegan's Copy.xlsx",
    #     "MASTER.ods",
    # ]
    # for source_file in RAW_DATA_LIST:
    #     if source_file in skip_list or source_file.startswith('.'):
    #         print(f'Skipping over {source_file}')
    #         df = None
    #     else:
    #         try:
    #             df = parse_df(source_file)
    #             customer_extract(df)
    #             print(len(df))
    #         except:
    #             print(f'{source_file} failed...')

def customer_extract(df):
   

    def extract_email_addresses(string):
        r = re.compile(r'[\w\.-]+@[\w\.-]+')
        emails = []
        [emails.append(item) for item in r.findall(string) if item not in emails]
        return emails
    
    def extract_phone_numbers(string):
        r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
        phone_numbers = r.findall(string)
        numbers =  [re.sub(r'\D', '', number) for number in phone_numbers]
        extracted_numbers = []
        [extracted_numbers.append(number) for number in numbers if number not in extracted_numbers]
        return extracted_numbers

    def clean_names(name):
        names_checked = []
        name_list = []
        with open(NAME_LIST, 'r') as f:
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
        # for name in names_checked:
        #     for address in addresses:
        #         if name in address:
        #             names_checked.remove(name)
        # for name in names_checked:
        #     if name in first_names:
        #         names_checked.remove(name)

    def parse_address(source_file):
        parsed_text = CommonRegex(source_file)
        chunker = address_extract.get_address_chunker(PICKLE_DATASET)
        return address_extract.extract_address(chunker, source_file)

    print('___________________________________________')
    print(f'DF TYPE : {type(df)}')
    print(len(df))

    if isinstance(df, str):
        print(df)
    elif isinstance(df, pandas.core.frame.DataFrame):
        for i in range(5):
            row = ''

            for info in df.iloc[i][:len(df.iloc[i])]:
                print(info)
                row += info
                print(row)

            ' '.join(row)
            names = extract_names(row)
            email = extract_email_addresses(row)
            phone = extract_phone_numbers(row)
            addresses = regex_address_extract(row)

            print(f'NAMES: {names}')
            print(f'EMAIL: {email}')
            print(f'PHONE: {phone}')
            print(f'ADDRESSES: {addresses}')

    print('___________________________________________')



def parse_df(source_file):
    failed_df = []
    if source_file in os.listdir():
        print(f'Located {source_file}')
    try:
        print(f'Opening {source_file}')
        #******* remove file when finished!!!!!

        file_ext = source_file.split(".")[1]
        if file_ext == "ods":
            print('Calling ODS function...')
            df = parse_ods(source_file)
            print(f'Records: {len(df)}')
        elif file_ext == "csv":
            print('Calling CSV function...')
            try:
                df = pandas.parse_csv(source_file)
            except:
                print('parse_csv failed....')
                df = pandas.read_csv(source_file, sep='delimiter', header=None, engine='python')
            print(f'Records: {len(df)}')
        elif file_ext == "xls" or "xlsx":
            print('Calling XLSX function...')
            try:
                df = pandas.read_excel(source_file)
                print(f'Records: {len(df)}')
            except:
                print('read_excel failed, trying read_html or concat....')
                df = pandas.read_html(source_file)
                df = pandas.concat(df)     
                print(f'Records: {len(df)}')
        #  li.append(df)
        # for i in range(len(df)):
        # for i in range(5):
        #     li.append(df.iloc[i].values)
        print(f'Records: {len(df)}')
    except:
        failed_df.append(source_file)
        df = None
        
    # print(f'FAILED: {failed_df}')
    # print(f'{len(failed_df)} out of {len(RAW_DATA_LIST)} FAILED')
    # for i in range(20):
    #     print(li[i])
    return df


def parse_csv(source_file):
    df = []

    with open(source_file, 'r') as f:
        lis = []
        li = ''
        for line in f:
            if not line.startswith('\n'):
                li += line.strip()
            else:
                lis.append(li)
                df.append(lis)
                lis = []
                li = ''

    return df    

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
    df = pandas.DataFrame(df_dict)
    return df


def regex_address_extract(row):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    regex.sub('', row)
    print(f'PPunct: {row}')

    parsed_text = CommonRegex(row)
    addresses = parsed_text.street_addresses
    # r = re.compile(r'^(?<address1>(?>\d{1,6}(?>\ 1\/[234])?( (N(orth)?|S(outh)?)? ?(E(ast)?|W(est)?))?((?> \d+ ?(th|rd|st|nd))|(?> [A-Z](?>[a-z])+)+) (?>(?i)THROUGHWAY|TRAFFICWAY|CROSSROADS|EXPRESSWAY|BOULEVARD|CROSSROAD|EXTENSION|JUNCTIONS|MOUNTAINS|STRAVENUE|UNDERPASS|CAUSEWAY|CRESCENT|CROSSING|JUNCTION|MOTORWAY|MOUNTAIN|OVERPASS|PARKWAYS|TURNPIKE|VILLIAGE|VILLAGES|CENTERS|CIRCLES|COMMONS|CORNERS|ESTATES|EXPRESS|FORESTS|FREEWAY|GARDENS|GATEWAY|HARBORS|HIGHWAY|HOLLOWS|ISLANDS|JUNCTON|LANDING|MEADOWS|MOUNTIN|ORCHARD|PARKWAY|PASSAGE|PRAIRIE|RANCHES|SPRINGS|SQUARES|STATION|STRAVEN|STRVNUE|STREETS|TERRACE|TRAILER|TUNNELS|VALLEYS|VIADUCT|VILLAGE|ALLEE|ARCADE|AVENUE|BLUFFS|BOTTOM|BRANCH|BRIDGE|BROOKS|BYPASS|CANYON|CAUSWA|CENTER|CENTRE|CIRCLE|CLIFFS|COMMON|CORNER|COURSE|COURTS|CRSENT|CRSSNG|DIVIDE|DRIVES|ESTATE|EXTNSN|FIELDS|FOREST|FORGES|FREEWY|GARDEN|GATEWY|GATWAY|GREENS|GROVES|HARBOR|HIGHWY|HOLLOW|ISLAND|ISLNDS|JCTION|JUNCTN|KNOLLS|LIGHTS|MANORS|MEADOW|MEDOWS|MNTAIN|ORCHRD|PARKWY|PLAINS|POINTS|RADIAL|RADIEL|RAPIDS|RIDGES|SHOALS|SHOARS|SHORES|SKYWAY|SPRING|SPRNGS|SQUARE|STRAVN|STREAM|STREME|STREET|SUMITT|SUMMIT|TRACES|TRACKS|TRAILS|TUNNEL|TURNPK|UNIONS|VALLEY|VIADCT|VILLAG|ALLEE|ALLEY|ANNEX|AVENU|AVNUE|BAYOO|BAYOU|BEACH|BLUFF|BOTTM|BOULV|BRNCH|BRDGE|BROOK|BURGS|BYPAS|CANYN|CENTR|CNTER|CIRCL|CRCLE|CLIFF|COURT|COVES|CREEK|CRSNT|CREST|CURVE|DRIVE|FALLS|FERRY|FIELD|FLATS|FORDS|FORGE|FORKS|FRWAY|GARDN|GRDEN|GRDNS|GTWAY|GLENS|GREEN|GROVE|HARBR|HRBOR|HAVEN|HIWAY|HILLS|HOLWS|ISLND|ISLES|JCTNS|KNOLL|LAKES|LNDNG|LIGHT|LOCKS|LODGE|LOOPS|MANOR|MILLS|MISSN|MOUNT|MNTNS|PARKS|PKWAY|PKWYS|PATHS|PIKES|PINES|PLAIN|PLAZA|POINT|PORTS|RANCH|RNCHS|RAPID|RIDGE|RIVER|ROADS|ROUTE|SHOAL|SHOAR|SHORE|SPRNG|SPNGS|SPURS|STATN|STRAV|STRVN|SUMIT|TRACE|TRACK|TRAIL|TRLRS|TUNEL|TUNLS|TUNNL|TRNPK|UNION|VALLY|VIEWS|VILLG|VILLE|VISTA|WALKS|WELLS|ALLY|ANEX|ANNX|AVEN|BEND|BLUF|BLVD|BOUL|BURG|BYPA|BYPS|CAMP|CNYN|CAPE|CSWY|CENT|CNTR|CIRC|CRCL|CLFS|CLUB|CORS|CRSE|COVE|CRES|XING|DALE|DRIV|ESTS|EXPR|EXPW|EXPY|EXTN|EXTS|FALL|FRRY|FLDS|FLAT|FLTS|FORD|FRST|FORG|FORK|FRKS|FORT|FRWY|GRDN|GDNS|GTWY|GLEN|GROV|HARB|HIWY|HWAY|HILL|HLLW|HOLW|INLT|ISLE|JCTN|JCTS|KEYS|KNOL|KNLS|LAKE|LAND|LNDG|LANE|LOAF|LOCK|LCKS|LDGE|LODG|LOOP|MALL|MNRS|MDWS|MEWS|MILL|MSSN|MNTN|MTIN|NECK|ORCH|OVAL|PARK|PKWY|PASS|PATH|PIKE|PINE|PNES|PLNS|PLZA|PORT|PRTS|RADL|RAMP|RNCH|RPDS|REST|RDGE|RDGS|RIVR|ROAD|SHLS|SHRS|SPNG|SPGS|SPUR|SQRE|SQRS|STRA|STRM|STRT|TERR|TRCE|TRAK|TRKS|TRLS|TRLR|TUNL|VLLY|VLYS|VDCT|VIEW|VILL|VLGS|VIST|VSTA|WALK|WALL|WAYS|WELL|ALY|ANX|ARC|AVE|AVN|BCH|BND|BLF|BOT|BTM|BRG|BRK|BYP|CMP|CPE|CEN|CTR|CIR|CLF|CLB|COR|CTS|CRK|DAM|DIV|DVD|DRV|EST|EXP|EXT|FLS|FRY|FLD|FLT|FRD|FRG|FRK|FRT|FWY|GLN|GRN|GRV|HBR|HVN|HTS|HWY|HLS|ISS|JCT|KEY|KYS|KNL|LKS|LGT|LCK|LDG|MNR|MDW|MNT|MTN|NCK|OVL|PRK|PKY|PLN|PLZ|PTS|PRT|PRR|RAD|RPD|RST|RDG|RIV|RVR|RDS|ROW|RUE|RUN|SHL|SHR|SPG|SQR|SQU|STA|STN|STR|SMT|TER|TRK|TRL|VLY|VIA|VWS|VLG|VIS|VST|WAY|WLS|AV|BR|CP|CT|CV|DL|DM|DV|DR|FT|HT|HL|IS|KY|LK|LN|LF|MT|PL|PT|PR|RD|SQ|ST|UN|VW|VL|WY))( (N(orth)?|S(outh)?)? ?(E(ast)?|W(est)?)?)?)$')
    # addresses = []
    # [addresses.append(item) for item in r.findall(object) if item not in addresses]
    return addresses
    


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

main()

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


# addrs = ["4170 137th Street West Rosemount, 55068", "529 6th St. Lake Elmo"]
# # addr = "4170 137th Street West Rosemount"
# for addr in addrs:
#     print(f'Correcting {addr}...')
#     google_address(addr)