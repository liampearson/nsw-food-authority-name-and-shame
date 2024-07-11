#!/usr/bin/env python
# coding: utf-8

# # Analysis of NSW Food Authority's Name & Shame Register
# 
# The NSW Food Authority publishes lists of businesses that have breached or are alleged to have breached NSW food safety laws. Publishing the lists gives consumers more information to make decisions about where they eat or buy food. Individuals and businesses may receive either a penalty notice for their alleged offence or be prosecuted before a court.

# In[2]:


import sys
print(sys.version)


# In[1]:


# Libraries
#import sys
#sys.path.append('../utils')  # For notebooks
#import utils 
import pandas as pd
import numpy as np
#import boto3
import os
import io
from dotenv import load_dotenv #for loading env variables
from github import Github #for pushing data to Github

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Add the script's directory to the Python path
sys.path.append(script_dir)

# Now you can import utils
import utils

# ## 1. Get Existing Data from Github
# 
# The Food Authority's Name & Shame website only displays the last 12 months of data. But since I started this repository (in June, 2024) I simply append any new data to the bottom of a dataset stored on Github. So step 1 of the overall process is to get this data
# 
# #### Get access keys and read from Github

# In[2]:
#####################debugging
notice_number = '3164613349'
record = utils.get_penalty_notice(notice_number)
print(record)
print("Complete\n")
#############################


# Load the environment variables from .env
load_dotenv()

# GitHub Authentication (Replace placeholders with your information)
access_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
g = Github(access_token)

# Repository and File Information
repo_owner = "liampearson" 
repo_name = "nsw-food-authority-name-and-shame"
file_path = "data/dataset.csv"

# Get Repository
repo = g.get_user(repo_owner).get_repo(repo_name)

# Get File Contents
try:
    file_content = repo.get_contents(file_path)
    
    decoded_content = file_content.decoded_content.decode() # Decode if necessary    

    prev_df = pd.read_csv(io.StringIO(decoded_content))

    prev_df['notice_number'] = prev_df['notice_number'].astype(str) #convert to string for comparison
    print("   Dataset has been downloaded. Shape: {}\n".format(prev_df.shape))

except Exception as e:
    print(f"Error downloading file: {e}")

prev_df.head()


# ## 2. Get all notices that are currently on the Food Authority Website
# 
# The function `scrape_tables` takes a url (which we've defined as the food authority Name and Shame Register) and iterates over child-page of the website. 
# 
# The result is `notice_df`; a dataframe of all the notices across all pages of the parent url. 

# In[3]:


#the parent page we are going to scrape
url = "https://www.foodauthority.nsw.gov.au/offences/penalty-notices"

print("iterate over the pages of url:\n  {}\n".format(url))
#scrape each of the pages and get the table of notices
notice_df = utils.scrape_tables(url)


# ## 3. Compare the website to dataset
# 
# We will now compare the notices found in Step 2 (whats currently live on the website), to the notices we've scraped in the past. 
# 
# This will tell us:
# * what has been removed from the webstie (`removed_notice_numbers`)
# * what has been added to the website (`new_notice_numbers`)

# In[4]:


old_notice_numbers = prev_df[prev_df['date_removed_from_website'].isnull()]['notice_number'].tolist()
current_notice_numbers = notice_df['notice_number'].tolist()

#get the difference of the above to determine new and removed notices.
removed_notice_numbers = set(old_notice_numbers) - set(current_notice_numbers)
new_notice_numbers = set(current_notice_numbers) - set(old_notice_numbers)

print("{} notice_numbers removed".format(len(removed_notice_numbers)))
print("{} notice_numbers added".format(len(new_notice_numbers)))


# ### Get More info per notice
# 
# Each notice has a dedicated child-page that outlines extra details such as penalty_amount, circumstances, address etc.
# 
# if **a notice was added**:
# * open up a particular page to get the finer details
# * then append to the dataset
# * when complete, join this extra information to the dataset
# 
# if **a notice was removed**
# * update the `date_removed_from_website` field in the dataset
# 

#check if notice numbers were removed
if len(removed_notice_numbers)==0:
    print("   0 notice_numbers removed")
    
