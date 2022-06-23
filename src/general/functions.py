from threading import Thread
from urllib.error import HTTPError

from flask import current_app
from sendgrid import SendGridAPIClient, Mail
from sqlalchemy import and_



def filter_data_result_with_operator(filter_name=None, attribute=None,
                                     filter_data=None):
    filter_main = and_()
    if all(v is not None for v in [attribute, filter_name, filter_data]):
        if check_filter_data(filter_name, filter_data):
            value = filter_data[filter_name]['value']
            operator = filter_data[filter_name]['operator']
            if value:
                filter_main = and_(
                    filter_main,
                    attribute.ilike(check_like_filter_operator(
                        operator, value)))
    else:
        pass
    return filter_main

def filter_data_result_between_two_values(
        filter_name=None, filter_date_from=None, filter_date_to=None,
        attribute=None, filter_data=None):

    from src import AppLogException
    from src.general import Status

    filter_main = and_()
    if all(v is not None for v in [attribute, filter_name,
                                   filter_date_from, filter_date_to,
                                   filter_data]):

        if filter_name in filter_data:
            if filter_date_from in filter_data[filter_name]:
                if filter_date_to in filter_data[filter_name]:
                    date_from = filter_data[filter_name][filter_date_from] if \
                        filter_data[filter_name][filter_date_from] != '' \
                        else None

                    date_to = filter_data[filter_name][filter_date_to] if \
                        filter_data[filter_name][filter_date_to] != '' else None

                    if date_from is None:
                        if date_to is None:
                            pass
                        else:
                            filter_main = and_(
                                filter_main,
                                attribute <= date_to)

                    elif date_to is None:
                        if date_from is None:
                            pass
                        else:
                            filter_main = and_(
                                filter_main,
                                attribute >= date_from)
                    else:
                        filter_main = and_(
                            filter_main,
                            attribute >= date_from,
                            attribute <= date_to)
                else:
                    pass
                    # raise DefaultAppException(
                    #     Status(-101,
                    #            "This filter_date_to not in "
                    #            "filter_data[filter_name]").__dict__)

            else:
                pass
                # raise DefaultAppException(
                #     Status(-101,
                #            "This filter_date_from not in "
                #            "filter_data[filter_name]").__dict__)

        else:
            pass
            # raise DefaultAppException(
            #     Status(-101, "This filter_name not in filter_data").__dict__)

    else:
        raise AppLogException(
            Status(400,
                   "All parameters are mandatory in filter_data_"
                   "between_date function"))

    return filter_main




def check_filter_data(key, filter_data):
    if filter_data is not None:
        if key in filter_data:
            if 'value' in filter_data[key]:
                if 'operator' in filter_data[key]:
                    return True
    return False


def check_like_filter_operator(operator, value):
    if operator == 'START':
        return value + '%'
    elif operator == 'CONTAINS':
        return '%' + value + '%'
    elif operator == 'EXACT':
        return value
    elif operator == 'FINISH':
        return '%' + value

def send_email_async(app, message):
    with app.app_context():
        sg = SendGridAPIClient(current_app.config.get('EMAIL_TOKEN'))
        try:
            msg = Mail(
                from_email='no.reply.sms.service.provider@gmail.com',
                to_emails=message['recipient'],
                subject=message['subject'],
                html_content=message['body'])

            response = sg.send(msg)
        except HTTPError as e:
            print(e)

def send_email(message):
    app = current_app._get_current_object()
    Thread(target=send_email_async, args=(app, message)).start()


