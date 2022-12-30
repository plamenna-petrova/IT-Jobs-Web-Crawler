import enum

import requests

from bs4 import BeautifulSoup

import time

import logging

from it_job_post_link import ITJobPostLink

from it_job_post import ITJobPost

from file_export_functions import *


IT_JOBS_SCRAPING_URL = 'https://www.jobs.bg/en/front_job_search.php?subm=1&categories%5B%5D=56&domains%5B%5D=5&domains%5B%5D=3&domains%5B%5D=2&domains%5B%5D=1&salary_from=1'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US'
}

logger = logging.getLogger('ftpuploader')

wanted_seniority_level = ''

with_file_export_options = False


def log_response_failure_information(status_code: int):
    logger.warning(f'Error fetching the given page, https://http.cat/{status_code}')
    if status_code == 503:
        logger.warning(
            f'it.jobs.bg has blacklisted the user agent. Try with another popular one: '
            f'https://techblog.willshouse.com/2012/01/03/most-common-user-agents/')


def get_single_it_job_post(soup: BeautifulSoup) -> ITJobPost:
    try:
        it_job_post_information_container = soup.find('div', class_='view-extra')
        it_job_posting_date_container = it_job_post_information_container.find('div', class_='date')
        if it_job_posting_date_container is not None:
            it_job_posting_date = it_job_posting_date_container.string.split(',')[0].strip()
        else:
            it_job_posting_date = None
        it_job_title_span = it_job_post_information_container.find('span', class_='bold')
        if it_job_title_span is not None:
            it_job_main_details_container = it_job_title_span.parent
            it_job_main_details = it_job_main_details_container.text.strip().split(',')
            it_job_title = it_job_main_details[0].strip()
            it_job_company = it_job_main_details[len(it_job_main_details) - 1].strip()
        else:
            it_job_title = 'Unknown Job Title'
            it_job_company = 'Unknown Company'
        it_job_work_details_container = it_job_main_details_container.find_next_sibling('div', class_='options')
        it_job_work_details_entries = []
        if it_job_work_details_container is not None:
            it_job_work_details_spans = it_job_work_details_container.select('li span')
            for it_job_work_details_span in it_job_work_details_spans:
                it_job_work_details_entries.append(it_job_work_details_span.text.strip())
        it_job_tech_stack_container = it_job_work_details_container.find_next_sibling('div', class_='skills')
        it_job_tech_stack_entries = []
        if it_job_tech_stack_container is not None:
            it_job_tech_stack_li_tags = it_job_tech_stack_container.find_all('li')
            for it_job_tech_stack_li in it_job_tech_stack_li_tags:
                it_job_tech_stack_entries.append(it_job_tech_stack_li.text.strip())
        it_job_company_details_container = soup.find('div', class_='margin-medium job-view-right-column no-print')
        it_job_company_details_entries = []
        if it_job_company_details_container is not None:
            it_job_company_details_ul = it_job_company_details_container.find('ul', class_='card-icon-list pt-8')
            it_job_company_li_tags = it_job_company_details_ul.findAll('li')
            for it_job_company_details_li in it_job_company_li_tags:
                it_job_company_details_icon = it_job_company_details_li.find('i')
                it_job_company_details_icon.decompose()
                it_job_company_details_entries.append(it_job_company_details_li.text.strip())
            it_job_company_links = it_job_company_details_container.find_all('a', class_='mdc-button '
                                                                                         'mdc-button--icon-leading '
                                                                                         'button-small theme-link')
            it_job_company_profile_address = it_job_company_links[1].get('href')
            it_job_company_more_jobs_address = it_job_company_links[0].get('href')
        else:
            it_job_company_profile_address = 'Unknown company profile address'
            it_job_company_more_jobs_address = 'Unknown company more jobs address'
        it_job_post_entry = ITJobPost(it_job_posting_date,
                                      it_job_title,
                                      it_job_company,
                                      it_job_work_details_entries,
                                      it_job_tech_stack_entries,
                                      it_job_company_profile_address,
                                      it_job_company_details_entries,
                                      it_job_company_more_jobs_address)
        return it_job_post_entry
    except AttributeError as attributeError:
        logger.error(str(attributeError))


