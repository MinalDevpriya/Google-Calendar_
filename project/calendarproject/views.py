from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views import View
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Google Calendar API credentials
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# View to initiate the OAuth2 flow
class GoogleCalendarInitView(View):
    def get(self, request):
        flow = self.get_flow(request)
        auth_url, _ = flow.authorization_url(prompt='consent')
        return HttpResponseRedirect(auth_url)

    def get_flow(self, request):
        return InstalledAppFlow.from_client_config(
            {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uris': [request.build_absolute_uri('/rest/v1/calendar/redirect/')]
            },
            scopes=SCOPES
        )

# View to handle the redirect request and get the access token
class GoogleCalendarRedirectView(View):
    def get(self, request):
        flow = self.get_flow(request)
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials

        # Check if the access token has expired, and refresh if necessary
        if credentials.expired:
            credentials.refresh(Request())

        # Create a service object to interact with the Google Calendar API
        service = build('calendar', 'v3', credentials=credentials)

        # Get the list of events in the user's calendar
        events = service.events().list(calendarId='primary').execute()

        # Process the events as needed
        for event in events['items']:
            # Do something with each event
            print(event['summary'])

        return HttpResponse("Events retrieved successfully!")

    def get_flow(self, request):
        return InstalledAppFlow.from_client_config(
            {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uris': [request.build_absolute_uri('/rest/v1/calendar/redirect/')]
            },
            scopes=SCOPES
        )