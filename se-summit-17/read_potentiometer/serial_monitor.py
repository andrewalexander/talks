# need to `pip install pyserial` first
import serial
import time
import logging
import logging.handlers
import boto3
from botocore.exceptions import ClientError

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler with rotating logs
LOG_FILE = 'serial-data.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

def monitor():
  print("Start Serial Monitor")

  COMPORT = '/dev/cu.usbmodem1411'
  BAUDRATE = 9600

  ser = serial.Serial(COMPORT, BAUDRATE, timeout=0)
  start = time.time()
  old_line = b''

  # read continuously for messages on the serial port
  while (1):
    line = ser.readline()
    
    # only do something if we got something from the serial port
    if line and isinstance(line, bytes):
      # sometimes the payload gets split into two reads, so wait 100ms and 
      # read again to be sure that doesn't happen
      time.sleep(0.100)
      tmp = ser.readline()
      if tmp:
        line = line + tmp
      
      # strip \n and \r
      fields = line.replace(b'\r', b'').replace(b'\n', b'').replace(b'b', b'')

      if line != b'\r\n':
        raw_value = fields.decode("utf-8")
        out_int = int(float(raw_value))
        out_string = 'Voltage Crossed! Voltage: {}\n'.format((out_int/1024)*5)

        logging.info(out_string)
        print(out_string)

      # send message to SNS topic to trigger lambda
      send_message(out_string)

def send_message(message):
  topic_arn = 'arn:aws:sns:us-east-1:458143874686:arduino-sns'
  client = boto3.client('sns')
  response = client.publish(
    TopicArn=topic_arn,
    Message=message
  )

def main():
  monitor()

if __name__ == '__main__':
  main()
