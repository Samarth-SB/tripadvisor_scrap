import re
import requests
from bs4 import BeautifulSoup as BS
import json
import numpy as np
import pandas as pd
from pymongo import MongoClient
import csv
import os.path

uids=['9428F259657A60D8742ED81B6A0FF838']
memberTravelMapURL = []

for i in range(len(uids)):
    if len(uids[i]) > 0:
        memberTravelMapURL.append('https://www.tripadvisor.com.sg/TravelMap-a_uid.' + str(uids[i]))
    else:
        memberTravelMapURL.append('')

print memberTravelMapURL
# In[12]:

cityNames = []
cityContribution = []


#<li class="gridTile contributionsTile " name="294217" data-ox-id="294217" data-ox-name="modules.membercenter.CityTiles:eachTile"> <a href="/members-citypage/Awesome2some/g294217" onclick="ta.setEvtCookie('modules.membercenter.PublicCityTiles', 'click-city-tile', '', 0, this.href)"><div class="cityHero"><img class="cityHeroImg" src="//media-cdn.tripadvisor.com/media/photo-s/0d/bf/44/3d/sharing-the-best-local.jpg"><span class="pinFlag sprite-beenBox"></span></div><div class="cityInfo"><div class="cityName">Hong Kong, China</div><div class="contributions"><div class="contributionCount">1</div><div class="contributionTitle">Contribution</div> </div></div></a><div class="tileBeenWant"><img src="//graph.facebook.com/100001403278008/picture?type=square" class="avatar"><div class="visitInfo viBeenWant"><div class="been"><div class="flag-icon been sprite-beenUnset"> </div><div class="visitText">Been</div> </div><div class="want"><div class="flag-icon want sprite-wantUnset"> </div><div class="visitText">Want</div> </div></div></div></li>
# In[13]:

for i in range(len(memberTravelMapURL)):
    if(memberTravelMapURL[i] is not None and len(memberTravelMapURL[i]) > 0):
        html = requests.get(memberTravelMapURL[i])
        soup = BS(html.content,'html.parser')
        container1 = soup.findAll('li',{'class':'gridTile contributionsTile pinOnlyTile'})
        if(container1 is not None):

            for c in container1:
                for l in c.find('div', {'class': 'cityName'}):
                    if l is None:
                        cityNames.append('')
                    else:
                        cityNames.append(l)

                for m in c.find('div', {'class': 'contributionTitle'}):
                    if m is None:
                        cityContribution.append('')
                    else:
                        cityContribution.append(m)
            #cityInfo = container.findAll('div',{'class':'cityInfo'})
            #cityPrompt = container.findAll('div',{'class':'cityPrompt'})



# In[14]:
if(cityNames is not None):
    cityNamesDF = pd.DataFrame(np.array(cityNames))
else:
    cityNamesDF = ""
if(cityContribution is not None):
    cityContributionDF = pd.DataFrame(np.array(cityContribution))
else:
    hometownsDF = ""

print cityNames
print cityContribution