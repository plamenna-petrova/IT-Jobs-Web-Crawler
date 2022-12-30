from datetime import datetime


class ITJobPost:
    posting_date: datetime
    job_title: str
    company_name: str
    work_details: set()
    technologies: set()
    company_profile_address: str
    company_details: set()
    more_jobs_from_company_address: str

    def __init__(
            self,
            posting_date,
            job_title,
            company_name,
            work_details,
            technologies,
            company_profile_address,
            company_details,
            more_jobs_from_company_address
    ):
        self.posting_date = posting_date
        self.job_title = job_title
        self.company_name = company_name
        self.work_details = work_details
        self.technologies = technologies
        self.company_profile_address = company_profile_address
        self.company_details = company_details
        self.more_jobs_from_company_address = more_jobs_from_company_address
