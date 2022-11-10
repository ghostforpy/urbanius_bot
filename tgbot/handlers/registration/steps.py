from .prepares import (
    prepare_ask_phone,
    prepare_ask_citi,
    prepare_ask_company,
    prepare_ask_job,
    prepare_ask_site,
    prepare_ask_lastname,
    prepare_ask_surname,
    prepare_approval,
    prepare_resident_urbanius_club,
    prepare_business_club_member,
    prepare_deep_link,
    prepare_job_region,
    prepare_company_turnover,
    prepare_company_number_of_employees,
    prepare_company_business_needs,
    prepare_company_business_benefits,
    prepare_company_business_branches,
    prepare_ask_photo,
    prepare_ask_first_name,
    prepare_tags
)
from .utils import counter
from .saveuser import end_registration

step_iterator = counter(1)
STEPS = {
    "FIRSTNAME": {
        "step": step_iterator.current,
        "prepare": prepare_ask_surname,
        "self_prepare": prepare_ask_first_name,
        "next": next(step_iterator)
    },
    "SURNAME": { # отчество
        "step": step_iterator.current,
        "prepare": prepare_ask_lastname,
        "next": next(step_iterator)
    },
    "LASTNAME": {
        "step": step_iterator.current,
        "prepare": prepare_ask_citi,
        "next": next(step_iterator)
    },
    "CITI": {
        "step": step_iterator.current,
        "prepare": prepare_ask_company,
        "next": next(step_iterator)
    },
    "COMPANY": {
        "step": step_iterator.current,
        "prepare": prepare_ask_job,
        "next": next(step_iterator)
    },
    "JOB": {
        "step": step_iterator.current,
        "prepare": prepare_ask_site,
        "next": next(step_iterator)
    },
    "SITE": {
        "step": step_iterator.current,
        "prepare": prepare_job_region,
        "next": next(step_iterator)
    },
    "JOB_REGION": {
        "step": step_iterator.current,
        "prepare": prepare_company_turnover,
        "next": next(step_iterator)
    },
    "COMPANY_TURNOVER": {
        "step": step_iterator.current,
        "prepare": prepare_company_number_of_employees,
        "self_prepare": prepare_company_turnover,
        "next": next(step_iterator)
    },
    "COMPANY_NUMBER_OF_EMPLOYESS": {
        "step": step_iterator.current,
        "prepare": prepare_company_business_branches,
        "self_prepare": prepare_company_number_of_employees,
        "next": next(step_iterator)
    },
    "COMPANY_BUSINESS_BRANCHES": {
        "step": step_iterator.current,
        "prepare": prepare_company_business_needs,
        "self_prepare": prepare_company_business_branches,
        "next": next(step_iterator)
    },
    "COMPANY_BUSINESS_NEEDS": {
        "step": step_iterator.current,
        "prepare": prepare_tags,
        "self_prepare": prepare_company_business_needs,
        "next": next(step_iterator)
    },
    "TAGS": {
        "step": step_iterator.current,
        "prepare": prepare_company_business_benefits,
        "self_prepare": prepare_tags,
        "next": next(step_iterator)
    },
    "COMPANY_BUSINESS_BENEFITS": {
        "step": step_iterator.current,
        "prepare": prepare_resident_urbanius_club,
        "self_prepare": prepare_company_business_benefits,
        "next": next(step_iterator)
    },
    "RESIDENT_URBANIUS_CLUB": {
        "step": step_iterator.current,
        "prepare": prepare_business_club_member,
        "next": next(step_iterator)
    },
    "BUSINESS_CLUB_MEMBER": {
        "step": step_iterator.current,
        "prepare": prepare_deep_link,
        "next": next(step_iterator)
    },
    "DEEP_LINK": {
        "step": step_iterator.current,
        "prepare": prepare_approval,
        "next": next(step_iterator)
    },
    "APROVAL": {
        "step": step_iterator.current,
        "prepare": prepare_ask_phone,
        "next": next(step_iterator)
    },
    "PHONE": {
        "step": step_iterator.current,
        "prepare": prepare_ask_photo,
        "self_prepare": prepare_ask_phone,
        "next": next(step_iterator)
    },
    "PHOTO": {
        "step": step_iterator.current,
        "prepare": "",
        "self_prepare": prepare_ask_photo,
        "next": end_registration
        # "next": next(step_iterator)
    },


    # "FIO": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_birthday,
    #     "next": next(step_iterator)
    # },
    # "BIRTHDAY": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_about,
    #     "next": next(step_iterator)
    # },
    # "ABOUT": {
    #     "step": step_iterator.current,
    #     "prepare": ,
    #     "next": next(step_iterator)
    # },





    # "HOBBY": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_find_out,
    #     "next": next(step_iterator)
    # },
    # "FIND_OUT": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_socials_nets,
    #     "next": next(step_iterator)
    # },
    # "SOCIAL_NETS": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_phone,
    #     "next": next(step_iterator)
    # },
}