
# https://stackoverflow.com/questions/49978705/access-ip-camera-in-python-opencv

from tkinter import *
from PIL import Image as Img
import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox
from imutils.video import WebcamVideoStream
import time
from PIL import ImageTk
import threading
import imutils
import cv2
import os
import pickle
import face_recognition
import MySQLdb as db
from datetime import datetime
from functools import partial
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class FaceDetection:
    
    def __init__(self):
        
        self.vs = None
        self.frame = None
        self.thread = None
        self.stopThread = None
        self.topview = None
        self.cur = 0
        
        self.root = tk.Tk()
        self.root.iconbitmap('icon.ico')
        self.root.configure(background='white')

        # Take laptop screen width and height
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        self.width_of_window = self.screen_width/2
        self.height_of_window = self.screen_height
        
        self.x = (self.screen_width / 2) - (self.width_of_window/2)
        self.y = (self.screen_height / 2) - (self.height_of_window/2)
        
        self.root.wm_attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.end_fullscreen)
        
        self.mainframe = Frame(self.root, bd=5,width=self.screen_width,height=self.screen_height, bg="#FFFFFF")
        self.mainframe.pack()
        self.mainframe.propagate(0)

        
        self.leftFrame = Frame(self.mainframe,bg="#FFFFFF",width=self.screen_width/4,
                               height=self.screen_height,relief=RIDGE)
        self.leftFrame.grid(row=0,column=0)
        
        self.centerFrame = Frame(self.mainframe,bg="#FFFFFF",width=self.screen_width/2,
                                 height=self.screen_height,relief=RIDGE)
        self.centerFrame.grid(row=0,column=1)
        
        self.bg = ImageTk.PhotoImage( file = "back_ground.png") 
        self.bklabel = Label(self.centerFrame, image = self.bg,width=self.screen_width/2,
                             height=self.screen_height,bg="#FFFFFF")
        self.bklabel.grid(row=0,column=1)
        
        self.rightFrame = Frame(self.mainframe,bg="#FFFFFF",width=self.screen_width/4,
                                height=self.screen_height,relief=RIDGE)
        self.rightFrame.grid(row=0,column=2)
        
        attendanceBtn = Button(self.leftFrame, text="ATTENDANCE",width=20,
                               height=2,bg='#222654',fg='#FFFFFF', command=self.Attendance_register)
        attendanceBtn.grid(row=0,column=0)
        
        demoBtn = Button(self.rightFrame, text="VIEW ATTENDANCE",width=20,
                         height=2,bg='#222654',fg='#FFFFFF', command=self.view_attendance)
        demoBtn.grid(row=0,column=2)
        
        self.panel = None
        
        self.data = pickle.loads(open("encodings.pickle", "rb").read())
        self.detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        
        # control title and close button of window
        self.root.wm_title("Auro University Attendence System")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
    
    def end_fullscreen(self,event=None):
        
        self.root.wm_attributes("-fullscreen", False)
        
    def dbconnection(self):
        try:
            con = db.connect(host="localhost",database="attendance_system",password="P@tely@sh07",user="root")
            cursor =con.cursor()
            return con,cursor
        except:
            print("Database connection is failed...")
            
    def insert_attendance(self,fid):
        
        attendance = 'P'
        today_date = datetime.today().strftime('%Y-%m-%d')
        time_in = datetime.now()
        
        con,cursor = self.dbconnection()        
        query = "insert into facultyattendance(facultyid,attendance,time_in,date) values ('%d','%s','%s','%s')"
        arg = (int(fid),attendance,time_in,today_date)
        
        try: 
            cursor.execute(query % arg)
            con.commit()
            return True
        except:
            
            con.rollback()
            print('Insertion problem...')
            return False
        finally:
            cursor.close()
            con.close()
            
    def update_attendance(self,fid):
        
        time_out = datetime.now()
        today_date = datetime.today().strftime('%Y-%m-%d')
        
        con,cursor = self.dbconnection()        
        query = "update facultyattendance set time_out = '%s' where facultyid = %d and date = '%s'"
        arg = (time_out,int(fid),today_date)
        
        try: 
            cursor.execute(query % arg)
            con.commit()
            return True
        except:
            
            con.rollback()
            print('Updation problem...')
            return False
        finally:
            cursor.close()
            con.close()
        
    def check_record(self,fid):
        
        query = "select * from facultyinfo where facultyid = %d"
        arg = (int(fid))
        con,cursor = self.dbconnection()
        try:
            cursor.execute(query % arg)
            record = cursor.fetchone()
            
            if record is not None:
                return record
            else:
                return None
        except:
            print('Checking in record problem...')
        finally:
            cursor.close()
            con.close()
            
    def count_present_days(self,fid,fromdate,todate):
        
        query = "select * from facultyattendance where facultyid = %d and date >= '%s' and date <= '%s' and attendance = '%s' "
        arg = (int(fid),fromdate,todate,'P')
        
        con,cursor = self.dbconnection()
        try:
            cursor.execute(query % arg)
            cursor.fetchall()
            return cursor.rowcount
        except:
            print('Checking in record problem...')
        finally:
            cursor.close()
            con.close()

    def check_present_registered(self,fid):
        
        today_date = datetime.today().strftime('%Y-%m-%d')
        query = "select * from facultyattendance where facultyid = %d and date = '%s'"
        
        arg = (int(fid),today_date)
        con,cursor = self.dbconnection()
        try:
            cursor.execute(query % arg)
            record = cursor.fetchone()
            if record is not None:
                return record
            else:
                return None
        except:
            print('Checking in record problem...')
        finally:
            cursor.close()
            con.close()
            
    def get_attendance_record(self,fid,fromdate,todate):
        
        query = "select * from facultyattendance where facultyid = %d and date >= '%s' and date <= '%s' "
        
        arg = (int(fid),fromdate,todate)
        con,cursor = self.dbconnection()
        try:
            cursor.execute(query % arg)
            record = cursor.fetchall()
            if record is not None:
                return record
            else:
                return None
        except:
            print('Getting record problem...')
        finally:
            cursor.close()
            con.close()
                
    def Attendance_register(self):
        
        cur = self.dbconnection()
        self.stopThread = True
        self.thread = threading.Thread(target=self.videoFraming, args=())
        self.thread.start()
    #createa video frame through threading
    def videoFraming(self):
        
        try:
            self.vs = cv2.VideoCapture(0)
            #time.sleep(2.0)
            
            while self.stopThread:
    
                _,self.frame = self.vs.read()
                self.frame = cv2.resize(self.frame,(500,350))
                
                # detect a face from frame
                rgb, name = self.faceDetect()
                
                # check face detects or not
                if rgb is not None:
                    
                    image = Img.fromarray(rgb)
                    image = ImageTk.PhotoImage(image) # convert image or frame into bitmap

                    if self.panel is None:
                        # Put frame into panel  
                        self.panel = tk.Label(self.centerFrame, image=image,width=self.screen_width/2,
                                              height=self.screen_height,bg="#FFFFFF")
                        self.panel.image = image
                        self.panel.grid(row=0,column=1)

                        # check record inserted or not
                        if self.cur != 1:
                            if name != "Unknown":
                                # check detected face available or not in database
                                check = self.check_record(name)
                                if check is not None:
                                    # check Time in present done or not for that specific date
                                    check_registered = self.check_present_registered(name)
                                    if check_registered is None:
                                        # confirmed to user that detected face is himself / herself
                                        result = messagebox.askquestion("Confirmation Box", "Are you "+ check[1] + ' ?')
                                        if result == 'yes':
                                            # insert record or morning present
                                            insertcheck = self.insert_attendance(name)
                                            if insertcheck:
                                                msg = "Your IN time is registered..."
                                                self.displayMsg(msg)
                                                self.cur = 1
                                                self.handleException()
                                            else:
                                                msg = "Please try again..."
                                                self.displayMsg(msg)
                                                self.handleException()
                                        else:
                                            msg = "Please try again..."
                                            self.displayMsg(msg)
                                            self.handleException()
                                    else:
                                        # verify person is same with detected face to user
                                        result = messagebox.askquestion("Confirmation Box", "Are you "+ check[1] + ' ?')
                                        if result == 'yes':
                                            # store Time OUT record 
                                            result1 = messagebox.askquestion("Confirmation Box", "Are you going to home?")
                                            if result1 == 'yes':
                                                updationcheck = self.update_attendance(name)
                                                if updationcheck:
                                                    msg = "Your OUT time is registered..."
                                                    self.displayMsg(msg)
                                                    self.cur = 1
                                                    self.handleException()
                                                else:
                                                    msg = "Please try again..."
                                                    self.displayMsg(msg)
                                                    self.handleException()
                                            else:
                                                self.handleException()
                                        else:
                                            msg = "Please try again..."
                                            self.displayMsg(msg)
                                            self.handleException()
                                else:
                                    msg = "No record found with your face..."
                                    self.displayMsg(msg)
                                    self.handleException()
                            else:
                                msg = "No record found with your face..."
                                self.displayMsg(msg)
                                self.handleException()
                    else:
                        self.panel.configure(image=image)
                        self.panel.image = image
                
                    self.stopThread = False
                else:
                    self.handleException()

                cv2.waitKey(5)

        except RuntimeError :
            msg = "There is a problem in camera. Kindly inform to management..."
            self.displayMsg(msg)
               
    def faceDetect(self):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            
        rects = self.detector.detectMultiScale(gray, scaleFactor=1.1, 
                                          minNeighbors=5, minSize=(50, 50),
                                          flags=cv2.CASCADE_SCALE_IMAGE)

        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
        # compare encoded detected faces 
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        
        if len(encodings) > 0:
            # compare encoded faces to detected faces
            matches = face_recognition.compare_faces(self.data["encodings"], encodings[0])
            name = "Unknown"

            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matchedIdxs:
                    name = self.data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                name = max(counts, key=counts.get)

            names.append(name)
        
            
        for ((top, right, bottom, left), name) in zip(boxes, names):
            cv2.rectangle(rgb, (left, top), (right, bottom),
                (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15

        if len(names) == 0:
            msg = "Your face is not detected. Please try again..."
            self.displayMsg(msg)
            self.handleException()
            return None,None
        else:
            #self.handleException()
            return rgb, names[0]
        
    def verify_face(self):
        try:
            self.vs = cv2.VideoCapture(0)
            time.sleep(2.0)
            
            while self.stopThread:
               
                _ , self.frame = self.vs.read()
                self.frame = cv2.resize(self.frame,(500,350))
                
                # detect a face from frame
                _, name = self.faceDetect()
                # check record inserted or not
                if self.cur != 1:
                    if name != "Unknown":
                        # check detected face available or not in database
                        check = self.check_record(name)
                        if check is not None:
                            # confirmed to user that detected face is himself / herself
                            result = messagebox.askquestion("Confirmation Box", "Are you "+ check[1] + ' ?',parent=self.topview)
                            if result == 'yes':
                                return name
                            else:
                                return 'no'
                                self.handleException()
                        else:
                            self.handleException()
                            return None
                    else:
                        self.handleException()
                        return None
                
        except RuntimeError:
            msg = "There is a problem in camera. Kindly inform to management..."
            self.displayMsg(msg)

    def onClose(self):
        cv2.destroyAllWindows()
        if self.vs is not None:
            #self.vs.stream.release()
            #self.vs.stop()
            self.vs.release()
            pass

        self.stopThread = False
        self.root.destroy()
        #cv2.destroyAllWindows()
        
    def handleException(self):
        
        #cv2.destroyAllWindows()
        self.stopThread = False

        if self.vs is not None:
            # self.vs.stream.release()
            # self.vs.stop()
            self.vs.release()
            pass

        # clear all the widgets of that particular frame
        for widget in self.centerFrame.winfo_children():
            widget.destroy()

        self.centerFrame.pack_forget()
        
        self.mainframe['width'] = self.screen_width
        self.leftFrame['width'] = self.screen_width/4
        self.centerFrame['width'] = self.screen_width/2
        self.rightFrame['width'] = self.screen_width/4
        
        self.mainframe['height'] = self.screen_height
        self.leftFrame['height'] = self.screen_height
        self.centerFrame['height'] = self.screen_height
        self.rightFrame['height'] = self.screen_height
        
        # change background to white
        self.bklabel = Label(self.centerFrame, image = self.bg,width=self.screen_width/2,
                             height=self.screen_height,bg="#FFFFFF")
        self.bklabel.grid(row=0,column=1)

        self.cur = 0
        self.panel = None
        
    def displayMsg(self,msg):
        # create custom message box
        top = Toplevel(self.root)
        
        self.screen_width = self.root.winfo_screenwidth() # take laptop screen width
        self.screen_height = self.root.winfo_screenheight() # take laptop screen width
        
        self.width_of_window = self.screen_width/5
        self.height_of_window = self.screen_height/7
        
        self.x = (self.screen_width / 2) - (self.width_of_window/2)
        self.y = (self.screen_height / 2) - (self.height_of_window/2)
        
        # display in center
        top.geometry("%dx%d+%d+%d" % (self.width_of_window,self.height_of_window,self.x,self.y))
        top.title('Message Box')
        Message(top, text=msg, padx=20, pady=20).pack()
        top.after(2000, top.destroy) # automatically disappear in 2 sec
        
    def alertMsg(self,msg,parent):
        # create custom message box
        top = Toplevel(parent)
        
        self.screen_width = self.root.winfo_screenwidth() # take laptop screen width
        self.screen_height = self.root.winfo_screenheight() # take laptop screen width
        
        width_of_window = self.screen_width/5
        height_of_window = self.screen_height/7
        
        x = (self.screen_width / 2) - (width_of_window/2)
        y = (self.screen_height / 2) - (height_of_window/2)
        
        # display in center
        top.geometry("%dx%d+%d+%d" % (width_of_window,height_of_window,x,y))
        top.title('Message Box')
        Message(top, text=msg, padx=20, pady=20).pack()
        top.after(2000, top.destroy) # automatically disappear in 2 sec
            
    def view_attendance(self):
        
        # create custom message box
        self.topview = Toplevel(self.root)
        
        screen_width = self.root.winfo_screenwidth() # take laptop screen width
        screen_height = self.root.winfo_screenheight() # take laptop screen width
        
        width_of_window = 540
        height_of_window = 400
        
        x = (screen_width / 2) - (width_of_window/2)
        y = (screen_height / 2) - (height_of_window/2)
        
        # display in center
        self.topview.geometry("%dx%d+%d+%d" % (width_of_window,height_of_window,x,y))
        self.topview.iconbitmap('icon.ico')
        self.topview.title("Attendance report card")
        
        fromlabel = Label(self.topview,text="FROM: ")
        fromlabel.grid(row=0,column=0)
        
        self.frommonth_val = '01'
        frommonth = ttk.Combobox(self.topview, width = 5,state="readonly", 
                                 values= ['01','02','03','04','05','06','09','10','11','12'])       
        frommonth.grid(row = 0,column=1, padx=5,pady=5) 
        frommonth.current(0)
        frommonth.bind("<<ComboboxSelected>>",self.frommonthfunc)
        
        self.fromdays_val = '01'
        fromdays = ttk.Combobox(self.topview, width = 5,state="readonly",
                                values= ['01','02','03','04','05','06','09','10','11','12','13','14','15','16',
                                                    '17','18','19','20','21',
                                         '22','23','24','25','26','27','28','29','30','31'])       
        fromdays.grid(row = 0,column=2, padx=5,pady=5) 
        fromdays.current(0)
        fromdays.bind("<<ComboboxSelected>>",self.fromdaysfunc)

        
        self.fromyear_val = '2020'
        fromyear = ttk.Combobox(self.topview, width = 5,state="readonly", 
                                values= ['2020','2021','2022','2023','2024','2025'])       
        fromyear.grid(row = 0,column=3, padx=5,pady=5) 
        fromyear.current(0)
        fromyear.bind("<<ComboboxSelected>>",self.fromyearfunc)
        
        tolabel = Label(self.topview,text="TO: ")
        tolabel.grid(row=0,column=4)
        
        self.tomonth_val = '01'
        tomonth = ttk.Combobox(self.topview, width = 5,state="readonly",
                               values= ['01','02','03','04','05','06','09','10','11','12'])       
        tomonth.grid(row = 0,column=5, padx=5,pady=5) 
        tomonth.current(0)
        tomonth.bind("<<ComboboxSelected>>",self.tomonthfunc)
        
        self.todays_val ='01'
        todays = ttk.Combobox(self.topview, width = 5,state="readonly",
                              values= ['01','02','03','04','05','06','09','10','11','12','13','14','15','16',
                                                    '17','18','19','20','21','22','23',
                                       '24','25','26','27','28','29','30','31'])       
        todays.grid(row = 0,column=6, padx=5,pady=5) 
        todays.current(0)
        todays.bind("<<ComboboxSelected>>",self.todaysfunc)
        
        self.toyear_val = '2020'
        toyear = ttk.Combobox(self.topview, width = 5,state="readonly", 
                              values= ['2020','2021','2022','2023','2024','2025'])       
        toyear.grid(row = 0,column=7, padx=5,pady=5) 
        toyear.current(0)
        toyear.bind("<<ComboboxSelected>>",self.toyearfunc)
        
        searchBtn = Button(self.topview, text="SEARCH",width=8,height=1,bg='#222654',fg='#FFFFFF',
                           command=self.treeview_recorddisp)
        searchBtn.grid(row=0,column=8,padx=5,pady=5)
        
    def frommonthfunc(self,event):
        self.frommonth_val = event.widget.get()
    
    def fromdaysfunc(self,event):
        self.fromdays_val = event.widget.get()
        
    def fromyearfunc(self,event):
        self.fromyear_val = event.widget.get()
        
    def tomonthfunc(self,event):
        self.tomonth_val = event.widget.get()
    
    def todaysfunc(self,event):
        self.todays_val = event.widget.get()
        
    def toyearfunc(self,event):
        self.toyear_val = event.widget.get()
        
    def treeview_recorddisp(self):
        
        self.fromdate = self.fromyear_val + '-' + self.frommonth_val + '-' + self.fromdays_val
        self.todate = self.toyear_val + '-' + self.tomonth_val + '-' + self.todays_val
        
        
        cur = self.dbconnection()
        self.stopThread = True
        faceid = self.verify_face()
        
        if faceid != 'no':
            if faceid is not None:
                
                userinfo = self.check_record(faceid)
                
                # insert record or morning present
                getrecords = self.get_attendance_record(faceid,self.fromdate,self.todate)

                if getrecords is not None:
                    present_days = self.count_present_days(faceid,self.fromdate,self.todate)
                    self.cur = 1
                    self.handleException()
                    
                    Label(self.topview,text="Name: ").grid(row=1,column=0)
                    Label(self.topview,text= userinfo[1]).grid(row=1,column=1)
                    Label(self.topview,text="From: ").grid(row=2,column=0)
                    Label(self.topview,text= self.fromdate).grid(row=2,column=1)
                    Label(self.topview,text="To: ").grid(row=3,column=0)
                    Label(self.topview,text= self.todate).grid(row=3,column=1)
                    Label(self.topview,text="Total days: ").grid(row=1,column=3, columnspan=2)
                    Label(self.topview,text= str(len(getrecords))).grid(row=1,column=4,columnspan=2)
                    Label(self.topview,text="Total presents: ").grid(row=2,column=3, columnspan=2)
                    Label(self.topview,text= str(present_days)).grid(row=2,column=4,columnspan=2)
                    Label(self.topview,text="Total absents: ").grid(row=3,column=3, columnspan=2)
                    Label(self.topview,text= str(len(getrecords) - present_days)).grid(row=3,column=4,columnspan=2)
                    
                    # Using treeview widget 
                    treev = ttk.Treeview(self.topview, selectmode ='browse') 

                    # Calling pack method w.r.to treeview 
                    treev.grid(row=5,column=0,columnspan=10,padx=5,pady=5) 

                    # Defining number of columns 
                    treev["columns"] = ("NO","DATE", "TIME_IN", "TIME_OUT", "ATTENDANCE") 

                    # Defining heading 
                    treev['show'] = 'headings'

                    # Assigning the width and anchor to  the 
                    # respective columns 
                    treev.column("NO", width = 40, anchor ='c')
                    treev.column("DATE", width = 90, anchor ='c') 
                    treev.column("TIME_IN", width = 130, anchor ='c') 
                    treev.column("TIME_OUT", width = 130, anchor ='c') 
                    treev.column("ATTENDANCE", width = 90, anchor ='c')

                    # Assigning the heading names to the  
                    # respective columns 
                    treev.heading("NO", text ="NO")
                    treev.heading("DATE", text ="DATE") 
                    treev.heading("TIME_IN", text ="TIME_IN") 
                    treev.heading("TIME_OUT", text ="TIME_OUT") 
                    treev.heading("ATTENDANCE", text ="ATTENDANCE")


                    for i,row in enumerate(getrecords):
                        # Inserting the items and their features to the  
                        # columns built 
                        treev.insert("", 'end', text =""+str(i)+"",  
                                     values =(i+1,row[5],row[3],row[4],row[2]))
                    
                    mailBtn = Button(self.topview, text="SEND TO MAIL",width=20,height=1,bg='#222654',fg='#FFFFFF',
                           command= partial(self.maildo,getrecords,userinfo,present_days))
                    mailBtn.grid(row=6,column=0,columnspan=10,padx=10,pady=10)

                else:
                    msg = "No record found with your face..."
                    self.alertMsg(msg,self.topview)
                    self.handleException()
        
            else:
                msg = "Your face is not detected..."
                self.alertMsg(msg,self.topview)
                self.handleException()
        else:
            self.handleException()
            
    def maildo(self,records,userinfo,present_days): 
        
        try:
            tb = ''
            for i, record in enumerate(records):
                tb += """<tr><td style='text-align:center'>""" + str(record[5]) + """</td><td style='text-align:center'>"""+ str(record[3]) + """</td><td style='text-align:center'>""" + str(record[4]) + """</td><td style='text-align:center'>""" + str(record[2]) +"""</td></tr>"""
            # creates SMTP session
            s = smtplib.SMTP_SSL('smtp.gmail.com', 465)

            # start TLS for security
            #s.starttls()

            # Authentication
            s.login("yash.p.yashp@gmail.com", "patelyash07")
            message = MIMEMultipart('alternative')
            message["Subject"] = "Attendance Report Card"
            # message to be sent
            html = """
                    <html>
                    <body>
                        <h2>Attendance Report Card</h2><br>
                        <p><span>Name:"""+ str(userinfo[1])+"""</span><br>
                        <span>From Date:"""+ str(self.fromdate)+"""</span><br>
                        <span>To Date:"""+ str(self.todate)+"""</span><br>
                        <span>Total Days:"""+ str(len(records))+"""</span><br>
                        <span>Total presents:"""+ str(present_days)+"""</span><br>
                        <span>Total Absents:"""+ str(len(records) - present_days)+"""</span></p><br>
                        <table border='2'>
                            <th>DATE</th>
                            <th>TIME_IN</th>
                            <th>TIME_OUT</th>
                            <th>ATTENDANCE</th>"""+tb+"""
                        </table>
                    </body>
                    </html>
                    """

            content = MIMEText(html, "html")
            message.attach(content)

            # sending the mail
            s.sendmail("yash.p.yashp@gmail.com", "yash.patel.mscai20@aurouniversity.edu.in", message.as_string())

            # terminating the session
            s.quit()

            msg = "Mail sent successfully..."
            self.alertMsg(msg,self.topview)
        except:
            msg = "Some problem while sending a mail..."
            self.alertMsg(msg,self.topview)
            print("error in mail sent")
        
face = FaceDetection()
face.root.mainloop()


