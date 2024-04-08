#code to detect markers on plant for arm to pick up
# to be completed 

import cv2
import numpy as np

arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)
arucoParams = cv2.aruco.DetectorParameters_create()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)
    
    if ids is not None and len(ids) > 0:
        ids = ids.flatten()
        
        for i, markerID in enumerate(ids):
            # calculate the centroid of the marker
            M = cv2.moments(corners[i][0])
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
            # draw bounding box and centroid
            cv2.aruco.drawDetectedMarkers(frame, corners)
            cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)
            cv2.putText(frame, str(markerID), (cX - 10, cY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        # when multiple markers are detected it continues to the next frame
        continue
    
    # if only one marker detected, treat it as a single marker against the background

    # display the resulting frame
    cv2.imshow('Frame', frame)
    
    #  press 'e' to break the loop
    if cv2.waitKey(1) & 0xFF == ord('e'):
        break

cap.release()
cv2.destroyAllWindows()
