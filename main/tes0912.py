def get_frame(self):
        global cmmd, largeBlob #to passing the value command if blink detected
        
        face_cascade = cv2.CascadeClassifier('static/assets/haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier('static/assets/haarcascade_eye.xml')
        
        retval,frame=self.video.read()

        #Converting the recorded image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #Applying filter to remove impurities
        gray = cv2.bilateralFilter(gray,5,1,1) 
        pupilFrame = frame
        #Detecting the face for region of image to be fed to eye classifier
        faces = face_cascade.detectMultiScale(gray, 1.3, 5,minSize=(200,200))
        if(len(faces)>0):
            for (x,y,w,h) in faces:
                #roi_face is face which is input to eye classifier
                roi_face = gray[y:y+h,x:x+w]
                roi_color = frame[y:y+h,x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_face,1.3,5,minSize=(50,50))
                
                if len(eyes)==0 :
                    cv2.putText(frame,"Blink Detected!", (70,70),cv2.FONT_HERSHEY_PLAIN, 3,(0,255,0),2)
                    # cmmd=1 
                    blinkdetect.valcommand(1)
                    # cv2.waitKey(200) #pause the function for halfsec, to avoid overlapped command
                
                # if len(eyes)==1 :
                #     blinkdetect.valcommand(2)

                for (ex,ey,ew,eh) in eyes:
                    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(255,255,255),2)
                    #Examining the length of eyes object for eyes
                    if(len(eyes)>=2):
                        # cv2.putText(frame,"Eyes open!", (70,70),cv2.FONT_HERSHEY_PLAIN, 2,(255,255,255),2)
                        # cmmd=0
                        blinkdetect.valcommand(0)

                    #draw crossline
                    # cv2.line(roi_color, (ex,ey), ((ex+ew,ey+eh)), (0,0,255),1)
                    # cv2.line(roi_color, (ex+ew,ey), ((ex,ey+eh)), (0,0,255),1)
                    kernel = np.ones((1, 1), np.uint8) #DLIB
                    pupilFrame = cv2.equalizeHist(roi_face[int(ey+(eh*.25)):(ey+eh), ex:(ex+ew)])
                    pupilFrame = cv2.bilateralFilter(pupilFrame, 10, 15, 15) #DLIB
                    pupilFrame = cv2.erode(pupilFrame, kernel, iterations=3) #DLIB
                    pupilFrame = cv2.threshold(pupilFrame, 70, 255, cv2.THRESH_BINARY)[1] #DLIB #50 ..nothin 70 is better
                    
                    # ret, pupilFrame = cv2.threshold(pupilFrame,55,255,cv2.THRESH_BINARY)		#50 ..nothin 70 is better
                    # pupilFrame = cv2.morphologyEx(pupilFrame, cv2.MORPH_CLOSE, kernel)
                    # pupilFrame = cv2.morphologyEx(pupilFrame, cv2.MORPH_ERODE, kernel)
                    # pupilFrame = cv2.morphologyEx(pupilFrame, cv2.MORPH_OPEN, kernel)

                    threshold = cv2.inRange(pupilFrame,250,255)		#get the blobs
                    contours, hierarchy = cv2.findContours(threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
                    
                    if len(contours) >= 2:
                        maxArea = 0
                        MAindex = 0			#to get the unwanted frame 
                        distanceX = []		#delete the left most (for right eye)
                        currentIndex = 0 
                        for cnt in contours:
                            area = cv2.contourArea(cnt)
                            center = cv2.moments(cnt)
                            if center['m00'] != 0:
                                cx = int(center["m10"] / center["m00"])
                                cy = int(center["m01"] / center["m00"])
                            else:
                                cx,cy = 0, 0
                            distanceX.append(cx)	
                            if area > maxArea:
                                maxArea = area
                                MAindex = currentIndex
                            currentIndex = currentIndex + 1
                            contours=list(contours)
                        del contours[MAindex]		#remove the picture frame contour
                        tuple(contours)
                        del distanceX[MAindex]
                    
                    eye = 'right'

                    if len(contours) >= 2:		#delete the left most blob for right eye
                        if eye == 'right':
                            edgeOfEye = distanceX.index(min(distanceX))
                        else:
                            edgeOfEye = distanceX.index(max(distanceX))	
                        del contours[edgeOfEye]
                        del distanceX[edgeOfEye]

                    if len(contours) >= 1:		#get largest blob
                        maxArea = 0
                        for cnt in contours:
                            area = cv2.contourArea(cnt)
                            if area > maxArea:
                                maxArea = area
                                largeBlob = cnt

                    if len(largeBlob) > 0:	
                        center = cv2.moments(largeBlob)
                        cx,cy = int(center['m10']/center['m00']), int(center['m01']/center['m00'])
                        cv2.circle(pupilFrame,(cx,cy),5,255,-1)
                        # Hframe=int(eh)/2 #get center value from eyes height
                        if cy <= 5 : #sesuaikan lagi (12-13 dalam cahaya kurang)(15-17 dalam cahaya baik)
                            cv2.putText(frame,"Looking Up",(450,30), cv2.FONT_HERSHEY_PLAIN, 1,(0,0,255),2,cv2.LINE_AA)
                            # cmmd=2
                            blinkdetect.valcommand(2)
                            # cv2.waitKey(200) #pause the function for halfsec, to avoid overlapped command

        else: 
            cv2.putText(frame,"No face detected",(100,100),cv2.FONT_HERSHEY_PLAIN, 3,(0,0,255),2)
            # cmmd=3 #value for face not detected
            blinkdetect.valcommand(3) 
        cv2.waitKey(200)
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
