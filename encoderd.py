#!/usr/bin/env python

################################################################################
# 
# encoderd.py is a python based daemon for persistant monitoring of the state of
#   any number of quadrature rotarty encoders attached to a raspberry pi
# 
# Written by: 
#    Matthew Ebert 
#    Department of Physics
#    University of Wisconsin - Madison
#    mfe5003@gmail.com
# 
# Python Daemon bootstrap code by:
#    Sander Marechal
#    http://www.jejik.com/ 
#    http://web.archive.org/web/20160305151936/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
#
# This daemon will poll the GPIO pins for each attached rotatry encoder and
#   convert the count to an angle.
#   Settings are listed in encoder-settings.py file.
#
################################################################################

import sys, time
from daemon import Daemon
import logging
import gaugette.rotary_encoder as rotary_encoder

import encoderd-settings as settings

class MyDaemon(Daemon):
  def run(self):
    setup()
    while True:
      for enc in self.encoders:
        steps = enc['obj'].get_delta()
        if steps != 0:
          enc['angle'] += enc['calibration']*steps
          self.logger.info("Encoder {}: {} movement detected. Angle is now {} degrees.".format(enc['number'],enc['name'],enc['angle']))
        saveAngle(enc) 

      time.sleep(settings.REFRESH_RATE)

  def setup(self):
    setupLogger()
    self.logger.info("Encoderd started.")
    setupEncoders()

  def setupLogger(self):
    # set up logger
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.DEBUG)
    # create a file handler for the logger
    fh = logging.FileHandler(settings.LOG_FILE)
    fh.setLevel(logging.DEBUG)
    # format logging
    fformatter = logging.Formatter('(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(fformatter)
    self.logger.addHandler(fh)

  def setupEncoders(self):
    self.encoders=[]
    enc_cnt = 0
    for enc in settings.ENCODERS:
      self.encoders.append(enc)
      pinA=enc['pinA']
      pinB=enc['pinB']
      # start a monitoring thread
      self.encoders[enc_cnt]['obj'] = rotary_encoder.Worker(pinA,pinB)
      self.encoders[enc_cnt]['number'] = enc_cnt
      self.encoders[enc_cnt]['obj'].start()
      self.logger.info("Encoder {}: {} registered. Worker thread started.".format(enc_cnt,enc['name']))
      # read recorded angle if log file exists
      readAngle(enc)
      enc_cnt += 1

    self.encoder_count = enc_cnt
    self.logger.info("Registered encoders: {}".format(str(enc_cnt)))
      
  def readAngle(self, encoder):
    try: 
      with open(encoder.logfile, 'r') as fi:
        angle = float(fi.readline())
    except IOError:
      angle = 0.0
    self.logger.info("Encoder: {}: {} angle set to {} degrees.".format(encoder['number'],encoder['name'],angle))
    self.encoders[enc_cnt]['angle'] = angle
    return angle

  def saveAngle(self, encoder):
    angle = encoder['angle']
    with open(encoder.logfile, 'w') as fo:
      fo.write(str())
    self.logger.debug("Encoder: {}: {} angle recorded as {} degrees.".format(encoder['number'],encoder['name'],angle))

  def zero(self):
    for enc in self.encoders:
      enc['angle'] = 0.0
      saveAngle(enc)


if __name__ == "__main__":
  daemon = MyDaemon(settings.PID_FILE)
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      daemon.start()
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      daemon.restart()
    elif 'zero' == sys.argv[1]:
      daemon.zero()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage: %s start|stop|restart|zero" % sys.argv[0]
    sys.exit(2)
