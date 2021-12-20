import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import time
import datetime
import webbrowser
import requests
from pygame import mixer
from googlesearch import *
from pycricbuzz import Cricbuzz
import COVID19Py
import billboard
import pytz

from tensorflow.keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
intents = json.loads(open('intents.json', encoding='utf-8').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def get_response(return_list,intents_json,text):

    if len(return_list)==0:
        tag='noanswer'
    else:
        tag=return_list[0]['intent']
    if tag=='datetime':
        x=''
        tz = pytz.timezone('Asia/Kolkata')
        dt=datetime.now(tz)
        x+=str(dt.strftime("%A"))+' '
        x+=str(dt.strftime("%d %B %Y"))+' '
        x+=str(dt.strftime("%H:%M:%S"))
        return x,'datetime'



    if tag=='weather':
        x=''
        api_key='987f44e8c16780be8c85e25a409ed07b'
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        # city_name = input("Enter city name : ")
        city_name = text.split(':')[1].strip()
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name
        response = requests.get(complete_url)
        response=response.json()
        pres_temp=round(response['main']['temp']-273,2)
        feels_temp=round(response['main']['feels_like']-273,2)
        cond=response['weather'][0]['main']
        x+='Present temp.:'+str(pres_temp)+'C. Feels like:'+str(feels_temp)+'C. '+str(cond)
        print(x)
        return x,'weather'

    if tag=='news':
        main_url = " http://newsapi.org/v2/top-headlines?country=in&apiKey=bc88c2e1ddd440d1be2cb0788d027ae2"
        open_news_page = requests.get(main_url).json()
        article = open_news_page["articles"]
        results = []
        x=''
        for ar in article:
            results.append([ar["title"],ar["url"]])

        for i in range(10):
            x+=(str(i + 1))
            x+='. '+str(results[i][0])
            x+=(str(results[i][1]))
            if i!=9:
                x+='\n'

        return x,'news'

    if tag=='cricket':
        c = Cricbuzz()
        matches = c.matches()
        for match in matches:
            print(match['srs'],' ',match['mnum'],' ',match['status'])

    if tag=='song':
        chart=billboard.ChartData('hot-100')
        x='The top 10 songs at the moment are: \n'
        for i in range(10):
            song=chart[i]
            x+=str(i+1)+'. '+str(song.title)+'- '+str(song.artist)
            if i!=9:
                x+='\n'
        return x,'songs'

    if tag=='timer':
        #mixer.init()
        x=text.split(':')[1].strip()
        time.sleep(float(x)*60)
        #mixer.music.load('Handbell-ringing-sound-effect.mp3')
        #mixer.music.play()
        x='Timer ringing...'
        return x,'timer'


    if tag=='covid19':

        covid19=COVID19Py.COVID19(data_source='jhu')
        country=text.split(':')[1].strip()
        x=''
        if country.lower()=='world':
            latest_world=covid19.getLatest()
            x+='Confirmed Cases:'+str(latest_world['confirmed'])+' Deaths:'+str(latest_world['deaths'])
            return x,'covid19'
        else:
            latest=covid19.getLocations()
            latest_conf=[]
            latest_deaths=[]
            for i in range(len(latest)):

                if latest[i]['country'].lower()== country.lower():
                    latest_conf.append(latest[i]['latest']['confirmed'])
                    latest_deaths.append(latest[i]['latest']['deaths'])
            latest_conf=np.array(latest_conf)
            latest_deaths=np.array(latest_deaths)
            x+='Confirmed Cases:'+str(np.sum(latest_conf))+' Deaths:'+str(np.sum(latest_deaths))
            return x,'covid19'



    list_of_intents= intents_json['intents']
    for i in list_of_intents:
        if tag==i['tag'] :
            result= random.choice(i['responses'])
    return result,tag

def response(text):
    return_list=predict_class(text,model)
    response,_=get_response(return_list,intents,text)
    return response

# while(1):
#     x=input()
#     print(response(x))
#     if x.lower() in ['bye','goodbye','get lost','see you']:  
#         break


# #Self learning
# print('Help me Learn?')
# tag=input('Please enter general category of your question  ')
# flag=-1
# for i in range(len(intents['intents'])):
#     if tag.lower() in intents['intents'][i]['tag']:
#         intents['intents'][i]['patterns'].append(input('Enter your message: '))
#         intents['intents'][i]['responses'].append(input('Enter expected reply: '))        
#         flag=1

# if flag==-1:
    
#     intents['intents'].append (
#         {'tag':tag,
#          'patterns': [input('Please enter your message')],
#          'responses': [input('Enter expected reply')]})
    
# with open('intents.json','w') as outfile:
#     outfile.write(json.dumps(intents,indent=4)) 