# IT-Jobs-Web-Crawler


## This project focuses on the scraping for IT job posts from the popular website - it.jobs.bg. 

## The command script has the functionalities to:
  - filter the results for seniority level, based on user choice - the available options are also: Junior, Mid and Senior.
  - save the scraped results in the following file formats: csv, txt (with subdirectory generation) and pdf, again depending on the preferences of the user
  - once the filtering and saving options are configured, the crawler will be started and the results will be scaped infinitely each 10 minutes, 
    until the program is stopped
  - during the process the results will be consequently printed on the console
    
## The project makes use of the following libraries:
  - beautifulsoup4
  - requests
  - lxml
  - csv
  - os
  - fpdf
  - logging

