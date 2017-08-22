# -*- coding: utf-8 -*-

# Import Library ###
import re
import requests
#import urllib, urllib.request
from bs4 import BeautifulSoup as BS
#import csv
import urllib
# import lxml
import json
import numpy as np
import pandas as pd
from pymongo import MongoClient
import sys
import os.path
import csv

# Define Global Variables ###
url = 'https://www.tripadvisor.com.sg/Hotels-g294217-Hong_Kong-Hotels.html'                     # Input Hong Kong Hotels URL
#hotel_name_list = ["JW Marriott Hotel Hong Kong", "Conrad Hong Kong", "The Upper House",
#                   "Hotel Madera Hollywood", "Shama Central Serviced Apartment", "Butterfly on Wellington",
#                   "Four Seasons Hotel Hong Kong", "The Pottinger Hong Kong", "Ovolo Central",
#                   "The Landmark Mandarin Oriental, Hong Kong", "Mandarin Oriental, Hong Kong",
#                   "Mini Hotel Central Hong Kong"]        # Provide hotel name list
#hotel_name_list = ["JW Marriott Hotel Hong Kong","Mini Hotel Central Hong Kong"]
hotel_name_list = []

hotel_listing = []
hotel_page_url = []
hotel_name = []
hotel_url = []
hotel_location = []
hotel_counter = 0

names = []
ratings = []
dates = []
titles = []
bodies = []
recommendTitles = []
recommendAnswers = []

ageGenders = []
ages = []
genders = []
hometowns = []
travelStyleTags = []
points = []
levels = []
usernames = []

REVIEW_THREADS = 4

# Define Functions ###

def main():
    
# Option 1: Add hotel document to collection 
# Option 2: Add reviews and member document to collection
# Option 3: Delete all documents in hotel collection
# Option 4: Delete all documents in user review collection
# Option 5: Delete all documents in member collection
# Option 6: Initialise database

# Provide option:  
    global hotel_name_list
    
    if len(sys.argv) > 3 or len(sys.argv) < 3:
        print("Run : python tripadvisor_hotels.py <option> <hotel list csv> e.g. python tripadvisor_hotels.py 2 hotel_list.csv")
        sys.exit()

    option = sys.argv[1]
    hotel_list_file = sys.argv[2]
    print("option : " + option)
    print("hotel_list_file : " + hotel_list_file)
    if os.path.isfile(hotel_list_file):
        with open(hotel_list_file,'rU') as f:
            line = csv.reader(f)
            i = 0
            print('Load hotels from file')
            for row in line:
                print(str(i) + ':' + row[0])
                hotel_name_list.append(row[0])
                i = i + 1
            print("total hotel list found : " + str(i)) 
            f.close()
    else:
        print("Hotel list csv file not found. Program exit.")
        sys.exit()

    if option == "1":        
        add_hotel_listing()    
    if option == "2":
        add_review_record()
    if option == "3":
        delete_from_mongoDB("hotel_listing")        
    if option == "4":
        delete_from_mongoDB("user_review")
    if option == "5":
        delete_from_mongoDB("member_profile")   
    if option == "6":
        initialise_database()



def add_hotel_listing():
#     html = requests.get(url)
#     soup = BS(html.content,'html.parser')
    print(hotel_name_list)
    
    for i1 in hotel_name_list:
        found_flag = 0
        attempt_cnt = 1
        while found_flag == 0:
            html = requests.get(url)
            soup = BS(html.content,'html.parser')
            print(i1)
            while True:
                for l1 in soup.findAll('div', {'class':"listing_title"}):
                    for l2 in l1.findAll('a', {'class':"property_title"}):
                        if l2.text.strip(' \n\t\r') == i1:
#                            if l2.text.strip(' \n\t\r') not in hotel_name:
                            found_flag = 1
    #                       print(found_flag)
                            hotel_name.append(l2.text.strip(' \n\t\r'))
                            hotel_url.append('https://www.tripadvisor.com.sg' + l2.get('href'))
                            print("Hotel url found for:", l2.text.strip(' \n\t\r'))
                            print('https://www.tripadvisor.com.sg' + l2.get('href'))
                page_link = soup.findAll(attrs={'class':"nav next taLnk ui_button primary"})
                if found_flag == 1:
                    break
                if len(page_link)==0:
                    break
                else:
                    soup=BS(urllib.request.urlopen('https://www.tripadvisor.com.sg' + page_link[0].get('href')),'html.parser')

            if found_flag == 0:
                attempt_cnt += 1
                print("Hotel url for", i1, "not found. Executing attempt:", attempt_cnt)
            

            
    write_to_mongoDB("hotel_listing")
        
