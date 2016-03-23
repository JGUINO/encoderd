import os.path

# working directory for daemon logs and persistance files
DIR = '/home/pi/.encoderd/'

# stores current system pid
PID_FILE=os.path.join(DIR,'encoderd.pid')

# log file
LOG_FILE=os.path.join(DIR,'encoderd.log')

# refresh rate (time in seconds between angle checks)
REFRESH_RATE = 1

# list of attached encoders
ENCODERS=[
  dict(
    name="780X",                # device nickname
    pinA=7,                     # wiringPI pin number
    pinB=0,                     # wiringPI pin number
    calibration=360/(2048*4.0), # degrees/step, HEDR-55L2-BH07
    logfile=os.path.join(DIR,"Angle_780X.log"),   # stores last known encoder value
  ),
  dict(
    name="780Y",                # device nickname
    pinA=2,                     # wiringPI pin number
    pinB=3,                     # wiringPI pin number
    calibration=360/(2048*4.0), # degrees/step, HEDR-55L2-BH07
    logfile=os.path.join(DIR,"Angle_780Y.log"),   # stores last known encoder value
  ),
]

# create directory if it doesn't exist
if not os.path.exists(DIR):
  print("logging directory not found, attempting to create")
  os.makedirs(DIR)
  print("logging directory created: %s", DIR)
