#! /usr/bin/env python3
import config

def main():
    try:
        shifts = get_shifts(config.user, config.password)
        add_shifts(shifts, config.cal)
        print('added shifts!')

    except:
        print('something went wrong!')

def get_shifts(user, password):
    from requests import Session
    from bs4 import BeautifulSoup

    headers = {'User-Agent': 'Mozilla/5.0'}
    formdata = {'portal':'emp',
                'code': 'CODE',
                'user': user,
                'pswd': password}

    s = Session()

    try:
        r = s.post('https://v2can.schedulesource.com/teamwork/logon/chkLogon.aspx',
                        headers=headers,
                        data=formdata)
        # convert to fstring add '&newdate=02/23/2023' but like the next month
        r = s.get('https://v2can.schedulesource.com/teamwork/Employee/sch/schedule.aspx?view=month&layout=list')

    except:
        print('failed to scrape html')

    soup = BeautifulSoup(r.text)
    shifts_in_html = soup.findAll('tr', id=lambda x: x and x.startswith('sftList_ctl'))

    shifts = []
    for tag in shifts_in_html:
        shift = []
        for subtag in tag.children:
            if subtag.string and len(''.join(subtag.string.split())) > 5:
                shift.append(''.join(subtag.string.split()))
        shifts.append(shift)

    return shifts

def add_shifts(shifts, cal):
    from datetime import datetime
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    secrets = 'credentials.json'
    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file(secrets, scopes)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)

    for shift in shifts:
        fmt = '%m/%d/%Y %I:%M%p'
        ts_begin = shift[0] + ' ' + shift[2]
        ts_end   = shift[0] + ' ' + shift[3]
        dt_begin = datetime.strptime(ts_begin, fmt)
        dt_end   = datetime.strptime(ts_end, fmt)

        event = {
        'summary': 'Work',
        'start': {
            'dateTime': f'{dt_begin.isoformat()}-08:00',
            'timeZone': 'America/Vancouver',},
        'end': {
            'dateTime': f'{dt_end.isoformat()}-08:00',
            'timeZone': 'America/Vancouver',},
        }

        try:
            event = service.events().insert(calendarId=cal, body=event).execute()
            
        except:
            print('failed to add events')

if __name__ == '__main__':
    main()