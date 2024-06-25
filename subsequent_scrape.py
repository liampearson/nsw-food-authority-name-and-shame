#!/usr/bin/env python
# coding: utf-8

#! pip install html-table-parser-python3
import utils

import pandas as pd
import numpy as np
import boto3
import os
import io
from dotenv import load_dotenv #for loading env variables

print("BEGIN SCRIPT")
print("1. Download existing dataset from S3..")

# Load the environment variables from .env
load_dotenv()

#get aws keys
CLIENT_ID = os.environ.get("AWS_ACCESS_KEY_ID")
CLIENT_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY") 

session = boto3.Session(
    aws_access_key_id=CLIENT_ID,
    aws_secret_access_key=CLIENT_SECRET)

# Create an S3 client using the boto3 session above
s3 = session.client('s3')

# Replace with your bucket name and object key
bucket_name = 'nsw-food-authority-name-and-shame'
object_key = 'dataset.csv'

# Retrieve object from S3
obj = s3.get_object(Bucket=bucket_name, Key=object_key)

# Read the object's content into a Pandas DataFrame
prev_df = pd.read_csv(io.BytesIO(obj['Body'].read()))
print("   Complete. Shape: {}\n".format(prev_df.shape))

print("2. Get all notices currently on the foodauthority website...")
#the parent page we are going to scrape
url = "https://www.foodauthority.nsw.gov.au/offences/penalty-notices"#?page=15
print("   scraping data from: {}".format(url))

#scrape each of the pages and get the table of notices
notice_df = utils.scrape_tables(url)



#get current dataset
#filename = "nsw_food_auth_name_and_shame.csv"
#print("reading in dataset...")
#prev_df = pd.read_csv(filename)

#Determine the new notice_numbers
prev_df['notice_number'] = prev_df['notice_number'].astype(str) #convert column to string
prev_df['date_removed_from_website']='' #once off DELETE

print("3. Comparing website to dataset...")
#compare the previous notice_numbers to the current ones
old_notice_numbers = prev_df['notice_number'].tolist()
current_notice_numbers = notice_df['notice_number'].tolist()
print(type(old_notice_numbers[0])) #dev - unsure why date-removed is not being updated
print(type(current_notice_numbers[0])) #dev - unsure why date-removed is not being updated

new_notice_numbers = set(current_notice_numbers) - set(old_notice_numbers)
removed_notice_numbers = set(old_notice_numbers) - set(current_notice_numbers)

#check if any removed notice numbers
if len(removed_notice_numbers)==0:
    print("   no notice_numbers removed")
    
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

print(len(removed_notice_numbers)) #dev
print(len(new_notice_numbers)) #dev

if len(removed_notice_numbers)>0 or len(new_notice_numbers) >0:
    #overwrite dataset
    print("There have been changes to the dataset")
    print("5. Begin Upload back to S3...")
    print("   Dataset Shape:{}".format(result.shape))

    # Reuse the bucket name but change object key
    #object_key = 'test.csv'
    print("This will write {} to bucket:{}".format(object_key, bucket_name))
    
    # Concatenate (append) df2 below df1
    result = pd.concat([prev_df, notice_df], ignore_index=True)  # Reset index for clean numbering
    result.sort_values(by='published_date', inplace=True)

    #result.to_csv('dataset.csv', index=False)
    #######
    # Convert DataFrame to CSV string
    csv_buffer = io.StringIO()
    result.to_csv(csv_buffer, index=False)  # Set index=False if you don't want row numbers

    # Upload to S3
    s3.put_object(
        Bucket=bucket_name, 
        Key=object_key, 
        Body=csv_buffer.getvalue()
    )

    print("object pushed to S3")
#####

print("END SCRIPT.")