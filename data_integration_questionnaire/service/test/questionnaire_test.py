

from data_integration_questionnaire.model.questionnaire import Questionnaire, merge_questionnaires
from data_integration_questionnaire.service.test.questionnaire_factory import create_questionnaire_list


def test_questionnaire_html():
    merged: Questionnaire = merge_questionnaires(create_questionnaire_list())
    html = merged.to_html()
    assert '<table>' in html