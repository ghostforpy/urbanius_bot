from .prepares import (
    prepare_ask_phone,
    prepare_ask_about,
    # prepare_ask_fio,
    prepare_ask_birthday,
    # prepare_ask_email,
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
    prepare_job_region
)
from .utils import counter
from .saveuser import end_registration

# Шаги диалога
# SITE->BUSINESS_BRANCH->MONEY_TURNOVER->TAGS->BUISNESS_NEEDS->USER_BENEFIT->RESEDENT_URBANIUS_CLUB->
# BUSINESS_CLUB_MEMBER->HOBBY->FIND_OUT->SOCIAL_NETS->REFERRER->PHONE->PHOTO->END
# EMAIL not need
#APROVAL,COMPANY,CITI,JOB,FIO,BIRHTDAY,ABOUT,SITE,PHONE = range(9)
step_iterator = counter(1)
STEPS = {
    "USERNAME": {
        "step": step_iterator.current,
        "prepare": prepare_ask_lastname,
        "next": next(step_iterator)
    },
    "LASTNAME": {
        "step": step_iterator.current,
        "prepare": prepare_ask_surname,
        "next": next(step_iterator)
    },
    "SURNAME": {
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
        "prepare": prepare_resident_urbanius_club,
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
        "prepare": "",
        # "prepare": prepare_ask_photo,
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

    # "BUSINESS_BRANCH": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_money_turnover,
    #     "next": next(step_iterator)
    # },
    # "MONEY_TURNOVER": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_tags,
    #     "next": next(step_iterator)
    # },
#     "TAGS": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_business_needs,
    #     "next": next(step_iterator)
    # },
    # "BUSINESS_NEEDS": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_user_benefit,
    #     "next": next(step_iterator)
    # },
    # "USER_BENEFIT": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_resident_urbanius_club,
    #     "next": next(step_iterator)
    # },
    # "RESIDENT_URBANIUS_CLUB": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_businesss_club_member,
    #     "next": next(step_iterator)
    # },
    # "BUSINESS_CLUB_MEMBER": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_hobby,
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
    # "PHONE": {
    #     "step": step_iterator.current,
    #     "prepare": "",
    #     # "prepare": prepare_ask_photo,
    #     "next": end_registration
    #     # "next": next(step_iterator)
    # },
    # "PHOTO": {
    #     "step": step_iterator.current,
    #     "prepare": "",
    #     "next": end_registration
    # },
}