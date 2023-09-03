from typing import Tuple, List



def create_initial_quizz() -> Tuple[List[str], List[str]]:
    initial_quizz = [
        "What tools are you currently using for data integration and how are they helping you achieve no-code/low-code integration?",
        "How are you currently capturing and managing metadata as data moves across multiple systems? Are you using a data catalog to improve data literacy and ensure data accuracy?",
        "Are you using Change Data Capture (CDC) to minimize data latency and provide timely transparency to business processes?",
        "What open-source tools are you using for ETL operations or as an abstraction layer on top of your existing compute engines?",
        "Are you considering a unified platform for data integration to simplify maintainability and deliver a more consistent and reliable view of your data across disparate applications?",
    ]
    answers = [
        "Right now we are not using Talend Open Studio for some ETL jobs, but we are using lots of Python and Lua scripts to achieve for out ETL jobs.",
        "At the moment we are only using JIRA connfluence to document the ETL flows. This is however not a proper data catalog. So we will have to work on that.",
        "CDC is currently being only partially used. Most of our jobs are still batch based.",
        "We are using Talend Open Studio, but that is about it right now. We have used Informatica in the past, but that was a bit too expensive.",
        "We know that Talend offers services in this area and we find this interesting. But is there not a risk of a vendor lock in once you go for these platforms?"
    ]
    return initial_quizz, answers


def create_secondary_quizz() -> Tuple[List[str], List[str]]:
    quizz = [
        "Considering your current use of Python and Lua scripts for ETL jobs, have you evaluated the potential benefits of using more no-code/low-code tools, such as cloud-based connectors, to increase your organization's agility in integrating systems?", 
        'You mentioned that you are currently using JIRA Confluence to document ETL flows, but not a proper data catalog. Have you considered implementing a data catalog to improve data literacy, ensure data accuracy, and manage business change more effectively?', 
        'You mentioned that you are only partially using Change Data Capture (CDC) and most of your jobs are still batch-based. Have you considered fully implementing CDC to minimize data latency and provide more timely transparency to your business processes?'
    ]
    answers = [
        "To be honest, I know that low code tools allow teams to be more productive. So definitely using low code tools is definitely on the cards.",
        "Yes, I am definitely interested in a proper data catalog.",
        "Yes, that is something that we can improve. What recommendation can you make to me?"
    ]
    return quizz, answers

if __name__ == "__main__":
    questions, answers = create_secondary_quizz()
    print(len(questions), len(answers))