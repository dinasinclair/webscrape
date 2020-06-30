"""
Sql queries
"""
drop_jobs_table = """DROP TABLE IF EXISTS jobs"""
drop_queries_table = """DROP TABLE IF EXISTS queries"""
create_jobs_table = """CREATE TABLE IF NOT EXISTS jobs (
    job_id integer NOT NULL PRIMARY KEY,
    query_id integer NOT NULL, 
    app_type text NOT NULL,
    app_text text NOT NULL,
    company text NOT NULL,
    title text NOT NULL,
    description text NOT NULL, 
    company_url text NOT NULL, 
    indeed_url text NOT NULL, 
    page_number integer NOT NULL, 
    rank_on_page integer NOT NULL,
    FOREIGN KEY (query_id)
       REFERENCES queries (query_id) 
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);"""
insert_into_jobs_table = ''' INSERT INTO jobs (query_id, 
    app_type, 
    app_text, 
    company, 
    title, 
    description, 
    company_url, 
    indeed_url, 
    page_number, 
    rank_on_page)
    VALUES(?,?,?,?,?,?,?,?,?,?) '''
create_queries_table = """CREATE TABLE IF NOT EXISTS queries (
    query_id integer NOT NULL PRIMARY KEY,
    scraper_version text NOT NULL,
    query_text text NOT NULL,
    location text NOT NULL,
    time datetime NOT NULL,
    result_url text NOT NULL,
    total_hits int
);"""
insert_into_queries_table = """INSERT INTO queries (
    scraper_version,
    query_text, 
    location,
    time, 
    result_url,
    total_hits)
    VALUES(?,?,?,?,?,?) """
