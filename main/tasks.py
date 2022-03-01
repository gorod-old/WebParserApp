from celery import shared_task

from main.parser import Parser


@shared_task
def run_pars():
    parser = Parser()
    print('spreadsheet:', parser.spreadsheet)
    print('is run:', parser.is_run)
    if parser.is_run:
        parser.job()


