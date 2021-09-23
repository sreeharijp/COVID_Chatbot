from tkinter import *
import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time

API_KEY = "tPEEw7WGxt4u"
PROJECT_TOKEN = "tesO10XY0Y7M"
RUN_TOKEN = "tYvpLKCqfcRp"
Query = ""
Reply = ""
Contry = ""
Context = ""


class Data:
    def __init__(self , api_key , project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data' ,
                                params=self.params)
        data = json.loads(response.text)
        return data

    def get_total_cases(self):
        data = self.data['total']

        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['value']

    def get_total_deaths(self):
        data = self.data['total']
        for content in data:
            if content['name'] == "Deaths:":
                return content['value']

        return "0"

    def get_country_data(self , country):
        data = self.data["country"]

        for content in data:
            if content['name'].lower() == country.lower():
                return content

        return "0"

    def get_list_of_countries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'].lower())

        return countries

    def update_data(self):
        response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run' ,
                                 params=self.params)

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data updated")
                    break
                time.sleep(5)

        t = threading.Thread(target=poll)
        t.start()


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            global Reply
            Reply = "I do not understand" + e
            global Country
            Country = "none"
    return said.lower()


def main():
    print("Started Program")
    global Country
    data = Data(API_KEY , PROJECT_TOKEN)
    END_PHRASE = "stop"
    country_list = data.get_list_of_countries()

    TOTAL_PATTERNS = {
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases ,
        re.compile("[\w\s]+ total cases"): data.get_total_cases ,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths ,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths
    }

    COUNTRY_PATTERNS = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'] ,
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'] ,
    }

    UPDATE_COMMAND = "update"
    text = Query.lower()
    print(text)
    result = None
    for pattern , func in COUNTRY_PATTERNS.items():
        if pattern.match(text):
            words = set(text.split(" "))
            for country in country_list:
                if country in words:
                    result = func(country)
                    global Country
                    Country = country
                    break

    for pattern , func in TOTAL_PATTERNS.items():
        if pattern.match(text):
            result = func()
            break

    if text == UPDATE_COMMAND:
        result = "Data is being updated. This may take a moment!"
        data.update_data()

    if result:
        #peak(result)
        global Reply
        global Contry
        if Country == "none":
            Reply = result
        else:
            Reply = "Number of " + Context + " in " + Country + " is " + result

    if text.find(END_PHRASE) != -1:  # stop loop
        textarea.insert("Bot:Let there be darkness")
        speak("let there be darkness")
        root.quit()


def ask_clicked():
    global Query
    global Context
    Query = questionfield.get()
    textarea.insert(END , "You:" + Query + "\n\n")
    if re.search("Cases",Query.lower(),re.IGNORECASE):
        Context ="cases"
    if re.search("deaths",Query.lower(),re.IGNORECASE):
        Context = "deaths"
    main()
    textarea.insert(END , "Bot:" + Reply + "\n\n")
    speak(Reply.lower())
    questionfield.delete(0 , END)
    textarea.yview(END)


def mic_clicked():
    global Query
    Query = get_audio()
    textarea.insert(END , "You:" + Query + "\n\n")
    main()
    textarea.insert(END , "Bot:" + Reply + "\n\n")
    questionfield.delete(0 , END)
    textarea.yview(END)


# gui
root = Tk()

root.geometry('500x570+100+30')
root.resizable(0 , 0)
root.title("Covid 19 chat bot")
root.config(bg='rosybrown2')

# pic = PhotoImage(file='pic.png')
# picture_label = Label(root, image=pic, bg='black')
# picture_label.pack(side=TOP, pady=5)

center_frame = Frame(root)
center_frame.pack()

sc_bar = Scrollbar(center_frame)
sc_bar.pack(side=RIGHT , fill=Y)

textarea = Text(center_frame , font=('times new roman' , 15 , 'bold') , width=80 , height=10 ,
                yscrollcommand=sc_bar.set ,
                bg='gray90')
textarea.pack(side=LEFT , fill=BOTH)
# sc_bar.config(command=textarea.yview)

questionfield = Entry(root , font=('verdana' , 15 , 'italic') , bg='snow3')
questionfield.pack(fill=X , pady=15)

askphoto = PhotoImage(file='ask.png')
askbutton = Button(root , text="Send" , bd=10 , bg='LightBlue1' , cursor='hand2' ,
                   command=ask_clicked)  # activebackground='rosybrown2'
askbutton.pack()

mic = Button(root , bd=6 , text="mic" , command=mic_clicked)
mic.pack()

update_button = Button(root , text="Update")
update_button.pack()

root.mainloop()
