import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

import requests
import datetime
import sys


WB_NAME = '2017 - Rehearsal Schedule'
SHEET_NAME = 'Rehearsal Schedule'

numHeaders = 3

SCOPES = [
    'https://spreadsheets.google.com/feeds'
];


def get_credentials():
    keyfileDict = json.loads(os.environ['GSPREAD_CREDENTIALS'])
    return ServiceAccountCredentials.from_json_keyfile_dict(keyfileDict, SCOPES)


def send_slack_message(text):
  webhook_url = os.environ['SLACK_WEBHOOK']
  payload = {
    'text': text,
    'username': "Rehearsal Bot",
    'icon_emoji': ':hatched_chick:',
    'link_names': 1
  }
  print requests.post(webhook_url, data=json.dumps(payload))

def get_sheet(workbook_name, sheet_ind, credentials):
    gc = gspread.authorize(credentials)
    return gc.open(workbook_name).worksheet(sheet_ind)

def get_today_column(dates):
  today = datetime.datetime.today().strftime("%m/%d/%y")

  for idx, dateStr in enumerate(dates):
    if dateStr in today:
      return idx+1


sheet = get_sheet(WB_NAME, SHEET_NAME, get_credentials())

dates = sheet.row_values(1)

def get_column_data(sheet, colOffset):
  colData = sheet.col_values(colOffset)

  if not colData:
    raise "Accessed missing column. colOffset = %s" % colOffset

  return colData


def get_rehearsal_time(colData):
  # is there rehearsal
  # When and where is rehearsal

  rehearsalTime = colData[1] # "11am-4pm" or "NO REHEARSAL"
  isRehearsing = rehearsalTime != "NO REHEARSAL"

  rehearsalLocation = colData[2]

  if not isRehearsing:
    return None

  return "Rehearsal is %s at %s" % (rehearsalTime, rehearsalLocation)


def get_categories(sheet):
  firstColumn = get_column_data(sheet, 1)
  return firstColumn[numHeaders:]

def get_rehearsal_agenda(cats, dayColumn):
  durations = dayColumn[numHeaders:]

  instructions = []

  for idx, duration in enumerate(durations):
    if duration != "":
      instructions.append("%s: %s Hrs" % (cats[idx], duration))

  return '\n'.join(instructions)



todayColumn = get_today_column(dates)
categories = get_categories(sheet)

if not todayColumn:
  print "Could not find today in columns!"
  sys.exit(1)


def examine_day(sheet, dayColumn):
  dayData = get_column_data(sheet, dayColumn)

  parts = []
  parts.append(dayData[0])

  timeAndLocation = get_rehearsal_time(dayData)
  agenda = get_rehearsal_agenda(categories, dayData)

  if timeAndLocation == None:
    parts.append("No Rehearsal Today")
  else:
    parts.append(timeAndLocation)
    parts.append(agenda)

  return '\n'.join(parts)

for dayColumn in range(todayColumn, todayColumn+2):
  send_slack_message(examine_day(sheet, dayColumn))
