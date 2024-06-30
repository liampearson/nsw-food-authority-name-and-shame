# Data Dictionary

This document provides descriptions for the data elements found within the project's dataset

## Table: dataset.csv

| Column Name | Data Type | Description                                |
|--------------|-----------|----------------------------------------------------|
| notice_number| integer   | Unique identifier for the penalty notice              |
| trade_name   | string    |.....|
| suburb        | string    |.....|
| council   | string  | ..... |
| date   | datetime  | ..... |
| party_served   | string  | ..... |
| party_served_trade_name   | string  | ..... |
| address   | string  | ..... |
| city   | string  | ..... |
| postcode   | string  | ..... |
| date_alleged_offence   | datetime  | ..... |
| offence_code   | string  | ..... |
| offence_description   | string  | ..... |
| offence_circumstances   | string  | ..... |
| penalty_amount   | int  | ..... |
| party_served_surname_company   | string  | ..... |
| penalty_date_served   | string  | ..... |
| penalty_issued_by   | string  | ..... |
| published_date   | datetime  | Date the details of this penalty notice were first published |
| updated_date   | datetime  | Date the details of this penalty notice were last updated |
| party_served_given_name   | string  | ..... |
| scrape_timestamp_utc   | string  | datetime record was scraped and added to this dataset |
| date_removed_from_website   | datetime  | date the penalty notice was removed from website (They only appear on website for 12 months) |


---

**Data Source**

List of Penalties: https://www.foodauthority.nsw.gov.au/offences/penalty-notices

Details of each penalty: https://www.foodauthority.nsw.gov.au/offences/penalty-notices/<notice_number>

**Data Processing Steps**

**Known Data Quality Issues**
