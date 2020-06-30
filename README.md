# Pronoun WebScraper

## Version Notes
#### 0.0.0
All the coding done before I started tracking the version number. 
Includes basic scraping functionality, jobs table, queries table.
#### 1.0.0
Adds version number and num_hits to the queries table.

## Schema
Star Schema ish? I should think through if there's a better way to do this.

#### Fact: Jobs Table
 - Int job_id
 - Int query_id
 - Text app_text
 - Text description_text
 - Text job_title
 - Text job_location
 - Text indeed_url
 - Text company_url
 - Int page_appeared
 - Int rank_appeared
 - Text app_type

#### Dimension: Queries Table 

Match with jobs on queries.query_id = jobs.query_id
 - Int query id 
 - Text scraper_version
 - Text query_text
 - Text location
 - Datetime time
 - Text result_url
 - Int total_hits

#### Dimension: Stats Table (TODO not implemented yet)

Match with jobs on stats.job_id = jons.job_id
 - Int job_id
 - Text text
 - Int description_frequency
 - Int app_frequency
