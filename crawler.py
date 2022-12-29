import requests

from bs4 import BeautifulSoup

import time

import logging

IT_JOBS_SCRAPING_URL = 'https://www.jobs.bg/en/front_job_search.php?subm=1&categories%5B%5D=56&domains%5B%5D=5&domains%5B%5D=3&domains%5B%5D=2&domains%5B%5D=1&salary_from=1'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US'
}

logger = logging.getLogger('ftpuploader')


class ITJobPostLink:
    title: str
    href: str

    def __init__(self, title, href):
        self.title = title
        self.href = href


def log_response_failure_information(status_code):
    logger.warning(f'Error fetching the given page, https://http.cat/{status_code}')
    if status_code == 503:
        logger.warning(
            f'it.jobs.bg has blacklisted the user agent. Try with another popular one: '
            f'https://techblog.willshouse.com/2012/01/03/most-common-user-agents/')
    exit()


def find_it_jobs():
    try:
        it_jobs_response = requests.get(IT_JOBS_SCRAPING_URL, headers=headers)
        it_jobs_response_status_code = it_jobs_response.status_code
        if it_jobs_response_status_code != 200:
            log_response_failure_information(it_jobs_response_status_code)
        else:
            it_jobs_html_text = it_jobs_response.text
            beautiful_soup = BeautifulSoup(it_jobs_html_text, 'lxml')
            # print(beautiful_soup.prettify())
            available_it_job_posts = beautiful_soup.find_all('div', class_='mdc-layout-grid')

            it_jobs_posts_links_list = []

            for it_job_post in available_it_job_posts:
                it_job_post_tag = it_job_post.a
                it_job_post_title = it_job_post_tag['title']
                it_job_post_href = it_job_post_tag['href']
                it_job_post_link = ITJobPostLink(it_job_post_title, it_job_post_href)
                it_jobs_posts_links_list.append(it_job_post_link)

            it_jobs_posts_list = []

            print('IT job posts with links')
            for it_job_post_link in it_jobs_posts_links_list:
                print(f'{it_job_post_link.title} - {it_job_post_link.href}')
                single_job_post_response = requests.get(it_job_post_link.href, headers=headers)
                print(single_job_post_response)
                single_job_post_response_status_code = single_job_post_response.status_code
                if it_jobs_response_status_code != 200:
                    log_response_failure_information(single_job_post_response_status_code)
                else:
                    single_job_post_html_text = single_job_post_response.text
                    new_beautiful_soup = BeautifulSoup(single_job_post_html_text, 'lxml')
                    print(new_beautiful_soup.prettify())
    except Exception as exception:
        logger.error(str(exception))


if __name__ == '__main__':
    find_it_jobs()
    base_waiting_time = 10
    print(f'Waiting {base_waiting_time} minutes...')
    time.sleep(base_waiting_time * 60)
