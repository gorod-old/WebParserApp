from celery import shared_task

from main.models import WorkTable
from main.parser import parser_info


@shared_task
def run_pars():
    try:
        obj = WorkTable.objects.all()[0]
        spreadsheet = obj.spreadsheet
    except Exception as e:
        print(str(e))
        spreadsheet = None
    print('spreadsheet:', spreadsheet)
    parser = parser_info.get('parser')
    print('parser:', parser)
    if parser:
        parser.job()


