import cv2
from cv2 import aruco
import numpy as np

cap = cv2.VideoCapture(1)

dict       = aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
arucoParams = cv2.aruco.DetectorParameters()

arucoParams.polygonalApproxAccuracyRate = 0.15 #0.04
arucoParams.minDistanceToBorder = 0
arucoParams.maxErroneousBitsInBorderRate = 1



detector = cv2.aruco.ArucoDetector(dict, arucoParams)
print(detector.getDetectorParameters().minMarkerDistanceRate)



while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #detector.detectMarkers(gray, corners=corners, ids=ids)

    corners, ids, rejected = detector.detectMarkers(gray)

    cv2.aruco.drawDetectedMarkers(gray, corners, ids)
    #cv2.aruco.drawDetectedMarkers(frame, corners, ids)


    cv2.imshow('frame', gray)

    command = cv2.waitKey(1)&0xFF
    if command == ord('q'):
        break
    elif command == ord('p'):
        cv2.imwrite("img1.jpg",frame)
		
cap.release()
cv2.destroyAllWindows()