from datetime import datetime
import requests
import json
from event import unauthorized_departure


def markAttendance(id, role):
    now = datetime.now()
    dString = now.strftime("%Y-%m-%d")
    tString = now.strftime("%H:%M")
    departureTime = now.replace(hour=1, minute=0, second=0, microsecond=0)
    # the jsons are saved in different repositories
    if role == "child":
        url = "https://eyesave.herokuapp.com/childrenAttendance/"
        query = "_childId"
        path = requests.get(url)
    elif role == "staff":
        url = "https://eyesave.herokuapp.com/staffAttendance/"
        query = "_employeeId"
        path = requests.get(url)
    found = False
    for element in path.json():
        if element[query] == id:
            if element["_date"] == dString:
                found = True
                if element["_escortArrival"]:
                    url = "https://eyesave.herokuapp.com/childrenAttendance/"
                    url1 = f'{url}{element["_id"]}'
                    data = {
                        "_departureTime": tString
                    }
                    request = requests.put(url1, json=data)
                else:
                    unauthorized_departure(id)
    if not found:
        print("what to do if attendance wasn't marked")
        # createData(id, role, path)


def createData(id, role, path):
    now = datetime.now()
    dString = now.strftime("%Y-%m-%d")
    tString = now.strftime("%H:%M")

    if role == "child":
        url = "https://eyesaveserver.herokuapp.com/childrenAttendance/"
        data = {"_childId": int(id),
                "_date": dString,
                "_arrivalTime": tString,
                "_departureTime": "",
                "_absence": False,
                "_childDelay": False,
                "_escortDelay": False}
        request = requests.post(url, json=data)
        print(request.text)
    if role == "staff":
        url = "https://eyesaveserver.herokuapp.com/staffAttendance/"
        data = {"_employeeId": int(id),
                "_date": dString,
                "_arrivalTime": tString,
                "_departureTime": "",
                }
        request = requests.post(url, json=data)
        print(request.text)


def escortArrival(id):
    url = f'https://eyesave.herokuapp.com/escorts/{id}'
    escortData = requests.get(url)
    data = {
        "_escortArrival": True
    }
    date = datetime.now()
    dateSTR = date.strftime("%Y-%m-%d")
    escort = escortData.json()
    for element in escort["_children"]:
        query = f'https://eyesave.herokuapp.com/childrenAttendance/{dateSTR}/children/{element}'
        req = requests.put(query, json=data)
        print(req.text)
