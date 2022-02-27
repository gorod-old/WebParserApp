from time import sleep

from django.http import HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from django.urls import reverse

from main.base import get_site_name, parse_json_payload
from main.exceptions import PayloadException
from main.forms import ParserStartForm
from main.g_spreadsheets import check_spreadsheet, get_credentials_email
from main.parser import parser_info, Parser, check_spreadsheet_in_db, delete_spreadsheet_from_db, check_parser
from webparserapp.settings import setup

# Create your views here.


def index(request):
    spreadsheet = check_spreadsheet_in_db()
    check_parser()
    form = ParserStartForm(initial={'spreadsheet': spreadsheet})
    context = {
        'title': f'{get_site_name()} - Home Page',
        'page_title': get_site_name(),
        'subtitle': setup.PROJ_SUBTITLE,
        'user_pk': request.user.pk,
        'spreadsheet': '' if not spreadsheet else spreadsheet,
        'form': form
    }
    return render(request, 'main/index.html', context=context)


def home(request):
    return HttpResponseRedirect(reverse('index'))


def run_parser(request):
    # GET POST DATA WITH TELETHON --->
    try:
        parser_name, phone, spreadsheet, channel = \
            parse_json_payload(request.body, 'parser_name', 'phone', 'spreadsheet', 'channel')
    except PayloadException as e:
        return e.to_response()

    spreadsheet_check = check_spreadsheet(spreadsheet)
    if spreadsheet_check is None:
        context = {
            'info': 'run_parser',
            'success': False,
            'message': "Can't access Google Spreadsheet, please make sure your Spreadsheet link is correct and you've "
                       "granted edit access at: ",
            'link': f"<a id='parser-link' style='color: #55a889; max-width: 100%; overflow-wrap: break-word;'>"
                    f"{get_credentials_email()}</a>"
        }
        return JsonResponse(context)

    check_spreadsheet_in_db(spreadsheet)
    if parser_info.get('parser') is None:
        Parser(spreadsheet).start()
        info = 'start parser'
    else:
        Parser(parser_info.get('parser')).change_spreadsheet(spreadsheet)
        info = 'update parser'

    return JsonResponse({'info': info, 'success': True})


def stop_parser(request):
    parser = parser_info.get('parser')
    if parser:
        parser.stop()
    delete_spreadsheet_from_db()
    while parser_info.get('parser'):
        sleep(1)
    return JsonResponse({'info': 'stop parser', 'success': True if parser else False})


def page_not_found(request, exception):
    return HttpResponseNotFound(f'<h1>Page Not Found</h1><p>{str(exception)}</p>')
