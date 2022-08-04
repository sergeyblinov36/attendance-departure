import requests
from datetime import datetime

global status
status = 0
global startTime
idList = []
staff = requests.get("https://eyesave.herokuapp.com/staff")
children = requests.get("https://eyesave.herokuapp.com/children")


def unauthorized_departure(id):
    global status
    global startTime
    global staff
    url1 = "https://eye-save-notifications.herokuapp.com/escort/send/"
    query = f'https://eyesave.herokuapp.com/children/{id}'
    childData = requests.get(query)
    if status == 0:
        url = "https://eyesave.herokuapp.com/events/"
        now = datetime.now()
        startTime = now.strftime("%H:%M")
        date = now.strftime("%Y-%m-%d")
        data1 = {'_date': date,
                 '_startTime': startTime,
                 '_endTime': '',
                 '_duration': '',
                 '_eventType': 'Child Left Alone',
                 '_child1': id,
                 '_child2': '',
                 '_videoUrl': ''}
        request = requests.post(url, json=data1)
    child = childData.json()
    if status == 0:
        for el in staff.json():
            if "_telegramID" in el:
                message = f'Warning !!!! \n{child["_firstName"]} {child["_lastName"]} left the kindergarten alone'
                data = {"userId": el["_telegramID"],
                        "msg": message}
                request = requests.post(url1, json=data)
                print(request.text)
                startTime = datetime.now()
        status = 1
    elif status == 1:
        curr_time = datetime.now()
        duration = curr_time - startTime
        if duration.total_seconds() > 60:
            status = 0
           

