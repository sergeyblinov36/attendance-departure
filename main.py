from dis import code_info
import json

import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from findEncodings import findEncodings
from attendance import markAttendance, escortArrival
import time
import schedule
from event import unauthorized_departure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import requests
import json


def attendance():
    settings = requests.get("https://eyesave.herokuapp.com/settings/")
    finishTime = settings.json()[0]["_endPickUp"]
    # arrays of images, names and roles(child or staff member)
    images = []
    id_list = []
    role = []
    # paths to children, staff and escorts information
    children = requests.get("https://eyesave.herokuapp.com/children/")
    staff = requests.get("https://eyesave.herokuapp.com/staff/")
    escorts = requests.get("https://eyesave.herokuapp.com/escorts/")
    print(children.text)
    # add the children images to the images array, their ids to the id list and their role "child" to the role array
    for cl in children.json():
        print(cl['_imageUrl'])
        Img = None
        try:
            resp = urllib.urlopen(cl['_imageUrl'])
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            Img = cv2.imdecode(image, cv2.IMREAD_COLOR)
            images.append(Img)
            id_list.append(cl['_id'])
            role.append("child")
        except Exception as e:
            print(e)

    # add the staff images to the images array, their ids to the id list and their role "staff" to the role array
    for employee in staff.json():
        Img = None
        try:
            resp = urllib.urlopen(employee['_imageUrl'])
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            Img = cv2.imdecode(image, cv2.IMREAD_COLOR)
            images.append(Img)
            id_list.append(employee['_id'])
            role.append("staff")
        except Exception as e:
            print(e)

    # add the escorts images to the images array, their ids to the id list and their role "escort" to the role array
    for escort in escorts.json():
        Img = None
        try:
            resp = urllib.urlopen(escort['_imageUrl'])
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            Img = cv2.imdecode(image, cv2.IMREAD_COLOR)
            images.append(Img)
            id_list.append(escort['_id'])
            role.append("escort")
        except Exception as e:
            print(e)

    # encode the images
    encodeListKnown = findEncodings(images)

    camera = settings.json()
    cam = camera[0]['_cameraUrl1']
    cap = cv2.VideoCapture(cam)

    while True:
        success, img = cap.read()
        if success:
            id_found = []
            # resize and change colour of the live stream
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            # locate and encode faces from the frame
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    
            # compare the faces from the frame to the faces from the repositories
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)
                id_found.append(id_list[matchIndex])
    
                # if the faces match change the name to upper letters and draw the rectangle around the face
                if matches[matchIndex]:
                    idString = id_list[matchIndex]
    
                    # print(id)
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, idString, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    id = int(idString)
                    # mark attendance
                    if role[matchIndex] == "child":
                        markAttendance(id, "child")
                    elif role[matchIndex] == "staff":
                        markAttendance(id, "staff")
                    elif role[matchIndex] == "escort":
                        escortArrival(id)

            img = cv2.resize(img, (600, 500))
            cv2.imshow('Webcam', img)
            cv2.waitKey(1)
            if cv2.waitKey(1) & 0xFF == ord('q') or finishTime < datetime.now():
                break
                
        else:
            cap.release()
            time.sleep(60)
            cap = cv2.VideoCapture(cam)
    cap.release()
    cv2.destroyAllWindows()


def main():
    settings = requests.get("https://eyesave.herokuapp.com/settings/")
    startTime = settings.json()
    schedule.every().sunday.at(startTime[0]["_startPickUp"]).do(attendance)
    schedule.every().monday.at(startTime[0]["_startPickUp"]).do(attendance)
    schedule.every().tuesday.at(startTime[0]["_startPickUp"]).do(attendance)
    schedule.every().wednesday.at(startTime[0]["_startPickUp"]).do(attendance)
    schedule.every().thursday.at(startTime[0]["_startPickUp"]).do(attendance)
    while True:
        schedule.run_pending()
        print("sleeping")
        time.sleep(1)


if __name__ == '__main__':
    main()