def print_it_job_post_information(it_job_post: ITJobPost):
    print(f'IT Job Post Information: ')
    print(f'Posting Date:', f'{it_job_post.posting_date}' if it_job_post.posting_date is not None else f'Unknown')
    print(f'Job Title: {it_job_post.job_title}')
    print(f'Company Name: {it_job_post.company_name}')
    print(f'Work Details: ')
    if it_job_post.work_details:
        for index, work_details_entry in enumerate(it_job_post.work_details):
            if work_details_entry != '':
                print(f'{3 * " "} #{index + 1} {work_details_entry}')
    else:
        print(f'Unfortunately, no work details were found!')
    print(f'Needed skills: ')
    if it_job_post.technologies:
        for index, technologies_entry in enumerate(it_job_post.technologies):
            if technologies_entry != '':
                print(f'{3 * " "} #{index + 1} {technologies_entry}')
    else:
        print(f'No skills found that are required for this job!')
    print(f'Company Profile: {it_job_post.company_profile_address.strip()}')
    print(f'Company Details: ')
    if it_job_post.company_details:
        for index, company_details_entry in enumerate(it_job_post.company_details):
            if company_details_entry != '':
                print(f'{3 * " "} #{index + 1} {company_details_entry}')
    else:
        print('Unfortunately, no company details were found!')
    print(f'More jobs from {it_job_post.company_name}: {it_job_post.more_jobs_from_company_address}')
    print('\n' * 2)


def find_it_jobs():
    try:
        it_jobs_response = requests.get(IT_JOBS_SCRAPING_URL, headers=headers)
        it_jobs_response_status_code = it_jobs_response.status_code
        if it_jobs_response_status_code != 200:
            log_response_failure_information(it_jobs_response_status_code)
            exit()
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
                if wanted_seniority_level.lower() in it_job_post_title.lower():
                    it_job_post_link = ITJobPostLink(it_job_post_title, it_job_post_href)
                    it_jobs_posts_links_list.append(it_job_post_link)

            it_jobs_posts_list = []

            print('IT job posts with links \n')
            for it_job_post_link in it_jobs_posts_links_list:
                print(f'Link to IT Job Post - {it_job_post_link.href}')
                single_job_post_response = requests.get(it_job_post_link.href, headers=headers)
                single_job_post_response_status_code = single_job_post_response.status_code
                if it_jobs_response_status_code != 200:
                    log_response_failure_information(single_job_post_response_status_code)
                    break
                else:
                    single_job_post_html_text = single_job_post_response.text
                    new_beautiful_soup = BeautifulSoup(single_job_post_html_text, 'lxml')
                    # print(new_beautiful_soup.prettify())
                    current_it_job_post = get_single_it_job_post(new_beautiful_soup)
                    if current_it_job_post.job_title == it_job_post_link.title:
                        print_it_job_post_information(current_it_job_post)
                        it_jobs_posts_list.append(current_it_job_post)
                    else:
                        print(f'Found mismatch between the title of the job post link and the job title itself!')

            if with_file_export_options:
                print('Data export initiated...')
                print('')
                print('Exporting data to a csv file')
                current_datetime_for_csv_file_creation = datetime.now()
                export_job_posts_scraping_results_to_csv(
                    current_datetime_for_csv_file_creation,
                    it_jobs_posts_list
                )
                print('CSV export finished successfully!')
                print('')
                print('Exporting data txt files within a subdirectory')
                current_datetime_for_txt_files_creation = datetime.now()
                export_job_posts_scraping_results_to_txt_files(
                    current_datetime_for_txt_files_creation,
                    it_jobs_posts_list
                )
                print('TXT export finished successfully!')
                print('')
                print('Exporting data to a pdf file')
                current_datetime_for_txt_files_creation = datetime.now()
                export_job_post_scraping_results_to_pdf(
                    current_datetime_for_txt_files_creation,
                    it_jobs_posts_list
                )
                print('PDF export finished successfully!')
                print('')
    except Exception as exception:
        logger.error(str(exception))


if __name__ == '__main__':
    print('Do you want to filter the results, based on seniority level Y/N')
    if input().upper() == 'Y':
        print('Enter the wanted seniority level: ')
        print('Options: ')
        print('1 - Junior')
        print('2 - Middle')
        print('3 - Senior')
        wanted_seniority_level_input = int(input('>'))
        print('The user input was')
        print(wanted_seniority_level_input)
        if wanted_seniority_level_input == 1:
            wanted_seniority_level = 'Junior'
        elif wanted_seniority_level_input == 2:
            wanted_seniority_level = 'Mid'
        elif wanted_seniority_level_input == 3:
            wanted_seniority_level = 'Senior'
        else:
            print(f'The seniority level was not given a proper format!')
        if wanted_seniority_level != '':
            print(wanted_seniority_level)
            print(f'Filtering out results for {wanted_seniority_level} positions...')
            print('')
        else:
            print(f'Fetching all of the results!')
    print('Do you wish the data to be exported in several file formats after each scraping session Y/N')
    if input().upper() == 'Y':
        with_file_export_options = True
        print('The data will be exported to csv, txt and pdf files!')
    else:
        print('The scraping results data won\'t be saved at all, as you wished...')
    while True:
        find_it_jobs()
        base_waiting_time = 10
        print(f'Waiting {base_waiting_time} minutes...')
        time.sleep(base_waiting_time * 60)
        # less time for data fetching for testing purposes
        # time.sleep(base_waiting_time)
