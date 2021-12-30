# from django.db.models.fields.files import FileField
# from django.forms import widgets
# from django.http import HttpResponse
from django.shortcuts import redirect, render
from django import forms
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
from datetime import date
from django.core.files.storage import FileSystemStorage
from django.http.response import HttpResponse
from django.http import JsonResponse
from io import StringIO
import os


from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


import cv2
import math
import dlib
import threading
import numpy as np
from django.views.decorators.csrf import csrf_exempt
# from main.gaze import GazeTracking

# Create your views here.

class uploadFile(forms.Form):
    def __init__(self,*args,**kwargs):
        super(uploadFile,self).__init__(*args,**kwargs)
        self.fields['docpdf'] = forms.FileField()
    docpdf = forms.FileField()

def index(request):
    if request.method == 'POST' :
        form=uploadFile()
        if form.is_valid():
            pass
    else:
        form=uploadFile()

    context = {
        "data" : [1, 2, 3, 4, 5, 6],
        "form" : form
    }
    return render(request,'index.html', context)

# def extract(request):
    # content = ""
    # pdfFile = open('static/docs/Document1.pdf', 'rb')
    # pdf = PyPDF2.PdfFileReader(pdfFile)
    # num_pages = pdf.getNumPages()
    # for i in range(0, num_pages):
	#     pageObj = pdf.getPage(i)
 	#    content = pageObj.extractText()
     # for i in range(0, num_pages):
     #     content += pdf.getPage(i).extractText() + "\n"
     # content = " ".join(content.replace(u"\xa0", " ").strip().split())
    # context = {'file_content': content}
     #return render(request,'readerpage.html', context)

class choosePage(forms.Form):
    def __init__(self,pageChoice,upload_date,*args,**kwargs):
        super(choosePage,self).__init__(*args,**kwargs)
        self.fields['pagenum'] = forms.ChoiceField(label='',choices=pageChoice,widget=forms.Select(attrs={'class': 'form-select form-select-lg mb-3'}))
        # self.fields['pagenum'].widget=forms.Select(attrs={'class': 'form-select form-select-lg mb-3'})
        # self.pages=pageChoice
        self.fields['filename'].widget = forms.HiddenInput(attrs={'value': upload_date})

    pagenum = forms.ChoiceField()
    # filename = forms.HiddenInput()
    filename = forms.CharField( 
        widget=forms.HiddenInput()
    )

def extract(request):
#----------------
    if request.method == 'POST':
        pdf = request.FILES['docpdf']
        fs = FileSystemStorage()
        fs.save(pdf.name, pdf)

        fp = open(os.path.join('docs/')+pdf.name, 'rb')
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # upload_date = date.today()
        page_no = 0
        totalPage = []
        for pageNumber, page in enumerate(PDFPage.get_pages(fp)):
            if pageNumber == page_no:
                interpreter.process_page(page)
                data = retstr.getvalue()
                with open(os.path.join('static/docs/', f'{pdf.name} page {page_no}.txt'), 'wb') as file:
                    file.write(data.encode('utf-8'))
                data = ''
                retstr.truncate(0)
                retstr.seek(0)
            totalPage.append(page_no)
            page_no += 1

        #creating the choices for choiceField in form
        pageChoice=(())
        y=[]
        for i in totalPage:
            x=[]
            for j in range(1):
                x.append(str(i))
                x.append('Page '+str(i+1))
            y.append(tuple(x))
        
        pageChoice = tuple(y)
        filename = pdf.name

        if request.method == 'POST':
            form =  choosePage(pageChoice,filename)
            if form.is_valid():
                pass  # does nothing, just trigger the validation
        else:
            form=choosePage(pageChoice,filename)

        context = {'form_page':form}
        return render(request,'choosepage.html', context)
    else:
        return redirect('/')

def writepage(request):
    if request.method == 'POST':
        pagenum = request.POST['pagenum']
        filename = request.POST['filename']
        file_path = 'static/docs/'+filename+' page '+pagenum+'.txt'
        text = []
        with open(file_path) as file:
            for item in file:
                text.append(item)
        context = {'file_content': text, 'enter':'\n'}
        return render(request,'readerpage.html', context)
    else:
        return redirect('/')


#--------EYE TRACK START FROM HERE-------------------

BLINK_RATIO_THRESHOLD = 5.7 #or 3.8?5.7
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('static/assets/shape_predictor_68_face_landmarks.dat')
val=[0]
from main.eye import Eye
from main.calibration import Calibration

