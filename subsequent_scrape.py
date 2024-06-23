#!/usr/bin/env python
# coding: utf-8

#! pip install html-table-parser-python3

import pandas as pd
import utils

print("BEGIN SCRIPT")
#the parent page we are going to scrape
url = "https://www.foodauthority.nsw.gov.au/offences/penalty-notices"#?page=15
print("scraping data from: {}\n".format(url))

#scrape each page and get the table
notice_df = utils.scrape_tables(url)
    
notice_df.head() #inspect dataframe


#Determine the new notice_numbers

#get current dataset
dataset = "nsw_food_auth_name_and_shame.csv"
print("reading in dataset...")
prev_df = pd.read_csv(dataset)
print("Complete; shape: {}\n".format(prev_df.shape))
      
prev_df['notice_number'] = prev_df['notice_number'].astype(str) #convert column to string

#compare the previous notice_numbers to the current ones
old_notice_numbers = prev_df['notice_number'].tolist()
current_notice_numbers = notice_df['notice_number'].tolist()
new_notice_numbers = set(current_notice_numbers) - set(old_notice_numbers)

#check if any new notice numbers
if len(new_notice_numbers)==0:
    print("no new notice_numbers")
    
else:
    print("{} new notice_numbers found".format(len(new_notice_numbers)))
    print(new_notice_numbers)
    
    #we'll only work with these
    notice_df = notice_df[notice_df['notice_number'].isin(new_notice_numbers)]
    
    #check they're unique
    #check only unique numbers
    if not len(notice_df['notice_number'].unique()) == len(notice_df):
        raise ValueError("Not all policy numbers are unique")
        
    else: #Get details per notice_number
        print("Retrieving penalty info...")
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
        
        # Concatenate (append) df2 below df1
        result = pd.concat([prev_df, notice_df], ignore_index=True)  # Reset index for clean numbering

        #overwrite dataset
        print("Updating Dataset...")
        result.to_csv("nsw_food_auth_name_and_shame.csv", index=False)
        print("Complete; dataset Shape:{}".format(result.shape))

print("END SCRIPT.")