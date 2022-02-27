import json

from main.exceptions import PayloadException
from main.models import SiteSettings, WorkTable
from webparserapp.settings import setup as Setup


def get_site_name():
    try:
        s_set = SiteSettings.objects.all()
        return s_set[0].site_title
    except Exception as e:
        print('get_site_name:' + str(e))
        s_set = SiteSettings(site_title=Setup.PROJ_TITLE)
        s_set.save()
        return s_set.site_title


def parse_json_payload(body, *keys):
    """
    Parse request.body and yield lookup values
    """
    try:
        raw_payload = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PayloadException("Cant decode body '%s'\n%s" % (body, exc))
    try:
        payload = json.loads(raw_payload)
    except (ValueError, TypeError) as exc:
        raise PayloadException("Can't load JSON from raw payload '%s'\n%s" % (raw_payload, exc))
    for key in keys:
        yield payload.get(key)


def check_spreadsheet_in_db(spreadsheet=None):
    try:
        obj = WorkTable.objects.all()[0]
        if spreadsheet is not None:
            obj.spreadsheet = spreadsheet
            obj.save()
        spreadsheet = obj.spreadsheet
    except Exception as e:
        print(str(e))
        if spreadsheet is not None:
            obj = WorkTable(spreadsheet=spreadsheet)
            obj.save()
    return spreadsheet


def delete_spreadsheet_from_db():
    try:
        WorkTable.objects.all()[0].delete()
    except Exception as e:
        print(str(e))

