# MCP Tools Implementation

## Google Calendar API

The Google Calendar API uses OAuth 2.0 authentication instead of an API key. This means that users must authenticate via OAuth 2.0 to access their calendars and create events programmatically.

## API Keys and Authentication Setup

### OpenWeatherMap API Key
To access the OpenWeatherMap API, you will need an API key. The free tier allows for up to 1000 calls per day.

### Google Calendar OAuth 2.0 Setup Process
1. Go to the Google Cloud Console.
2. Create a new project.
3. Navigate to the APIs & Services > Credentials.
4. Click on 'Create Credentials' and select 'OAuth 2.0 Client IDs'.
5. Configure the consent screen and specify the authorized redirect URIs.
6. Download the generated client secret JSON file to use in your application.