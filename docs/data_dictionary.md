# Data Dictionary

This document provides descriptions for the data elements found within the project's dataset

## Table: dataset.csv

| Column Name | Data Type | Description                                |
|--------------|-----------|----------------------------------------------------|
| published_date   | datetime  | Date the details of this penalty notice were first published |
| notice_number| integer   | Unique identifier for the penalty notice              |
| council   | string  | Which LGA the business address is in |
| trade_name   | string    | The business' trading name|
| suburb        | string    |Suburb of the business|
| address   | string  | Address of the business |
| postcode   | string  | The business' postcode |
| date_alleged_offence   | datetime  | date of alleged offence |
| offence_code   | string  | ..... |
| offence_description   | string  | ..... |
| offence_circumstances   | string  | ..... |
| party_served_company   | string  | ..... |
| party_served_given_name   | string  | ..... |
| party_served_surname   | string  | ..... |
| penalty_amount   | int  | ..... |
| penalty_issued_by   | string  | ..... |
| penalty_date_served   | string  | ..... |
| updated_date   | datetime  | Date the details of this penalty notice were last updated |
| scrape_timestamp_utc   | string  | datetime record was scraped and added to this dataset |
| date_removed_from_website   | datetime  | date the penalty notice was removed from website (They only appear on website for 12 months) |

---

**Data Sources**

* List of Penalties:
  * https://www.foodauthority.nsw.gov.au/offences/penalty-notices
* Details of each penalty
  * https://www.foodauthority.nsw.gov.au/offences/penalty-notices/<notice_number>

**Data Processing Steps**

**Known Data Quality Issues**
