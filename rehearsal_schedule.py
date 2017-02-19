import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

WB_NAME = '2017 - Rehearsal Schedule'
SHEET_NAME = 'Rehearsal Schedule'


SCOPES = [
    'https://spreadsheets.google.com/feeds'
];

def get_credentials():
    return ServiceAccountCredentials.from_json_keyfile_name(
        'client_secrets.json', SCOPES)


def get_sheet(workbook_name, sheet_ind, credentials):
    gc = gspread.authorize(credentials)
    return gc.open(workbook_name).worksheet(sheet_ind)



sheet = get_sheet(WB_NAME, SHEET_NAME, get_credentials())

print sheet.row_values(1)
