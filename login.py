import json
import webbrowser

import httplib2

from apiclient import discovery
from oauth2client import client

from oauth2client.file import Storage

if __name__ == '__main__':
  flow = client.flow_from_clientsecrets(
    'client_secrets.json',
    scope='https://www.googleapis.com/auth/spreadsheets.readonly',
    redirect_uri='urn:ietf:wg:oauth:2.0:oob')

  auth_uri = flow.step1_get_authorize_url()
  webbrowser.open(auth_uri)

  auth_code = raw_input('Enter the auth code: ')

  credentials = flow.step2_exchange(auth_code)

  print "Credentials saved to `credentials.txt`."
  print "Update the GSPREAD_CREDENTIALS env variable with that."

  storage = Storage('credentials.txt')
  storage.put(credentials)


  http_auth = credentials.authorize(httplib2.Http())

  drive_service = discovery.build('drive', 'v2', http_auth)
  files = drive_service.files().list().execute()
  for f in files['items']:
    print f['title']