def add_review_record():

    global hotel_counter
        
    read_from_mongoDB("hotel_listing")
    print("No. of hotel in name list provided:", len(hotel_name_list))    
    print("No. of hotel url found on TripAdvisor website:", len(hotel_name))
    
    #if len(hotel_name) == len(hotel_name_list):
    #    print('Hotel list matched.')    
#         for i in hotel_url:
#         #    print(i)
#             get_hotel_review(i)
        #pool = ThreadPool(REVIEW_THREADS)
    while hotel_counter < len(hotel_name):
        print('Hotel no.:', hotel_counter + 1)
        print(hotel_name[hotel_counter])
        print(hotel_url[hotel_counter])
        try:
            if(hotel_name[hotel_counter] in hotel_name_list):
                #param1 = [hotel_url[hotel_counter]]
                #pool.map(get_hotel_review, param1)
                #pool.wait_completion()
                get_hotel_review(hotel_url[hotel_counter])
            hotel_counter += 1
        except:
            print("Error: unable to run get_hotel_review")
    #else:
    #    print('Hotel list mismatched.')



def get_hotel_review(url):

    print('Get hotel review url.')    
    html = requests.get(url)
    soup = BS(html.content,'html.parser')
    page_no = []
    temp_url = []
    
    for l1 in soup.findAll('div', {'id':"REVIEWS"}):
        for l2 in l1.findAll('span', {'class':"pageNum last taLnk "}):
            page_no.append(l2.get('data-page-number'))
    print('Review pages: ' + page_no[0])   

# Get review link ###    
    for l1 in soup.findAll('div', {'class':"quote"}):
        container = l1.find('a')
        temp_url.append('https://www.tripadvisor.com.sg' + container['href'])    
    
    userReviewURL = []
    userReviewURL.append(temp_url[0])

# To loop through all reviews pages
    for i in range(int(page_no[0])-1):            # To use this line when running full scrap (all pages of reviews)
    #for i in range(3):                              # To use this line when running partial scrap for debug
#        print(i)
        html = requests.get(userReviewURL[i])
        print(userReviewURL[i])
        soup = BS(html.content,'html.parser')
        container = soup.find('a',{'data-page-number':i+2})
#        print(container)
        urlTemp = 'https://www.tripadvisor.com.sg' + container['href']
        userReviewURL.append(urlTemp)    

# Read review ###    
    print('Reading reviews.')  
    temp = []
    uids = []

    global names
    global ratings
    global dates
    global titles
    global bodies
    global recommendTitles
    global recommendAnswers    
    names[:] = []
    ratings[:] = []
    dates[:] = []
    titles[:] = []
    bodies[:] = []
    recommendTitles[:] = []
    recommendAnswers[:] = []

    for i in range(len(userReviewURL)):
        html = requests.get(userReviewURL[i])
        soup = BS(html.content,'html.parser')
        container = soup.find('div',{'id':'SHOW_USER_REVIEW'})    
        print('Parsing url : ' + userReviewURL[i])

        for j in range(5):
            temp = container.findAll('div',{'id':re.compile('^review_')})[j]
            name = temp.find('span',{'class':re.compile('^expand_inline')})
            if(name is None):
                continue
            rating = temp.find('span',{'class':re.compile('^ui_bubble_rating')})['class'][1]
            date = temp.find('span',{'class':'ratingDate'}).next_element
                
            if j == 0:
                title = temp.find('div',{'property':'name'})
                body = temp.find('p',{'property':'reviewBody'})
            else:
                title = temp.find('span',{'class':'noQuotes'})
                body = temp.find('p',{'id':re.compile('^review_')})
            recommendTitle = temp.find('span',{'class':'recommend-titleInline'})
            recommendAnswer = temp.findAll('li',{'class':'recommend-answer'})
            memberInfo = temp.find('div',{'class':'member_info'})
#            print(memberInfo)
            memberOverlayLink = memberInfo.find('div',{'class':'memberOverlayLink'})
            if(memberOverlayLink is not None):
                uid = memberOverlayLink['id']
                print('uid : ' + uid)
            else:
                uid = ""
        
            if name is not None and len(name) > 0:
                names.append(name.text)
            else:
                names.append('')
            if rating is not None and len(rating) > 0:
                ratings.append(rating[7])
            else:
                ratings.append('')
            if date is not None and len(date) > 0:
                dates.append(date)
            else:
                dates.append('')
            if title is not None and len(title) > 0:
                titles.append(title.text)
            else:
                titles.append('')
            if body is not None and len(body) > 0:
                bodies.append(body.text.strip('\n'))
            else:
                bodies.append('')
            if recommendTitle is not None and len(recommendTitle) > 0:
                recommendTitles.append(recommendTitle.text)
            else:
                recommendTitles.append('')
            if recommendAnswer is not None and len(recommendAnswer) > 0:
                jsonTemp = {}
                for k in range(len(recommendAnswer)):
                    jsonTemp[recommendAnswer[k].text.strip('\n')] = recommendAnswer[k].find('span')['alt'][0]
                recommendAnswers.append(json.dumps(jsonTemp))
            else:
                recommendAnswers.append('')
            if uid is not None and len(uid) > 0:
                uids.append(uid[4:uid.find('-SRC')])
            else:
                uids.append('')
    
    write_to_mongoDB("user_review")   
    get_member_profile(uids)
    


