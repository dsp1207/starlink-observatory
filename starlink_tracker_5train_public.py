from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import json

'''
Requirements:
- BeautifulSoup4
- IFTTT Recipe for Webhook -> Rich Notification with message content = value1 and url = value2
- OpenWeatherMap free account API key

This script checks whether conditions are favorable to see a train of Starlink satellites from the third launch from a given location on the current day. 

Here's an example of what that can look like: https://www.youtube.com/watch?v=ytUygPqjXEc

Note: Starlink satellites spread out over time after the launch, so the best time to see them is shortly after launch. You can simply update HEAVENS_ABOVE_URL with the link for future launches. 
'''

# OpenWeather API Key
OW_API_KEY = ''

# IFTTT KEY
IFTTT_KEY = ''

# IFTTT_RECIPE_NAME
IFTTT_RECIPE_NAME = ''

# Cloud threshold in % (int). Notification is triggered if value is below this.
CLOUD_THRESHOLD = 25

# Visibility Threshold. Notification is triggered if value is below this.
VISIBILITY_THRESHOLD = 3

# Maximum temporal distance in seconds between 5 satellites at their highest point. 
MAX_T_DELTA = 60

# Select your city from the top left at https://heavens-above.com/AllPassesFromLaunch.aspx and use that link (ends with ?lat=...&lng=...&loc=...&tz=...)
HEAVENS_ABOVE_URL = ''

# City ID for OpenWeather from https://openweathermap.org/find?q=
CITY_ID = ''

ow_api_url = 'https://api.openweathermap.org/data/2.5/forecast?id='+CITY_ID+'&APPID='+OW_API_KEY

ifttt_url = "https://maker.ifttt.com/trigger/"+IFTTT_RECIPE_NAME+"/with/key/"+IFTTT_KEY

list_of_visible_satellites = []

weather_data = urllib.request.urlopen(ow_api_url)

weather_json = json.loads(weather_data.read())

class satellite:
    def __init__(self, date, url, time, name, visibility, startDirection, startDegs, highDegs, endDegs):
        self.date = date
        self.time = time
        self.url = url
        self.name = name
        self.visibility = visibility
        self.startDirection = startDirection
        self.startDegs = startDegs
        self.highDegs = highDegs
        self.endDegs = endDegs
        self.isVisible = 0
        self.noti_url = ""
        self.datetime = datetime.strptime(str(datetime.now().year)+" "+date+" "+time, "%Y %d %B %H:%M:%S")

    def __str__(self):
        return(self.date+" "+self.time+": "+self.name+", Visibility: "+str(self.visibility))

    def __repr__(self):
        return(self.date+" "+self.time+": "+self.name+" Visibility: "+str(self.visibility))

def checkViz(thing):
    for item in weather_json['list']:
        timey = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
        if timey<=thing.datetime<=timey+timedelta(hours=4):
            if item['clouds']['all'] <= CLOUD_THRESHOLD:
                info_str = "Good chances for {}, Clouds: {}%".format(thing, item['clouds']['all'])
                _url = thing.url
                return [info_str, _url]



_page = urllib.request.urlopen(HEAVENS_ABOVE_URL)
_html = _page.read()
_soup = BeautifulSoup(_html,'html.parser')
clickableRows = _soup.find_all('tr',class_='clickableRow')
for row in clickableRows:
    tds = row.find_all('td')
    if float(tds[2].text) <= VISIBILITY_THRESHOLD:
        sat = satellite(date=tds[0].text, url="https://heavens-above.com/"+tds[6].find_all("a")[0]['href'], time=tds[3].text, name=tds[1].text, visibility=float(tds[2].text), startDirection=tds[5].text, startDegs=tds[4].text, highDegs=tds[7].text, endDegs=tds[10].text)
        visible = checkViz(sat)
        if visible and datetime.now().date() == sat.datetime.date():
            sat.isVisible = 1
            list_of_visible_satellites.append(sat)
            msg_content = visible[0]
            msg_url = visible[1]
            f = urllib.parse.quote_plus(msg_content)
            u = urllib.parse.quote_plus(msg_url)
            noti_url = ifttt_url+"?value1="+f+"&value2="+u
            noti_url_2 = ifttt_mama+"?value1="+f+"&value2="+u
            sat.noti_url = noti_url


for x in range(0, len(list_of_visible_satellites)-5):
    time1 = list_of_visible_satellites[x].datetime
    time2 = list_of_visible_satellites[x+4].datetime
    latest_possible_time = time1+timedelta(seconds=MAX_T_DELTA)
    if time2 < latest_possible_time:
        urllib.request.urlopen(list_of_visible_satellites[x].noti_url)
        break



print("All done")
quit()
