import cx_Freeze
import sys
import os
base = None

#os.environ["TCL_LIBRARY"] = "C:/Users/Yash Patel/anaconda3/tcl/tcl8.6"
#os.environ["TK_LIBRARY"] = "C:/Users/Yash Patel/anaconda3/tcl/tk8.6"

if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [cx_Freeze.Executable("Attendance_System.py", base=base, icon='icon.ico')]

cx_Freeze.setup(
    name="Attendance_System",
    options={"build_exe": {"packages": ["tkinter","PIL","imutils","time","threading","cv2","os","pickle","face_recognition","MySQLdb","datetime","functools","smtplib"],
                           "include_files": ["tk86t.dll","tcl86t.dll","icon.ico","back_ground.png","encodings.pickle","haarcascade_frontalface_default.xml"]}},
    version = "0.1",
    description = "Attendance System",
    executables = executables
    )