# Read member profile ###
def get_member_profile(uids):
    
    print('Get member profile.')    
    print(uids)
    memberOverlayLink = []
    memberProfileURL = []

    for i in range(len(uids)):
        if len(uids[i]) > 0:
            memberOverlayLink.append('https://www.tripadvisor.com.sg/MemberOverlay?Mode=owa&uid=' + str(uids[i]))
            memberProfileURL.append('https://www.tripadvisor.com.sg/MemberProfile-a_uid.' + str(uids[i]))
        else:
            memberOverlayLink.append('')
            memberProfileURL.append('')

    global ageGenders
    global hometowns
    global travelStyleTags
    global points
    global levels
    global usernames
    global ages
    global genders
    
    ageGenders[:] = []
    hometowns[:] = []
    travelStyleTags[:] = []
    points[:] = []
    levels[:] = []
    usernames[:] = []
    ages[:] = []
    genders[:] = []
    
    for i in range(len(memberProfileURL)):
        if(memberProfileURL[i] is not None and len(memberProfileURL[i]) > 0):
            html = requests.get(memberProfileURL[i])
            soup = BS(html.content,'html.parser')
            container = soup.find('div',{'id':'MODULES_MEMBER_CENTER'})
            if(container is not None):
                ageGender = container.find('div',{'class':'ageSince'})
                hometown = container.find('div',{'class':'hometown'})
                travelStyleTag = container.findAll('div',{'class':'tagBubble unclickable'})
                point = container.find('div',{'class':'points'})
                level = container.find('div',{'class':'level tripcollectiveinfo'})
                username = container.find('span',{'class':'nameText'})
                
                if len(ageGender) > 0:
                    ageGenders.append(ageGender.text[14:].strip())
                    splitAgeGenders = ageGender.text[14:].strip().split('old')
                    if(len(splitAgeGenders)==1):
                        ages.append(splitAgeGenders[0])
                        genders.append('')
                    elif(len(splitAgeGenders)==2):
                        ages.append(splitAgeGenders[0])
                        genders.append(splitAgeGenders[1])
                else:
                    ageGenders.append('')
                if len(hometown) > 0:
                    hometowns.append(hometown.text)
                else:
                    hometowns.append('')
                if len(travelStyleTag) > 0:
                    listTemp = []
                    for j in range(len(travelStyleTag)):
                        listTemp.append(travelStyleTag[j].text.strip())
                    travelStyleTags.append(listTemp)
                else:
                    travelStyleTags.append('')
                if len(point) > 0:
                    points.append(int(str(point.text.strip()).replace(',','')))
                else:
                    points.append('')
                if level is not None:
                    levels.append(level.text[6:level.text.find(' ',6)].strip())
                else:
                    levels.append('')
                if len(username) > 0:
                    usernames.append(username.text)
                else:
                    usernames.append('')
    
    write_to_mongoDB("member_profile")
    
    
    
def read_from_mongoDB(doc_name):  
    
# db host
    client = MongoClient("localhost", 27017)
#    client = MongoClient("mongodb://ke5016:ke5016!@cluster0-shard-00-00-5ymmp.mongodb.net:27017,cluster0-shard-00-01-5ymmp.mongodb.net:27017,cluster0-shard-00-02-5ymmp.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")

# db name
    db = client.tripadvisor
    
# collection name
    print('Collection name: ' + doc_name)
    collection = db[doc_name].find()
#    print(collection)

    if doc_name == "hotel_listing":
        for i in collection:
            hotel_name.append(i['name'])
            hotel_url.append(i['url'])
            hotel_location.append(i['location'])   
#            print(i['name'])
        print("Number of documents read:", len(hotel_name))
        
#         i=0
#         while i < len(hotel_name):
#             print(hotel_name[i])
#             print(hotel_url[i])
#             print(hotel_location[i])
#             i += 1     



def initialise_database():
# db host
    client = MongoClient("localhost", 27017)
#    client = MongoClient("mongodb://ke5016:ke5016!@cluster0-shard-00-00-5ymmp.mongodb.net:27017,cluster0-shard-00-01-5ymmp.mongodb.net:27017,cluster0-shard-00-02-5ymmp.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")

# db name
    db = client.tripadvisor

# reset collection
    collection = db.collection_names(include_system_collections=False)
    for collect in collection:
        db[collect].drop()
    
    print('All collections dropped from database.')

        
    
def write_to_mongoDB(doc_name):    

