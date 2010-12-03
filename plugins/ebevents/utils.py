import urllib2
from datetime import datetime
from django.conf import settings
from BeautifulSoup import BeautifulStoneSoup

from django.utils.html import strip_tags

def get_event_by_id(id, **kwargs):
    try:
        xml_url = settings.EVENTBOOKING_XML_URL
    except:
        xml_url = "http://xml.eventbooking.com/xml_public.asp?pwl=4E2.4AA4404E"
        
    xml_url = '%s&mode=detail&event_id=%s' % (xml_url.strip(), id)
    
    xml = urllib2.urlopen(xml_url)
    soup = BeautifulStoneSoup(xml)
    node = soup.find('public_event_detail')
    
    event = {}
    
    try:
        event['event_name'] = node.event_name.string
    except AttributeError:
        return None
        
    event['event_name'] = event['event_name'].replace('&amp;', '&')
    event['event_type'] = node.event_type.string
    event['unique_event_id'] = node.unique_event_id.string
    
    # date time
    try:
        start_date = node.showtimes.subevent['startdate']
        start_date = datetime.strptime(start_date, '%Y-%b-%d')
    except:
        start_date = ''
    try:
        start_time = node.showtimes.subevent['starttime']
        start_time =  datetime.strptime(start_time.strip(), '%I:%M:%S %p')
        #start_time = start_time.replace(":00 ", " ")   # 04:00:00 PM - fix later by converting to dt
    except:
        start_time = ''

        
    try:
        end_date = node.showtimes.subevent['enddate']
        end_date = datetime.strptime(end_date, '%Y-%b-%d')
    except:
        end_date = ''
    try:
        end_time = node.showtimes.subevent.string
        end_time = end_time.replace('-', '')
        
        end_time =  datetime.strptime(end_time.strip(), '%I:%M %p')
    except:
        end_time = ''
    print end_time
     
    if not start_date:
        start_date = node.date_range.start_date.string
        start_date = datetime.strptime(start_date, '%Y-%b-%d')
        start_time = node.date_range.start_time.string
        try:
            start_time =  datetime.strptime(start_time.strip(), '%I:%M:%S %p')
        except:
            pass 
        end_date = node.date_range.end_date.string
        end_date = datetime.strptime(end_date, '%Y-%b-%d')
        end_time = node.date_range.end_time.string
        try:
            end_time =  datetime.strptime(end_time.strip(), '%I:%M:%S %p')
        except:
            pass 
           
    event['start_date'] = start_date
    event['start_time'] = start_time
    event['end_date'] = end_date
    event['end_time'] = end_time
    
    # description
    event['description'] = node.description.string
    if event['description']:
        event['description'] = event['description'].replace('&amp;', '&')
        event['description'] = event['description'].replace('&lt;', '<')
        event['description'] = event['description'].replace('&gt;', '>')
    else:
        event['description'] = ''
    # caption
    try:
        event['caption'] = node.subevents.subevent['caption'] 
    except:
        event['caption'] = ""
    
    # ticket
    event['ticket_info'] = node.ticket_info.string
    event['ticket_prices'] = node.ticket_prices.string
    event['ticket_sale_date'] = node.ticket_sale_date.string
    try:
        event['ticket_sale_date'] = datetime.strptime(event['ticket_sale_date'], '%Y-%b-%d')
    except:
        pass
    event['ticket_sale_time'] = node.ticket_sale_time.string
    
    # location
    event['location'] = node.location.string
    event['venue_name'] = node.venue_name.string
    event['venue_website'] = node.venue_website.string
    
    # additional info
    event['additional_info'] = node.additional_info.string
    
    # picture thumb
    event['picture_thumb'] = node.picture_thumb.string
    if event['picture_thumb']:
        event['picture_thumb_height'] = int(node.picture_thumb['height'])
        event['picture_thumb_width'] = int(node.picture_thumb['width'])
    
    # picture full
    event['picture_full'] = node.picture_full.string
    if event['picture_full']:
        event['picture_full_height'] = int(node.picture_full['height'])
        event['picture_full_width'] = int(node.picture_full['width'])
    
    # weird - those elements appear as upper case in the xml file
    # but the parser only takes as lower case. Need to change all to lower case
    elements = ['DIRURL', 'TI', 'MI', 'SEATCHART', 'RM', 'SPONS',
                'PARKING', 'PROMOTER', 'PRESENTER', 'PRODUCER', 
                'OPENING_ACT', 'CONTACT', 'SPECIAL_ENT', 'DOORSOPEN',
                'RESTR', 'CONTACT_PHONE', 'CONTACT_EMAIL', 'VIDEO', 
                'AUDIO', 'GROUPSALES']
    elements = [e.lower() for e in elements]
    
    for e in elements:
        try:
            event[e] = eval("node.%s.string" % e) 
            event[e + '_caption'] = eval("node.%s['caption']" %e)
        except:
            event[e]= ''
            event[e + '_caption'] = ''
            
    return event


def build_ical_text(event, d):
    ical_text = '%s\n\n' % d['event_url']
    
    # title
    ical_text += "Event Name: %s\n" % strip_tags(event['event_name'])
    
    # start_dt
    if event['start_dt']:
        ical_text += 'Start Date / Time: %s CST\n' % (event['start_dt'].strftime('%b %d, %Y %I:%M %p'))
    
    # location
    if event['location']:
        ical_text += 'Location: %s\n' % (event['location'])
    if event['venue_name']:
        ical_text += 'Venue: %s\n' % (event['venue_name'])
    if event['venue_website']:
        ical_text += '%s\n' % (event['venue_website'])
            
    ical_text += strip_tags(event['description'])
    
    ical_text  = ical_text.replace(';', '\;')
    ical_text  = ical_text.replace('\n', '\\n')
   
    return ical_text
    
def build_ical_html(event, d):  
    # title
    ical_html = "<h1>Event Name: %s</h1>" % (event['event_name'])
    
    ical_html += '<div>%s</div><br />' % d['event_url']
    
    # start_dt
    if event['start_dt']:
        ical_html += '<div>When: %s CST</div>' % (event['start_dt'].strftime('%b %d, %Y %I:%M %p')) 
        
    # location
    if event['location']:
        ical_html += '<div>Location: %s</div>' % (event['location'])
    if event['venue_name']:
        ical_html += '<div>Venue: %s</div>' % (event['venue_name'])
    if event['venue_website']:
        ical_html += '<div>%s</div>' % (event['venue_website'])
   
    ical_html += '<div>%s</div>' % (event['description'])
    
    ical_html  = ical_html.replace(';', '\;')
    #ical_html  = degrade_tags(ical_html.replace(';', '\;'))
   
    return ical_html