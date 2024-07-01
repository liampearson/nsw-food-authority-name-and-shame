import pandas as pd
import requests # may not run on online IDE 
from bs4 import BeautifulSoup 
import urllib.request # Library for opening url and creating 
from pprint import pprint # pretty-print python data structures
from html_table_parser.parser import HTMLTableParser # for parsing all the tables present on the website
from datetime import datetime, timezone

# Opens a website and read its
# binary contents (HTTP Response Body)
def url_get_contents(url):

    # Opens a website and read its
    # binary contents (HTTP Response Body)

    #making request to the website
    req = urllib.request.Request(url=url)
    f = urllib.request.urlopen(req)

    #reading contents of the website
    return f.read()

def scrape_tables(url, page_num=0):
    df = pd.DataFrame()
    while True:
        print("   processing page {} (index: {})...".format(page_num+1, page_num))
        this_page = url + "?page=" + str(page_num)
        try:
            xhtml = url_get_contents(url=this_page).decode('utf-8')

            # Defining the HTMLTableParser object
            p = HTMLTableParser()

            # feeding the html contents in the
            # HTMLTableParser object
            p.feed(xhtml)

            # Now finally obtaining the data of
            # the table required
            if len(p.tables)==0:
                print("   no tables on page {} (index: {})\n".format(page_num+1, page_num))
            elif len(p.tables)>1:
                print("   More than 1 table found\n")

            # converting the parsed data to
            # dataframe
            temp = pd.DataFrame(p.tables[0])

            #set headers as values in first row
            new_header = temp.iloc[0] #grab the first row for the header
            temp = temp[1:] #take the data less the header row
            temp.columns = new_header #set the header row as the df header

            #df = df.append(temp)
            df = pd.concat([df, temp], ignore_index=True)

            page_num+=1

        except:
            break
            print("stopped at page {} (index: {})".format(page_num+1, page_num))
            
    #adjust column names and convert to lowercase
    df.rename(columns={"Date  Sort ascending": "Date"}, inplace=True)
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(' ', '_')
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date

    #check only unique numbers
    if not len(df['notice_number'].unique()) == len(df):
        print("Error: Not all notice_numbers are unique")
            
    return df

def get_penalty_notice(notice_number):
    """
    Given a penalty number from food authority website, go to that page and scrape the data
    Reference: 
        https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/
    Input:
        int (or string) : notice_number (penalty notice number)
        
    Returns:
        record: dict of all the fields
        
    """
    URL = "https://www.foodauthority.nsw.gov.au/offences/penalty-notices/"+str(notice_number) 
    # Send a HTTP request to the specified URL and save the response from server in a response object called r.
    r = requests.get(URL) 

    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 
    #data = soup.find('div', attrs = {'class':'block-region-content'}) # mid Feb 2024
    data = soup.find('div', attrs = {'class':'nsw-layout__main'}) # late Feb 2024


    record = {}
    for row in data.find_all('div'):
        # each div tag has a label and then an item nested within that
        try:
            if 'field__label' in row['class']:
                label = row.text
                #print("label:",label) #dev
                child = row.find_next('div')

                if 'field__item' in child['class']:
                    #print("child:",child.text) #dev
                    item=child.text
                    record[label] = item
            if 'field-content' in row['class']:
                #print("FOUND!!") #dev
                # split the string so as to extract the dates
                dates = row.text
                dates = dates.split("first published ")[1]
                published_date, updated_date = dates.split(", last updated ")
                record['published_date'] = published_date
                record['updated_date'] = updated_date.split(".")[0]
        except:
            pass
    
    return record

#General Cleanup

def cleanup_dataframe(df):
    rename_cols = {}
    rename_cols['Penalty notice number']='notice_number'
    rename_cols['Party served - Trade name']='party_served_trade_name'
    rename_cols['Address - Street']='address'
    rename_cols['Address - City']='city'
    rename_cols['Address - Postal code']='postcode'
    rename_cols['Council']='council'
    rename_cols['Date of alleged offence']='date_alleged_offence'
    rename_cols['Offence code']='offence_code'
    rename_cols['Offence description']='offence_description'
    rename_cols['Nature & circumstances of alleged offence']='offence_circumstances'
    rename_cols['Amount of penalty']='penalty_amount'
    rename_cols['Party served - Surname or company']='party_served_surname_company'
    rename_cols['Date penalty notice served']='penalty_date_served'
    rename_cols['Issued by']='penalty_issued_by'
    rename_cols['Party served - Given names']='party_served_given_name'
    
    print("Cleaning Up Dataframe...")

    #Rename certain columns using the rename_cols dict
    df.rename(columns=rename_cols, inplace=True)

    #remove new line char
    df['date_alleged_offence'] = df['date_alleged_offence'].str.strip()
    df['penalty_date_served'] = df['penalty_date_served'].str.strip()

    #remove dollar sign
    df['penalty_amount'] = df['penalty_amount'].str.replace('$','', regex=False).astype(float)

    df['date_alleged_offence'] = pd.to_datetime(df['date_alleged_offence'], errors='coerce').dt.date
    df['penalty_date_served'] = pd.to_datetime(df['penalty_date_served'], errors='coerce').dt.date
    df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce').dt.date
    df['updated_date'] = pd.to_datetime(df['updated_date'], errors='coerce').dt.date
    
    #Drop 'council' column in one of the tables as appears in both
    df.drop('council', axis=1, inplace=True)

    #Change council to uppercase
    df['council'] = df['council'].str.upper()
    
    print("Cleanup Complete\n")
    
    return df

def join_dataframes(df1, df2):
    print("joining notices with notice-level info...")
    # join notice-level data onto notices
    if len(df1)==len(df2):
        prev_len = len(df2)
        df2 = df2.merge(df1, how='left', left_on='notice_number', right_on='notice_number')
        new_len = len(df2)

        if prev_len != new_len:
            raise ValueError("There was an issue when doing left join; number of rows changed")
            
        else:
            print("Join successful\n")
    else:
        raise ValueError("Differnt number of rows => missing data")
            
    return df2

def add_timestamp(df):
    
    # timestamp when data was collected
    now_utc = datetime.now(timezone.utc)
    # Format the datetime, omitting microseconds
    formatted_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S")

    df['scrape_timestamp_utc'] = formatted_utc
    
    return df

def handle_removed_notices(df, removed):
    #ensure are of type str
    removed = [str(x) for x in removed]
    
    from datetime import date
    date_string = date.today().strftime("%Y-%m-%d")
    
    #update the dataframe with the date it was removed from website
    for r in removed:
        df.loc[df['notice_number']==r, 'date_removed_from_website'] = date_string
    
    return df