from celery import shared_task
from main.parser import parser_info


@shared_task
def run_pars():
    parser = parser_info.get('parser')
    print('parser:', parser)
    if parser:
        parser.job()


