import os
import urllib2
from datetime import datetime
import time
#import cPickle
from BeautifulSoup import BeautifulStoneSoup
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
from django.http import Http404

from base.http import Http403
from forms import EventSearchForm
from utils import get_event_by_id
from site_settings.utils import get_setting
from pages.models import Page

def list(request, form_class=EventSearchForm, template_name="ebevents/list.html"):
    q_event_month = request.GET.get('event_month', '')
    q_event_year = request.GET.get('event_year', '')
    q_event_type = request.GET.get('event_type', '')
    
    try:
        q_event_month = int(q_event_month)
    except:
        q_event_month = 0
    try:
        q_event_year = int(q_event_year)
    except:
        q_event_year = 0    
    
    # check the cache first
    cache_file_name = 'events.txt'
    cache_path = os.path.join(settings.MEDIA_ROOT, 'ebevents/')
    
    use_cache = False
    
    if not os.path.isdir(cache_path):
        os.mkdir(cache_path)
    cache_path = os.path.join(cache_path, cache_file_name)
    
    if os.path.isfile(cache_path):
        if time.time() - os.path.getmtime(cache_path) < 3600: # 1 hour
            use_cache = True
       
    if use_cache: 
        fd = open(cache_path, 'r')
        content = fd.read()
        fd.close()
    else:
        # process all events and store in the cache
        try:
            xml_path = settings.EVENTBOOKING_XML_URL
        except:
            xml_path = "http://xml.eventbooking.com/xml_public.asp?pwl=4E2.4AA4404E"
            
        xml = urllib2.urlopen(xml_path)
        content = xml.read()
        
        # store the xml content in the cache
        fd = open(cache_path, 'w')
        fd.write(content)
        fd.close()
        
    soup = BeautifulStoneSoup(content)
    
    events = []
    nodes = soup.findAll('event')
    for node in nodes:
        event_name =node.event_name.string
        event_name = event_name.replace('&amp;', '&').replace('&apos;', "'")
        event_type = node.event_type.string
        event_type = event_type.replace('&amp;', '&').replace('&apos;', "'")
        #if event_type <> u'HPL Express Events':
        start_date = node.date_range.start_date.string
        if start_date:
            #start_date = (datetime.strptime(start_date, '%Y-%b-%d')).strftime('%m/%d/%Y')
            start_date = datetime.strptime(start_date, '%Y-%b-%d')
        
        
        events.append({'event_name': event_name, 
                       'event_type': event_type,
                       'start_date': start_date,
                       'unique_event_id':node.unique_event_id.string})
   
        
    # make event type list
    event_types = set([evnt['event_type'] for evnt in events])
    event_types = [t for t in event_types]
    event_types.sort()
   
    
    # make year list
    event_years = set([evnt['start_date'].year for evnt in events if evnt['start_date']])
     
    # filter type  
    if q_event_type <> "":
        events = [event for event in events if event['event_type']==q_event_type]
    
    # filter date  
    if q_event_month and q_event_year:
        events = [event for event in events if event['start_date'].year==q_event_year and \
                  event['start_date'].month==q_event_month]
    elif q_event_month:
        events = [event for event in events if event['start_date'].month==q_event_month]
    elif q_event_year:
        events = [event for event in events if event['start_date'].year==q_event_year]
        

    # set form initials and choices    
    form = form_class()
    form.fields['event_month'].initial = q_event_month
    
    form.fields['event_year'].initial = q_event_year
    form.fields['event_year'].choices = [("", "Select Year")] + [(year, year) for year in event_years]
    
    form.fields['event_type'].initial = q_event_type
    form.fields['event_type'].choices = [("", "Select Category")] + [(e_type, e_type) for e_type in event_types]
    
    # top cms - it's bad but we have to hard-code the slug here
    slug = 'calendar-events'
    try:
        top_page = Page.objects.get(slug=slug)
    except:
        top_page = ''
    
  
    return render_to_response(template_name, {'form': form,
                                              'events': events, 
                                              'event_types': event_types,
                                              'selected_event_type':q_event_type,
                                              'top_page': top_page}, 
        context_instance=RequestContext(request))
    
