import requests
from bs4 import BeautifulSoup

# Set the URL you want to webscrape from
url = 'https://www.indeed.com/q-machine-learning-engineer-l-Seattle,-WA-jobs.html'

# Connect to the URL
response = requests.get(url)

# Parse HTML and save to BeautifulSoup object
soup = BeautifulSoup(response.text, "html.parser")
job_links = []
titles_found = []
for tag in soup.findAll('a', class_="jobtitle turnstileLink"):
    title = tag["title"]
    titles_found.append(title)
    job_links.append(tag)

# Testing
print("right number of jobs (18)? ", len(job_links) == 18, " actual was {}".format(len(job_links)))
job_titles = [
    "Machine Learning Engineer - Sensing - AI/ML",
    "Siri - Machine Learning Engineer, Siri Experience",
    "AI/ML - Machine Learning Research Engineer, Advanced Development",
    "Machine Learning Educator",
    "Machine Learning Engineer, Siri Web Answers",
    "AI/ML - Machine Learning Research Engineer, Machine Intelligence",
    "Applied Machine Learning Researcher",
    "Machine Learning Software Engineer",
    "2020 TechX Professional Program - Software Engineering and Development",
    "Machine Learning Engineer",
    "Software Engineer, AI",
    "2020 TechX Engineering Internship",
    "NLP / Machine Learning Engineers",
    "Applied Machine Learning Engineer",
    "Machine Learning Engineer",
    "Software Engineer",
    "Machine Learning Software Engineer - US",
    "Siri - Machine Learning Engineer"
]

# titles_found.append(title)
# job_links.append(tag)


not_found = []
found = []
for job_title in job_titles:
    found_it = job_title in titles_found
    if found_it:
        tag = job_links
        found.append(job_title)
    else:
        not_found.append(job_title)

print("found: ", len(found))
print("not found: ", len(not_found), "\n")
print("Found the following:\n", "\n".join(found), "\n")
print("Did not find the following:\n", "\n".join(not_found))


print("\n\n Whole Tag:")
tag = job_links[0]
# Print attributes
for k, v in tag.attrs.items():
    print("'{}': {}".format(k,v))

print("\nStripped String:")
for string in tag.stripped_strings:
    print(repr(string))

next_url = 'http://indeed.com/' + tag['href']

# Connect to the URL
response = requests.get(next_url)
print(next_url)
soup = BeautifulSoup(response.text, "html.parser")
# print (soup)


#
# # for tag in job_links:
# #     print(tag['href'])
# print (len(job_links))
#     # print (tag['href'])
# #    try:
# #        link = tag['href']
# #    except:
# #        print("no href in ", tag)
# #    if 'data/nyct/turnstile' in link:
# #        print("link: ", link)
# #        download_url = 'http://web.mta.info/developers/' + link
# #        urllib.request.urlretrieve(download_url, './' + link[link.find('/turnstile_') + 1:])
# #        time.sleep(1)  # pause the code for a sec
