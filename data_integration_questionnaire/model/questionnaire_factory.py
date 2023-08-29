from data_integration_questionnaire.model.questionnaire import (
    QuestionAnswer,
    Questionnaire,
)

def questionnaire_factory() -> Questionnaire:
    question_answers = []
    questions = [
        "Does your organization support an event driven architecture for data integration?",
        "Does your organization take more than 3 weeks for data integration between 2 systems?",
        "Would you like to know more about capabilities that would cut down your integration cost and time spend for integration by 50%?",
        "Does your organization export data lineage to data catalog?",
        "How many integration engineers does your team have?",
        "What is the scope of integration? What is the total count of source systems? What is the total count of the destination systems?",
        "Does your organization promote use of open source for data integration?"
    ]
    for q in questions:
        question_answers.append(QuestionAnswer(question=q, answer=""))
    return Questionnaire(questions=question_answers)


if __name__ == "__main__":
    questions = questionnaire_factory().questions
    for question in questions:
        print(type(question))
