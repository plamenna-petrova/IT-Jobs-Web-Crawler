import requests

from bs4 import BeautifulSoup

import time

import logging

IT_JOBS_SCRAPING_URL = 'https://www.jobs.bg/en/front_job_search.php?subm=1&categories%5B0%5D=56&domains%5B0%5D=1&domains%5B1%5D=2&domains%5B2%5D=3&domains%5B3%5D=5'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US'
}

logger = logging.getLogger('ftpuploader')

def find_it_jobs():
    try:
        it_jobs_response = requests.get(IT_JOBS_SCRAPING_URL, headers=headers)
        it_jobs_response_status_code = it_jobs_response.status_code
        if it_jobs_response_status_code != 200:
            if it_jobs_response_status_code == 503:
                logger.warning(f'it.jobs.bg has blacklisted the user agent. Try with another popular one: https://techblog.willshouse.com/2012/01/03/most-common-user-agents/')
            else:
                logger.warning(f'Error fetching the given page, https://http.cat/{it_jobs_response_status_code}')
            exit()
        else:
            it_jobs_html_text = it_jobs_response.text
            beautiful_soup = BeautifulSoup(it_jobs_html_text, 'lxml')
            print(beautiful_soup.prettify())
    except Exception as exception:
        logger.error(str(exception))


if __name__ == '__main__':
    find_it_jobs()
    base_waiting_time = 10
    print(f'Waiting {base_waiting_time} minutes...')
    time.sleep(base_waiting_time * 60)

