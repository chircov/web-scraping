from xlsxwriter.workbook import Workbook
from bs4 import BeautifulSoup
from io import BytesIO
import pandas as pd
import requests
import zipfile

PRACTICE_PARAM = "Query"
LOCATION_PARAM = "Location"
DOC_NAME_CLASS = "doc_name"

# This is the url to search for doctors.
doc_info_url = "https://www.patientfusion.com/search"

# This is a good source for zip codes. They update it frequently from the US Census.
zip_codes_url = 'http://download.geonames.org/export/zip/US.zip'


def download_zip_codes(url):
    response = requests.get(url)

    # Download the file into a memory stream and open it as a Zip File.
    with zipfile.ZipFile(BytesIO(response.content)) as archive:
        # Read the txt Zip Codes file as a csv with a space separator into a DataFrame object. 
        df = pd.read_csv(archive.open('US.txt'), delim_whitespace=True,
                         usecols=[1], header=None, names=['Zip Code'])

        return df['Zip Code'].tolist()


def make_request(url, zip_code, field_of_practice):
    r = requests.get(url, params=(
                        (PRACTICE_PARAM, field_of_practice),
                        (LOCATION_PARAM, zip_code)))
    return r.content


def extract_data(page):
    data = []
    soup = BeautifulSoup(page, "html5lib")

    # Get the doctors div and extract their name and url.
    doc_divs = soup.findAll("div", {"class": DOC_NAME_CLASS})
    for doc_div in doc_divs:
        name = doc_div.a.div.text
        url = doc_div.a['href']
        data.append((name, url))

    return data

def write_data_to_excel(data, field_of_practice):

    # Write the data into a new Excel file
    workbook = Workbook('patientfusion_%s_docs.xlsx' % (field_of_practice), {'constant_memory': True})
    worksheet = workbook.add_worksheet()
    for entry in range(len(data)): 
        worksheet.write(entry, 0, data[entry][0]) # doc's name
        worksheet.write(entry, 1, data[entry][1]) # doc's url

    workbook.close()


def get_all_docs_urls(url, field_of_practice):
    zip_codes = download_zip_codes(zip_codes_url)
    for zip_code in zip_codes[406:407]: # zip_codes can couse a dos
        data = extract_data(make_request(url, zip_code, field_of_practice))
        write_data_to_excel(data, field_of_practice)

get_all_docs_urls(doc_info_url, 'Psychology')
