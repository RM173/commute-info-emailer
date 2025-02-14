import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import boto3

def get_transit_options(api_key, origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "transit",
        "departure_time": "now",
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('routes'):
            return None, []
        
        leg = data['routes'][0]['legs'][0]
        overall_departure = leg.get('departure_time', {}).get('value')
        if not overall_departure:
            return None, []
        
        trip_duration = leg.get('duration', {}).get('text', "Unknown duration")
        toronto_tz = ZoneInfo("America/Toronto")
        origin_departure_dt = datetime.fromtimestamp(overall_departure, toronto_tz)
        leave_from_time = origin_departure_dt.strftime("%I:%M %p").lstrip("0")
        
        transit_options = []
        for step in leg.get('steps', []):
            if step.get('travel_mode') == 'TRANSIT':
                transit_details = step.get('transit_details', {})
                transit_departure_timestamp = transit_details.get('departure_time', {}).get('value')
                if not transit_departure_timestamp:
                    continue
                
                transit_departure_dt = datetime.fromtimestamp(transit_departure_timestamp, toronto_tz)
                transit_time_str = transit_departure_dt.strftime("%I:%M %p").lstrip("0")
                
                line_info = transit_details.get('line', {})
                transit_line = line_info.get('short_name') or line_info.get('name', 'Unknown line')
                station_name = transit_details.get('departure_stop', {}).get('name', 'Unknown station')
                
                transit_options.append({
                    "leave_from_time": leave_from_time,
                    "transit_line": transit_line,
                    "station_name": station_name,
                    "transit_departure": transit_time_str,
                    "transit_departure_timestamp": transit_departure_timestamp
                })
        
        transit_options.sort(key=lambda x: x['transit_departure_timestamp'])
        return trip_duration, transit_options
    
    except Exception as ex:
        print(f"Error in get_transit_options: {ex}")
        return None, []

def send_email_via_ses(subject, body, sender, recipient):
    ses_client = boto3.client('ses', region_name="us-east-1")
    try:
        response = ses_client.send_email(
            Source=sender,
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body}
                }
            }
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending email via SES: {e}")

def lambda_handler(event, context):
    # Get Google API key, origin, and destination from environment variables
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
    ORIGIN = os.environ.get("ORIGIN", "")
    DESTINATION = os.environ.get("DESTINATION", "")
    
    # Get sender and recipient from environment variables
    SES_SENDER = os.environ.get("SES_SENDER", "sender@example.com")
    SES_RECIPIENT = os.environ.get("SES_RECIPIENT", "recipient@example.com")
    
    trip_duration, options = get_transit_options(GOOGLE_API_KEY, ORIGIN, DESTINATION)
    
    if not options:
        output = "Could not determine any transit options."
    else:
        sentences = []
        for opt in options:
            sentence = (f"You can leave at {opt['leave_from_time']} to catch the {opt['transit_line']} at the "
                        f"{opt['station_name']} station, which leaves at {opt['transit_departure']}. "
                        f"Your commute will take {trip_duration}.")
            sentences.append(sentence)
        output = "\n".join(sentences)
    
    print(output)
    
    # Send the output via email
    send_email_via_ses(
        subject="Daily Transit Notification",
        body=output,
        sender=SES_SENDER,
        recipient=SES_RECIPIENT
    )
    
    return {
        "statusCode": 200,
        "body": json.dumps({"message": output})
    }
