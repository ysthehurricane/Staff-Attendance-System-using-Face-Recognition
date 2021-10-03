import MySQLdb as db
import string
import random
import os 
import cv2

class DatabaseOp:

    def __init__(self):
        try:
            self.con = db.connect(host="localhost",database="attendance_system",password="P@tely@sh07",user="root")
            self.cursor = self.con.cursor()
        except:
            print("Database connection is failed...")
        

    def dbfetchall(self, tbl):
        query = "select * from " + tbl
        try:
            self.cursor.execute(query)
            record = self.cursor.fetchall()
            return record
        except:
            print('Checking in record problem...')
            return None
        finally:
            self.cursor.close()
            self.con.close()

    def dbfetchbyid(self, tbl, fid):
        query = "select * from " + tbl + "where facultyid =" + fid
        try:
            self.cursor.execute(query)
            record = self.cursor.fetchall()
            return record
        except:
            print('Checking in record problem by id...')
            return None
        finally:
            self.cursor.close()
            self.con.close()

    def capturefaces(self, fid):
        current_dir = os.getcwd()
        dir_path = os.path.join(current_dir, 'faces')
        create_dir_path = os.path.join(dir_path, fid)
        os.mkdir(create_dir_path)

        face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_alt2.xml')
        counter = 0
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        while counter <= 20:
            
            check , frame = cap.read()
            faces = face_cascade.detectMultiScale(frame,scaleFactor=1.5,minNeighbors=5)
            
            if len(faces) != 0:
            
                for (x,y,w,h) in faces:
            
                    roi_color = frame[y:y+h,x:x+w]
                    
                    image_item = create_dir_path + '/' + fid + str(counter) + '.jpg'
                    img = cv2.flip(roi_color,1)
                    img = cv2.resize(img,(224,224))
                    cv2.imwrite(image_item,img)
            
                    color = (255,0,0) 
                    stroke = 2
                    end_x = x+w
                    end_y = y+h
                    mainimg = cv2.flip(frame,1)
                    cv2.rectangle(mainimg,(x,y),(end_x , end_y) , color,stroke) 
                    cv2.imshow('Capture Faces',mainimg) 
                
                counter += 1

            cv2.waitKey(20)

        cap.release()
        cv2.destroyAllWindows()



    def insertrecord(self,tbl,data):
        
        N = 10
        registerdate = datetime.today().strftime('%Y-%m-%d')

        while True:
            fid = str(''.join(random.choices(string.ascii_uppercase + string.digits, k = N)))
            if self.dbfetchbyid(tbl, fid) is None:
                break
        
        fname = data[0]
        femail = data[1]          
        
        query = "insert into " + tbl+"('%s','%s','%s','%s')"
        arg = (fid,fname,femail,registerdate)
        self.capturefaces(fid)

        try: 
            self.cursor.execute(query % arg)
            self.con.commit()
            return True
        except:
            self.con.rollback()
            print('Insertion problem...')
            return False
        finally:
            self.cursor.close()
            self.con.close()


