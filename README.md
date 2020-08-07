# Pronoun WebScraper

This webscraper iterates through indeed.com job postings for a given location (ex. "Chicago, IL") and job type (ex. "Machine Learning Engineer"), storing all job applications that use LGBTQ friendly language ("pronoun", "transgender", etc.). While some applications are done within indeed.com, some require following external links to a wide variety of job application website formats, thus the code complexity.

Indeed.com states in their [robots.txt](https://www.indeed.com/robots.txt) that scraping their site is allowed.

## Version Notes
#### 0.0.0
All the coding done before I started tracking the version number. 
Includes basic scraping functionality, jobs table, queries table.
#### 1.0.0
Adds version number and num_hits to the queries table.

## Schema
This schema follows roughly a star schema, with each job joined across several descriptive dimensions.

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

#### Dimension: Stats Table

Match with jobs on stats.job_id = jobs.job_id
 - Int job_id
 - Text text
 - Int description_frequency
 - Int app_frequency
