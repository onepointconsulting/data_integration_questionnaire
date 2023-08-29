from typing import List

from data_integration_questionnaire.log_init import logger

from data_integration_questionnaire.service.test.questionnaire_factory import (
    create_questionnaire_on_top,
    create_questionnaire_slightly_behind,
)

from data_integration_questionnaire.service.advice_service import create_match_profile_chain_pydantic, extract_advices

def give_advice_slightly_behind():
    questionnaire = create_questionnaire_slightly_behind()
    process_advice(questionnaire)


def give_advice_super_nerd():
    questionnaire = create_questionnaire_on_top()
    process_advice(questionnaire)


def process_advice(questionnaire: str) -> List[str]:
    chain = create_match_profile_chain_pydantic()
    res = chain.run(questionnaire)
    advices = extract_advices(res)
    advice_amount = len(advices)
    logger.info(f"You have {advice_amount} advices")
    for advice in advices:
        logger.info(advice)



if __name__ == "__main__":
    give_advice_slightly_behind()
    print()
    print()
    give_advice_super_nerd()
    