

from data_integration_questionnaire.service.dynamic_quizz_service import BestPracticesAdvices


def simple_advice_provider() -> BestPracticesAdvices:
    return BestPracticesAdvices(advices=[
        "Continue leveraging Talend Data Studio for your ETL processes. Consider exploring more of its out-of-the-box connectors, especially as you're considering using Snowflake in the future. This will enhance your data integration capabilities and potentially reduce development time.",
        "Start implementing a data catalog in your organization. This will help you document and understand your data better, improving data literacy and ensuring data accuracy. There are many data catalog tools available in the market, each with its own strengths and features. Consider your specific needs and choose a tool that best fits them.",
        "As you're planning to use Kafka in the future, ensure that you leverage Change Data Capture (CDC) with it. This will help you minimize data latency and improve business decision making. Remember, CDC is ideal when you want the data to be kept up to date all the time. It's a powerful tool to keep data consistency and keep all data-related systems synchronized."
    ])