def display(request, id, template_name="ebevents/display.html"):
    if not id: raise Http403
        
    event = get_event_by_id(id)
    if not event: raise Http404
    
    # html meta title
    html_title = '%s - ' % event['event_name']
    if isinstance(event['start_date'], datetime) and isinstance(event['start_time'], datetime):
        html_title += '%s %s' % (event['start_date'].strftime('%d-%b-%Y'), 
                                 event['start_time'].strftime('%I:%M %p'))
    if event['location']:
        html_title += ' at %s' % event['location']
    
    html_title += '. A calendar event on %s' % get_setting('site', 'global', 'sitedisplayname')
    
    
    return render_to_response(template_name, {'event': event, 'html_title': html_title}, 
        context_instance=RequestContext(request))
    
def ical(request, id):
    import re
    from timezones.utils import adjust_datetime_to_timezone
    from django.http import HttpResponse
    from django.core.urlresolvers import reverse
    from django.utils.html import strip_tags
    from utils import build_ical_text, build_ical_html
    
    event = get_event_by_id(id)
    if not event: raise Http404
    
    p = re.compile(r'http(s)?://(www.)?([^/]+)')
    d = {}
    
    d['site_url'] = get_setting('site', 'global', 'siteurl')
    match = p.search(d['site_url'])
    if match:
        d['domain_name'] = match.group(3)
    else:
        d['domain_name'] = ""
        
    ics_str = "BEGIN:VCALENDAR\n"
    ics_str += "PRODID:-//Schipul Technologies//Schipul Codebase 5.0 MIMEDIR//EN\n"
    ics_str += "VERSION:2.0\n"
    ics_str += "METHOD:PUBLISH\n"
    
    
    ics_str += "BEGIN:VEVENT\n"
        
    
    # date time
    event['start_dt'] = ''
    if isinstance(event['start_date'], datetime) and isinstance(event['start_time'], datetime):
        start_dt = datetime(event['start_date'].year, 
                            event['start_date'].month, 
                            event['start_date'].day,
                            event['start_time'].hour, 
                            event['start_time'].minute, 
                            event['start_time'].second)
        if start_dt:
            event['start_dt'] = start_dt
            start_dt = adjust_datetime_to_timezone(start_dt, settings.TIME_ZONE, 'GMT')
            start_dt = start_dt.strftime('%Y%m%dT%H%M%SZ')
            ics_str += "DTSTART:%s\n" % (start_dt)
            
    if isinstance(event['end_date'], datetime) and isinstance(event['end_time'], datetime):
        end_dt = datetime(event['end_date'].year, 
                            event['end_date'].month, 
                            event['end_date'].day,
                            event['end_time'].hour, 
                            event['end_time'].minute, 
                            event['end_time'].second)
            
        if end_dt:
            end_dt = adjust_datetime_to_timezone(end_dt, settings.TIME_ZONE, 'GMT')
            end_dt = end_dt.strftime('%Y%m%dT%H%M%SZ')
            ics_str += "DTEND:%s\n" % (end_dt)
    
    # location
    if event['location']:
        ics_str += "LOCATION:%s\n" % (event['location'])
        
    ics_str += "TRANSP:OPAQUE\n"
    ics_str += "SEQUENCE:0\n"
    
    # uid
    ics_str += "UID:uid%s@%s\n" % (id, d['domain_name'])
    
    event_url = "%s%s" % (d['site_url'], reverse('ebevent_display', args=[id]))
    d['event_url'] = event_url
    
    # text description
    ics_str += "DESCRIPTION:%s\n" % (build_ical_text(event,d))
    #  html description
    ics_str += "X-ALT-DESC;FMTTYPE=text/html:%s\n" % (build_ical_html(event,d))
    
    ics_str += "SUMMARY:%s\n" % strip_tags(event['event_name'])
    ics_str += "PRIORITY:5\n"
    ics_str += "CLASS:PUBLIC\n"
    ics_str += "BEGIN:VALARM\n"
    ics_str += "TRIGGER:-PT30M\n"
    ics_str += "ACTION:DISPLAY\n"
    ics_str += "DESCRIPTION:Reminder\n"
    ics_str += "END:VALARM\n"
    ics_str += "END:VEVENT\n"
    
    ics_str += "END:VCALENDAR\n"
    
    response = HttpResponse(ics_str)
    response['Content-Type'] = 'text/calendar'
    if d['domain_name']:
        file_name = '%s_event_%s.ics' % (d['domain_name'], id)
    else:
        file_name = "event_%s.ics" % id
    response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
    return response
    
    
    
