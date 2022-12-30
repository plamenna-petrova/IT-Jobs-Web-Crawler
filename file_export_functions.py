import csv

import os
from base64 import encode

from datetime import datetime

from crawler import logger

from it_job_post import ITJobPost

from fpdf import FPDF


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
                tabulation_character = '\t'
                work_details_string = tabulation_character.join(it_job_post.work_details)
                technologies_string = tabulation_character.join(it_job_post.technologies)
                company_details_string = tabulation_character.join(it_job_post.company_details)
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
            new_line_character = '\n'
            for i, it_job_post in enumerate(it_job_posts_list):
                with open(f'{txt_files_storage_directory_name}/{i}.txt', 'w') as txt_file_writer:
                    txt_file_writer.write(f'IT Job Post Information: {new_line_character}')
                    txt_file_writer.write(f'Posting Date: {it_job_post.posting_date} {new_line_character}')
                    txt_file_writer.write(f'Job Title: {it_job_post.job_title} {new_line_character}')
                    txt_file_writer.write(f'Company Name: {it_job_post.company_name} {new_line_character}')
                    txt_file_writer.write(f'Work Details: {new_line_character}')
                    if it_job_post.work_details:
                        for j, work_details_entry in enumerate(it_job_post.work_details):
                            if work_details_entry != '':
                                txt_file_writer.write(f'{3 * " "} #{j + 1} {work_details_entry} {new_line_character}')
                    else:
                        txt_file_writer.write(f'Unfortunately, no work details were found! {new_line_character}')
                    txt_file_writer.write(f'Needed skills: {new_line_character}')
                    if it_job_post.technologies:
                        for t, technologies_entry in enumerate(it_job_post.technologies):
                            if technologies_entry != '':
                                txt_file_writer.write(f'{3 * " "} #{t + 1} {technologies_entry} {new_line_character}')
                    else:
                        txt_file_writer.write(f'No skills found that are required for this job! {new_line_character}')
                    txt_file_writer\
                        .write(f'Company Profile: {it_job_post.company_profile_address.strip()} {new_line_character}')
                    txt_file_writer.write(f'Company Details: {new_line_character}')
                    if it_job_post.company_details:
                        for c, company_details_entry in enumerate(it_job_post.company_details):
                            if company_details_entry != '':
                                txt_file_writer.write(f'{3 * " "} #{c + 1} {company_details_entry} {new_line_character}')
                    else:
                        txt_file_writer.write(f'Unfortunately, no company details were found! {new_line_character}')
                    txt_file_writer.write(f'More jobs from {it_job_post.company_name}: {it_job_post.more_jobs_from_company_address} {new_line_character}')
                    txt_file_writer.write('\n' * 2)
    except Exception as exception:
        logger.error(str(exception))


def export_job_post_scraping_results_to_pdf(
        datetime_for_pdf_file_creation: datetime,
        it_job_posts_list: list[ITJobPost]
):
    try:
        if input().upper() == 'Y':
            pdf_table_column_names = \
                (
                 "Title",
                 "Technologies",
                 "Company Profile Address",
                 )
            pdf_data = ()
            for it_job_post in it_job_posts_list:
                technologies_string = ','.join(it_job_post.technologies)
                if technologies_string == '':
                    technologies_string = 'No skills found that are required for this job!'
                pdf_data_entry = (
                    it_job_post.job_title,
                    technologies_string,
                    it_job_post.company_profile_address,
                )
                pdf_data = pdf_data + (pdf_data_entry,)
                print(f'PDF Data: ')
                print(str(pdf_data))
            pdf_file = FPDF('L', 'mm', 'A4')
            pdf_file.set_font(family='Arial', style='B', size=5)
            pdf_file.add_page()
            line_height = pdf_file.font_size * 2.7
            column_width = pdf_file.epw / 3
            for pdf_column_name in pdf_table_column_names:
                pdf_file.cell(column_width, line_height, pdf_column_name, border=1)
            pdf_file.ln(line_height)
            for row in pdf_data:
                for datum in row:
                    pdf_file.cell(column_width, line_height, datum, border=1)
                pdf_file.ln(line_height)
            pdf_file_name_arguments = get_timestamp_arguments_for_filename(datetime_for_pdf_file_creation)
            pdf_file_name = '''ITJobPostsScrapingResults_{0}.{1}.{2}_{3}_{4}_{5}.pdf'''.format(*pdf_file_name_arguments)
            pdf_file.output(pdf_file_name)
    except Exception as exception:
        logger.error(str(exception))