else:
    print("   {} notice_numbers removed".format(len(removed_notice_numbers)))
    prev_df = utils.handle_removed_notices(prev_df, removed_notice_numbers)

#check if any new notice numbers
if len(new_notice_numbers)==0:
    print("   0 new notice_numbers added")
    result = prev_df #since no new entries, the result is just the old dataframe. 
    
else:
    print("   {} new notice_numbers found".format(len(new_notice_numbers)))
    print(new_notice_numbers)
    
    #we'll only work with these
    notice_df = notice_df[notice_df['notice_number'].isin(new_notice_numbers)]
    
    #check they're unique
    #check only unique numbers
    if not len(notice_df['notice_number'].unique()) == len(notice_df):
        raise ValueError("Not all policy numbers are unique")
        
    else: #Get details per notice_number
        print("4. Get penalty info...")
        #empty list to collect each row as a dictionary
        penalties = []

        for notice_number in new_notice_numbers:
            print("   processing: {}".format(notice_number))

            # scrape the website
            record = utils.get_penalty_notice(notice_number)    
            penalties.append(record)
            
        print("Complete\n")

        penalties_df = pd.DataFrame(penalties)
        
        utils.cleanup_dataframe(penalties_df)
        notice_df = utils.join_dataframes(penalties_df, notice_df)
        notice_df = utils.add_timestamp(notice_df)
        notice_df['council'] = notice_df['council'].str.upper()

        result = pd.concat([prev_df, notice_df], ignore_index=True)

    #regardless of if there were some removed added or nothing
    result.drop('trade_name', axis=1, inplace=True)
    result.rename(columns={'party_served_trade_name':'trade_name'}, inplace=True)
    
    reorder_columns = ['published_date',
                   'notice_number',
                   'council',
                   'trade_name',
                   'suburb',
                   'address',
                   'postcode',
                   'date_alleged_offence',
                   'offence_code',
                   'offence_description',
                   'offence_circumstances',
                   'party_served_company',
                   'party_served_given_name',
                   'party_served_surname',
                   'penalty_amount',
                   'penalty_issued_by',
                   'penalty_date_served',
                   'updated_date',
                   'scrape_timestamp_utc',
                   'date_removed_from_website']
    
    result = result[reorder_columns]
    
    result["published_date"]= pd.to_datetime(result['published_date'], errors='coerce').dt.date
    result['penalty_amount'] = result['penalty_amount'].astype(int)
    result.sort_values(by=['published_date', 'council', 'suburb', 'trade_name'], inplace=True, ascending=[False, True, True,True])
    
    result.head()


# ## 4. Finalise the dataset and push back to Github

# In[6]:


if len(new_notice_numbers)>0 or len(removed_notice_numbers)>0:
    
    #overwrite dataset
    print("5. Begin Upload to Github...")
    print("shape:",result.shape)
    repo = g.get_user(repo_owner).get_repo(repo_name)
    
    # Update the main dataset
    file_content = result.to_csv(index=False)  # Convert to CSV

    try:
        # Check if file exists
        contents = repo.get_contents(file_path)
        repo.update_file(contents.path, "Updated dataset", file_content, contents.sha)
        print(f"Updated existing file: {file_path}")

    except:  # File doesn't exist
        repo.create_file(file_path, "Added dataset", file_content)
        print(f"Created new file: {file_path}") 

#There were no changes to data so no need to upload.
else:
    print("no changes to the website so dataset will not be updated at this time.")
    print("shape:",result.shape)
    
result.head()


# ## Create and push subset of latest notices to Github

# In[7]:


latest_results = result[result['published_date']==result['published_date'].max()][['published_date', 'council','trade_name', 'suburb','address', 'penalty_amount',
       'offence_circumstances','offence_code']]

print("shape:",latest_results.shape)

# Update the latest_result dataset
file_content = latest_results.to_csv(index=False)  # Convert to CSV
file_path = "data/last_weeks_notices.csv"

try:
    # Check if file exists
    contents = repo.get_contents(file_path)
    repo.update_file(contents.path, "Updated dataset", file_content, contents.sha)
    print(f"Updated existing file: {file_path}")

except:  # File doesn't exist
    repo.create_file(file_path, "Added dataset", file_content)
    print(f"Created new file: {file_path}")

latest_results

