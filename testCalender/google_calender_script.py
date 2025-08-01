import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scope for the Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    creds = None
    script_dir = os.path.dirname(os.path.realpath(__file__))
    credentials_path = os.path.join(script_dir, 'credentials.json')
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def block_calendar_days(date_ranges, calendar_ids=None):
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    if calendar_ids is None:
        calendar_ids = ['primary']  #will default to the primary calendar if no IDs are provided

    for calendar_id in calendar_ids:
        for start_date, end_date in date_ranges:
            # enter the event in this case will be bank holidays. 
            event = {
                'summary': 'Blocked',
                'description': 'Bank Holiday',
                'start': {
                    'dateTime': f'{start_date}T00:00:00',
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': f'{end_date}T23:59:59',
                    'timeZone': 'UTC',
                },
            }

            # creates the event
            
            event = service.events().insert(calendarId=calendar_id, body=event).execute()

            if 'htmlLink' in event:
                 print(f'Event created on {calendar_id}: {event.get("htmlLink")} ') 
            else:
                print(f'Event could not be created, please try again.')
                break

if __name__ == '__main__':
    # bank holidays days below:
    # end date should be same date unless blocked needs to span over mutliple dates - this is due to the time set in event above. 
    date_ranges = [  # make sure to update dates depending on year of use 
        ('2024-03-29', '2024-03-29'),
        ('2024-04-01', '2024-04-01'),
        ('2024-05-06', '2024-05-06'),
        ('2024-05-27', '2024-05-27'),
        ('2024-08-26', '2024-08-26'),
        ('2024-12-25', '2024-12-26'),
    ]

    # enter calender ids below - primary can be removed but must be replaced - if primary is not below, can be entered like so 'primary'
    calendar_ids = ['#enter calender ids here'] 

    block_calendar_days(date_ranges, calendar_ids)