# db host
    client = MongoClient("localhost", 27017)
#    client = MongoClient("mongodb://ke5016:ke5016!@cluster0-shard-00-00-5ymmp.mongodb.net:27017,cluster0-shard-00-01-5ymmp.mongodb.net:27017,cluster0-shard-00-02-5ymmp.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")

# db name
    db = client.tripadvisor

# collection name
    print('Collection name: ' + doc_name)
    collection = db[doc_name]
    print(collection)

# reset collection
#    collection.remove({})

    if doc_name == "hotel_listing":
        
        for i in range(len(hotel_name)):
            document = {'name':hotel_name[i].strip(),
                        'url':hotel_url[i].strip(),
                        'location':''}
            collection.insert(document)
            
        print("Number of documents inserted:", len(hotel_name))
        
        for i in collection.find():
            print(i['name'])
            print(i['url'])
                
    if doc_name == "user_review":     
        
#        print(hotel_counter)
        print('Writing User Reviews for: ' + hotel_name[hotel_counter].strip())
        for i in range(len(names)):
            document = {'name':names[i].strip(),
                        'hotelName':hotel_name[hotel_counter].strip(),
                        'rating':ratings[i].strip(),
                        'date':dates[i].strip(),
                        'title':titles[i].strip(),
                        'body':bodies[i].strip(),
                        'recommendTitle':recommendTitles[i].strip(),
                        'ratingSummary':recommendAnswers[i].strip(),
                        'sentiment':'',
                        }
            collection.insert(document)  
        
        print("Number of documents inserted:", len(names))
        
        for i in collection.find():
            print(i['name'])
            print(i['hotelName'])
            print(i['rating'])
            print(i['date'])
            print(i['title'])
            print(i['body'])
            print(i['recommendTitle'])
            print(i['ratingSummary'])
            
    if doc_name == "member_profile":
        print(ageGenders)
        print(hometowns)
        print(travelStyleTags)
        print(points)
        print(levels)
        
        for i in range(len(ageGenders)):
            hotels = []
            travelTypes = []
            
            for hotelsResult in db.user_review.find({ 'name': usernames[i].strip()}):
                if(hotelsResult['hotelName'] not in hotels):
                    hotels.append(hotelsResult['hotelName'])
                if(hotelsResult['recommendTitle'] not in travelTypes):
                    splitRecTitle = hotelsResult['recommendTitle'].split(',')
                    if(len(splitRecTitle) == 2):
                        travelTypes.append(splitRecTitle[1].strip())
            
            print('hotels : ' + str(hotels)[1:-1])
            document = db.member_profile.find_one({ 'username': usernames[i].strip()})
            
            if(document is not None and document.count() > 0):
                if(len(set(document['hotels'])-set(hotels)) > 0):
                    print("updating hotels");
                    collection.update({'username':usernames[i].strip()},
                                      {
                                        'hotels':hotels   
                                      }
                                     )
                elif(len(set(document['travelTypeTag'])-set(travelTypes)) > 0):
                    print("updating travelTypeTag");
                    collection.update({'username':usernames[i].strip()},
                                      {
                                        'travelTypeTag':travelTypes  
                                      }
                                     )
            else:
                print("inserting");
                document = {'username':usernames[i].strip(),
                            'age':ages[i].strip(),
                            'gender':genders[i].strip(),
                            'hometown':hometowns[i].strip(),
                            'travelStyleTag':travelStyleTags[i],
                            'travelTypeTag':travelTypes,
                            'point':points[i],
                            'level':levels[i].strip(),
                            'hotels':hotels
                            }

                collection.insert(document)
                            
        
        print("Number of documents inserted:", len(ageGenders))
        
        for i in collection.find():
            print(i['age'])
            print(i['gender'])
            print(i['hometown'])
            print(i['travelStyleTag'])
            print(i['point'])
            print(i['level'])
            print(i['hotels'])
                    
    print("Number of documents in collection after new documents inserted:", collection.count())
    client.close()



def delete_from_mongoDB(doc_name):

# db host
    client = MongoClient("localhost", 27017)
#    client = MongoClient("mongodb://ke5016:ke5016!@cluster0-shard-00-00-5ymmp.mongodb.net:27017,cluster0-shard-00-01-5ymmp.mongodb.net:27017,cluster0-shard-00-02-5ymmp.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")

# db name
    db = client.tripadvisor

# collection name
    print('Collection name: ' + doc_name)
    collection = db[doc_name]
    print(collection)

# reset collection
#    collection.remove({})

    if doc_name == "hotel_listing":
        collection.remove({})
        
    if doc_name == "user_review":  
        collection.remove({})
        
    if doc_name == "member_profile":
        collection.remove({})
                 
    print("All documents deleted from collection:", doc_name)
    client.close()

# Execute ###
main()



