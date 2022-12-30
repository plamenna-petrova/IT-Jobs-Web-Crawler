import csv
import os

from datetime import datetime

import requests

from bs4 import BeautifulSoup

import time

import logging

from it_job_post_link import ITJobPostLink

from it_job_post import ITJobPost

IT_JOBS_SCRAPING_URL = 'https://www.jobs.bg/en/front_job_search.php?subm=1&categories%5B%5D=56&domains%5B%5D=5&domains%5B%5D=3&domains%5B%5D=2&domains%5B%5D=1&salary_from=1'


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US'
}

logger = logging.getLogger('ftpuploader')


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


def get_timestamp_arguments_for_filename(datetime_result: datetime) -> tuple[str, str, str, str, str, str]:
    return(
        str(datetime_result.day) if (datetime_result.day >= 10) else f'{0}{str(datetime_result.day)}',
        str(datetime_result.month) if (datetime_result.month >= 10) else f'{0}{str(datetime_result.month)}',
        str(datetime_result.year),
        str(datetime_result.hour) if (datetime_result.hour >= 10) else f'{0}{str(datetime_result.hour)}',
        str(datetime_result.minute) if (datetime_result.minute >= 10) else f'{0}{str(datetime_result.minute)}',
        str(datetime_result.second) if (datetime_result.second >= 10) else f'{0}{str(datetime_result.second)}'
     )


def export_job_posts_scraping_results_to_csv(
        datetime_for_csv_file_creation: datetime,
        csv_headers: list[str],
        it_jobs_posts_list: list[ITJobPost]
):
    try:
        if input().upper() == 'Y':
            csv_file_name_arguments = get_timestamp_arguments_for_filename(datetime_for_csv_file_creation)
            csv_file_name = '''ITJobPostsScrapingResults_{0}.{1}.{2}_{3}_{4}_{5}.csv'''.format(*csv_file_name_arguments)
            csv_data_entries = []
            for it_job_post in it_jobs_posts_list:
                tabulation_string = '\t'
                work_details_string = tabulation_string.join(it_job_post.work_details)
                technologies_string = tabulation_string.join(it_job_post.technologies)
                company_details_string = tabulation_string.join(it_job_post.company_details)
                csv_data_entries.append({
                    'posting_date': it_job_post.posting_date,
                    'job_title': it_job_post.job_title,
                    'company_name': it_job_post.company_name,
                    'work_details': f'{work_details_string}',
                    'technologies': f'{technologies_string}',
                    'company_profile_address': it_job_post.company_profile_address,
                    'company_details': f'{company_details_string}',
                    'more_jobs_from_company_address': it_job_post.more_jobs_from_company_address
                })
            with open(csv_file_name, 'w', encoding='cp1251', newline='') as csv_file:
                csv_file_writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
                csv_file_writer.writeheader()
                csv_file_writer.writerows(csv_data_entries)
                csv_file.close()
    except Exception as exception:
        logger.error(str(exception))


def export_job_posts_scraping_results_to_txt_files(
        datetime_for_txt_files_creation: datetime,
        it_job_posts_list: list[ITJobPost]
):
    try:
        if input().upper() == 'Y':
            txt_files_storage_folder_arguments = get_timestamp_arguments_for_filename(datetime_for_txt_files_creation)
            txt_files_storage_directory_name = '''ITJobPostsScrapingResults_{0}.{1}.{2}_{3}_{4}_{5}'''\
                .format(*txt_files_storage_folder_arguments)
            os.makedirs(txt_files_storage_directory_name)
            new_line_string = '\n'
            for i, it_job_post in enumerate(it_job_posts_list):
                with open(f'{txt_files_storage_directory_name}/{i}.txt', 'w') as txt_file_writer:
                    txt_file_writer.write(f'IT Job Post Information: {new_line_string}')
                    txt_file_writer.write(f'Posting Date: {it_job_post.posting_date} {new_line_string}')
                    txt_file_writer.write(f'Job Title: {it_job_post.job_title} {new_line_string}')
                    txt_file_writer.write(f'Company Name: {it_job_post.company_name} {new_line_string}')
                    txt_file_writer.write(f'Work Details: ')
                    if it_job_post.work_details:
                        for j, work_details_entry in enumerate(it_job_post.work_details):
                            if work_details_entry != '':
                                txt_file_writer.write(f'{3 * " "} #{j + 1} {work_details_entry} {new_line_string}')
                    else:
                        txt_file_writer.write(f'Unfortunately, no work details were found! {new_line_string}')
                    txt_file_writer.write(f'Needed skills: {new_line_string}')
                    if it_job_post.technologies:
                        for t, technologies_entry in enumerate(it_job_post.technologies):
                            if technologies_entry != '':
                                txt_file_writer.write(f'{3 * " "} #{t + 1} {technologies_entry} {new_line_string}')
                    else:
                        txt_file_writer.write(f'No skills found that are required for this job! {new_line_string}')
                    txt_file_writer\
                        .write(f'Company Profile: {it_job_post.company_profile_address.strip()} {new_line_string}')
                    txt_file_writer.write(f'Company Details: {new_line_string}')
                    if it_job_post.company_details:
                        for c, company_details_entry in enumerate(it_job_post.company_details):
                            if company_details_entry != '':
                                txt_file_writer.write(f'{3 * " "} #{c + 1} {company_details_entry} {new_line_string}')
                    else:
                        txt_file_writer.write(f'Unfortunately, no company details were found! {new_line_string}')
                    txt_file_writer.write(f'More jobs from {it_job_post.company_name}: {it_job_post.more_jobs_from_company_address} {new_line_string}')
                    txt_file_writer.write('\n' * 2)
    except Exception as exception:
        logger.error(str(exception))


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

            print('Do you wish to export the data? Y/N')
            file_export_headers = [
                'posting_date',
                'job_title',
                'company_name',
                'work_details',
                'technologies',
                'company_profile_address',
                'company_details',
                'more_jobs_from_company_address'
            ]
            if input().upper() == 'Y':
                print('Do you want the data to be exported to csv?')
                current_datetime_for_csv_file_creation = datetime.now()
                export_job_posts_scraping_results_to_csv(
                    current_datetime_for_csv_file_creation,
                    file_export_headers,
                    it_jobs_posts_list
                )
                print('Do you want the data to be exported to txt file?')
                current_datetime_for_txt_files_creation = datetime.now()
                export_job_posts_scraping_results_to_txt_files(
                    current_datetime_for_txt_files_creation,
                    it_jobs_posts_list
                )
            else:
                print('The data is not exported at all, as you wished.')
    except Exception as exception:
        logger.error(str(exception))


if __name__ == '__main__':
    find_it_jobs()
    base_waiting_time = 10
    print(f'Waiting {base_waiting_time} minutes...')
    time.sleep(base_waiting_time * 60)
