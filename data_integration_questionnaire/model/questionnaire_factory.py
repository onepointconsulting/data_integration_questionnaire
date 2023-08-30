from data_integration_questionnaire.model.questionnaire import (
    QuestionAnswer,
    Questionnaire,
)


def questionnaire_factory() -> Questionnaire:
    question_answers = []
    questions = [
        {
            "text": "Does your organization support an event driven architecture for data integration?"
        },
        {
            "text": "Does your organization take more than 3 weeks for data integration between 2 systems?"
        },
        {
            "text": "Would you like to know more about capabilities that would cut down your integration cost and time spend for integration by 50%?"
        },
        {"text": "Does your organization export data lineage to data catalog?"},
        {"text": "How many integration engineers does your team have?"},
        {
            "text": "What is the scope of integration? What is the total count of source systems? What is the total count of the destination systems?"
        },
        {
            "text": "Does your organization promote use of open source for data integration?"
        },
    ]
    for q in questions:
        question_answer = QuestionAnswer(question=q["text"], answer="", image=None, image_alt=None, image_title=None)
        if 'image_path' in q and 'image_alt' in q and 'image_title' in q:
            question_answer.image = q['image_path']
            question_answer.image_title = q['image_title']
            question_answer.image_alt = q['image_alt']
        question_answers.append(question_answer)
    return Questionnaire(questions=question_answers)


if __name__ == "__main__":
    questionnaire = questionnaire_factory()
    print(questionnaire)
