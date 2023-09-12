import smtplib

from data_integration_questionnaire.config import mail_config
from data_integration_questionnaire.log_init import logger

from email.utils import parseaddr

import re
from data_integration_questionnaire.model.questionnaire import merge_questionnaires

from data_integration_questionnaire.service.test.questionnaire_factory import create_questionnaire_list, create_simple_questionnaire

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def validate_address(target_email: str):
    logger.info("Checking if %s is an email", target_email)
    res = parseaddr(target_email)
    return len(res[1]) > 0 and EMAIL_REGEX.match(target_email)


def send_email(
    person_name: str, target_email: str, quizz_title: str, questionnaire_summary: str
):
    # Create the base text message.

    message = f"""From: {mail_config.mail_from_person} <{mail_config.mail_user}>
To: {person_name} <{target_email}>
MIME-Version: 1.0
Content-type: text/html
Subject: {quizz_title}

<a href="https://www.onepointltd.com"><img src="https://www.onepointltd.com/wp-content/uploads/2020/06/logo-one-point.png" alt="Onepoint Consulting Ltd" /></a>
{questionnaire_summary}

"""
    # Send the message via local SMTP server.
    with smtplib.SMTP(mail_config.mail_server) as server:
        logger.info("Before starttls to %s", mail_config.mail_server)
        ehlo_res = server.ehlo()
        logger.info("ehlo_res %s", ehlo_res)
        tls_reply = server.starttls()
        logger.info("tls_reply %s", tls_reply)
        login_res = server.login(mail_config.mail_user, mail_config.mail_password)
        logger.info("login_res %s", login_res)
        logger.info("Message: %s", message)
        send_mail_res = server.sendmail(
            mail_config.mail_from, target_email, message
        )
        logger.info("send_mail_res %s", send_mail_res)
        server.quit()


if __name__ == "__main__":
    recipient = "gil.fernandes@gmail.com"
    assert validate_address(recipient)
    questionnaire = create_simple_questionnaire()
    send_email(
        "Gil Fernandeds",
        recipient,
        "Onepoint Data Integration Questionnaire",
        f"""
<h2>Questionnaire</h2>
{questionnaire.to_html()}
""",
    )
    
