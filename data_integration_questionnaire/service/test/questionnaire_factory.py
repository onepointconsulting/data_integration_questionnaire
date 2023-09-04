from typing import List

from data_integration_questionnaire.model.questionnaire import QuestionAnswer, Questionnaire


def create_questionnaire_full_on_beginner() -> str:
    return """
Does your organization support an event driven architecture for data integration?
No. To be honest I do not know what event driven architecture is. Can you enlighten me?

Does your organization take more than 3 weeks for data integration between 2 systems?
Yes, we are always behind schedule.

Would you like to know more about capabilities that would cut down your integration cost and time spend for integration by 50%?
Yes, I am really interested about that.

Does your organization export data lineage to data catalog?
Nope, not yet, but we are very interested.

How many integration engineers does your team have?
Just 8

What is the scope of integration? What is the total count of source systems? What is the total count of the destination systems?
We have right now 6 source systems, including an Oracle DB, an SAP system for our raw materials, an HR system, a billing system, a customer database and a calendaring system.

Does your organization promote use of open source for data integration?
Not at the moment. We have bought into Oracle, SAP and Sage to help us. So we have not looked at anything else as of now. But we are open to new ideas.
"""


def create_questionnaire_slightly_behind() -> str:
    return """
Does your organization support an event driven architecture for data integration?
Yes, it does, but I would like to improve it.

Does your organization take more than 3 weeks for data integration between 2 systems?
Oh, not really. Most of the time it takes much longer than that.

Would you like to know more about capabilities that would cut down your integration cost and time spend for integration by 50%?
Yes, I am really interested about that.

Does your organization export data lineage to data catalog?
Nope, not yet, but we are very interested.

How many integration engineers does your team have?
Just 8

What is the scope of integration? What is the total count of source systems? What is the total count of the destination systems?
We have right now 6 source systems, including an Oracle DB, an SAP system for our raw materials, an HR system, a billing system, a customer database and a calendaring system.

Does your organization promote use of open source for data integration?
Not at the moment. We have bought into Oracle and SAP to help us. So we have not looked at anything else as of now. But we are open to new ideas.
"""

def create_questionnaire_on_top() -> str:
    return """
Does your organization support an event driven architecture for data integration?
Yes, it does. We have a fully event driven architecture.

Does your organization take more than 3 weeks for data integration between 2 systems?
Nope, we are super efficient and are always on time.

Would you like to know more about capabilities that would cut down your integration cost and time spend for integration by 50%?
No, I am really satisfied with what I have.

Does your organization export data lineage to data catalog?
Yes, we do that all the time.

How many integration engineers does your team have?
We have more than 100 data engineers.

What is the scope of integration? What is the total count of source systems? What is the total count of the destination systems?
We have right now 6 source systems, including an Oracle DB, an SAP system for our raw materials, an HR system, a billing system, a customer database and a calendaring system.

Does your organization promote use of open source for data integration?
We do promote the usage of Open source as much as we can.
"""

def create_questionnaire_list() -> List[Questionnaire]:
    questionnaire1 = Questionnaire(questions=[
        QuestionAnswer(
            question="What steps have you taken to implement no code/low code tools for data integration in your organization? How has this impacted your organization's agility and ability to consume data downstream?",
            answer = {'createdAt': '', 'content': 'We are using Informatica for our ETL processes. Informatica standardizes the ETL processes and also cuts down the development time.'},
            image='',
            image_alt='',
            image_title=''
        )
    ])
    questionnaire2 = Questionnaire(questions=[
        QuestionAnswer(
            question="How are you currently utilizing data catalogs and data lineage to improve data literacy, ensure data accuracy, and manage business change in your organization?",
            answer = {'createdAt': '', 'content': 'We are right now not using data catalogs. We are only documenting the processes using JIRA Confluence as some sort of Wiki.'},
            image='',
            image_alt='',
            image_title=''
        )
    ])
    return [questionnaire1, questionnaire2]
