#!/usr/bin/python3

import sys
import uwsgi 
 
import urllib.request
from urllib.parse import parse_qs, unquote
from icalendar import Calendar

def application(environ, start_response):

    query = environ['QUERY_STRING']
    query_t = parse_qs(query)

    if 'type' in query_t:
        valid_event_types = query_t['type']
    else:
        valid_event_types = ["TENTATIVE", "ACCEPTED"]
    
    try :
        url = unquote(query_t['url'][0]) 
        f = urllib.request.urlopen(url)
    except (KeyError, ValueError) :
        start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
        return [b"Wrong / No URL specified\n"]

    cal = Calendar.from_ical(f.read());

    output = Calendar()

    # Copy VCALENDAR fields
    for k,v in cal.items():
        output.add(k,v)

    # Filter
    good_events = filter(lambda x: x['partstat'] in valid_event_types, 
        cal.walk("VEVENT"))

    for e in good_events:
        output.add_component(e)

    start_response('200 OK', [('Content-Type', 'text/calendar; charset=utf-8')])
    return [output.to_ical(True)]