class GazeTracking(object):

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration()

    @property
    def pupils_located(self):
        """Check that the pupils have been located"""
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            return False
            
    def _analyze(self):
        """Detects the face and initialize Eye objects"""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = detector(frame)

        try:
            landmarks = predictor(frame, faces[0])
            self.eye_left = Eye(frame, landmarks, 0, self.calibration)
            self.eye_right = Eye(frame, landmarks, 1, self.calibration)

        except IndexError:
            self.eye_left = None
            self.eye_right = None

    def refresh(self, frame):
        """Refreshes the frame and analyzes it.
        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        self._analyze()

    def pupil_left_coords(self):
        """Returns the coordinates of the left pupil"""
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def pupil_right_coords(self):
        """Returns the coordinates of the right pupil"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)

    def vertical_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        vertical direction of the gaze. The extreme top is 0.0,
        the center is 0.5 and the extreme bottom is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.y / (self.eye_left.center[1] * 2 - 10)
            pupil_right = self.eye_right.pupil.y / (self.eye_right.center[1] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def is_up(self):
        """Returns true if the user is looking to the up"""
        if self.pupils_located:
            return self.vertical_ratio() <= 0.6 #0.5-0.6
    
    def is_blinking(self):
        """Returns true if the user closes his eyes"""
        if self.pupils_located:
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking) / 2
            return blinking_ratio > 5.7 #3.8

    def annotated_frame(self):
        """Returns the main frame with pupils highlighted"""
        frame = self.frame.copy()

        if self.pupils_located:
            color = (0, 0, 255)
            x_left, y_left = self.pupil_left_coords()
            x_right, y_right = self.pupil_right_coords()
            cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), color)
            cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), color)
            cv2.line(frame, (x_right - 5, y_right), (x_right + 5, y_right), color)
            cv2.line(frame, (x_right, y_right - 5), (x_right, y_right + 5), color)

        return frame

# class blinkdetect(object):

    # def __init__(self): 
    #     self.video = cv2.VideoCapture(0+cv2.CAP_DSHOW) # (0+cv2.CAP_DSHOW)built-in cam ; (2) droidcam; (3) webcam
    #     (self.grabbed, self.frame)=self.video.read()
    #     self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    #     threading.Thread(target=self.update, args=()).start()
 
    # def __del__(self):
    #     self.video.release()
    #     # cv2.destroyAllWindows() 
    
    # def update(self):
    #     while True:
    #         if self.video.isOpened():
    #             (self.status, self.frame) = self.video.read()

    # def valcommand(cmmd):
    #     if (cmmd<4):
    #         val.insert(0, cmmd)
    #         del val[1]
    #     else :
    #         return val[0]

    # def get_frame(self):
    #     global cmmd #to passing the value command if blink detected
    #     cmmd=0

    #     #these landmarks are based on the image above 
    #     left_eye_landmarks  = [36, 37, 38, 39, 40, 41]
    #     right_eye_landmarks = [42, 43, 44, 45, 46, 47]
        
    #     retval, frame = self.video.read()
    #     # frame = cv2.flip(frame,1) ---mirroring video

    #     #--------------GAZE DETECTOR---------------
    #     gaze = GazeTracking()
    #     gaze.refresh(frame)
    #     frame = gaze.annotated_frame() #draw line in pupil
    #     blinkdetect.valcommand(0)
    #     if  gaze.is_blinking():
    #     #Blink detected! Do Something!
    #         cv2.putText(frame,"BLINKING",(10,50), cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),2,cv2.LINE_AA)
    #         blinkdetect.valcommand(1)
    #     elif gaze.is_up():
    #         text = "Looking up"
    #         cv2.putText(frame, text, (10,50), cv2.FONT_HERSHEY_SIMPLEX,2,(255,255,255),2,cv2.LINE_AA)
    #         blinkdetect.valcommand(2)
    #     else: 
    #         blinkdetect.valcommand(0)
    #         # cv2.putText(frame,"No face detected",(100,100),cv2.FONT_HERSHEY_PLAIN, 3,(0,0,255),2)
    #         # # cmmd=3 #value for face not detected
    #         # blinkdetect.valcommand(3) 

    #     cv2.waitKey(1)
    #     _, jpeg = cv2.imencode('.jpg', frame)
    #     return jpeg.tobytes()

def send_file_data(data, mimetype='image/jpeg', filename='output.jpg'):
    # https://stackoverflow.com/questions/11017466/flask-to-return-image-stored-in-database/11017839

    response = HttpResponse(data)
    response['Content-Type']=mimetype
    response['Content-Disposition']= 'attachment; filename="output.jpeg"'
    return response

def valcommand(cmmd):
    if (cmmd<4):
        val.insert(0, cmmd)
        del val[1]
    else :
        return val[0]

@csrf_exempt 
def upload(request):
    if request.method == 'POST':
        fs = request.FILES.get('snap')
        if fs:
            img = cv2.imdecode(np.frombuffer(fs.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            gaze = GazeTracking()
            gaze.refresh(img)
            frame = gaze.annotated_frame() #draw line in pupil
            valcommand(0)
            if  gaze.is_blinking():
                cv2.putText(frame,"BLINKING",(10,50), cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),2,cv2.LINE_AA)
                valcommand(1)
            elif gaze.is_up():
                text = "Looking up"
                cv2.putText(frame, text, (10,50), cv2.FONT_HERSHEY_SIMPLEX,2,(255,255,255),2,cv2.LINE_AA)
                valcommand(2)
            # frame = cv2.resize(frame, (150,100),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
            ret, buf = cv2.imencode('.jpg', frame)
            return send_file_data(buf.tobytes())
    return redirect('/')

#to grab the camera object
# def gen():
#     while True:
#         camera=blinkdetect()
#         frame=camera.get_frame()
#         # print(cmmd)
#         yield(b'--frame\r\n'
#         b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n\r\n')

#get the blink command
def command(request):
    # p=blinkdetect()
    value=valcommand(4) # 4 define not a command value    
    command= {'value':value}
    return JsonResponse(command,safe=False)

#load camera
# @gzip.gzip_page
# def camera(request):
#     # cam = blinkdetect()
#     return StreamingHttpResponse(gen(), content_type="multipart/x-mixed-replace;boundary=frame")

#-----------end of eye-tracker-----------------#