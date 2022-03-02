from celery import shared_task

from main.parser import Parser, ParserAutoStart


@shared_task
def run_pars():
    parser = Parser()
    print('spreadsheet:', parser.spreadsheet)
    print('is run:', parser.is_run)
    if parser.is_run:
        parser.job()


@shared_task
def run_pars_on_background(spreadsheet):
    parser = ParserAutoStart(spreadsheet)
    print('spreadsheet:', parser.spreadsheet)
    parser.job()


