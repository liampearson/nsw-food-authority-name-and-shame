import pandas as pd
import requests # may not run on online IDE 
from bs4 import BeautifulSoup 
import urllib.request # Library for opening url and creating
from urllib.error import URLError, HTTPError
from pprint import pprint # pretty-print python data structures
from html_table_parser.parser import HTMLTableParser # for parsing all the tables present on the website
from datetime import datetime, timezone
import numpy as np

#using requests.get(url)
notice_number = '3164613349'
print(notice_number)
url = "https://www.foodauthority.nsw.gov.au/offences/penalty-notices/"+str(notice_number) 

try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception if the request failed
    print(f"Request succeeded! Status code: {response.status_code}")
    #print(response.content)
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")


# #using urllib.request and urllib.request.urlopen
# #the parent page we are going to scrape
# url = "https://www.foodauthority.nsw.gov.au/offences/penalty-notices"

# #making request to the website
# req = urllib.request.Request(url=url)
# try:
#     with urllib.request.urlopen(req) as response:
#         html = response.read()
# # Process the fetched HTML content here...
# except HTTPError as e:
#     print(f"HTTP Error: {e.code} - {e.reason}")  # Print the HTTP error code and reason
# except URLError as e:
#     print(f"URL Error: {e.reason}")              # Print the underlying URL error reason
# except Exception as e:
#     print(f"An error occurred: {e}")              # Catch any other unexpected errors

