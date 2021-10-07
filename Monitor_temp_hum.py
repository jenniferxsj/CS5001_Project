#Final Project for CS 5001
#Brian Meyer
#Shujun Xiao
#Xiaoliang Xu

import Adafruit_DHT as DHT
import json
import time
import psutil
import twilio
from twilio.rest import Client
import matplotlib.pyplot as plt
import csv
from matplotlib import rcParams
import http.client
import urllib

# Turn on the interactive mode
plt.ion()
# Creact 3 lists to hold all the inputted data.
x = []
y_tem = []
y_hum = []

# API Thingspeak - Brian
key = '66EU45C8K4SJUNCH'
channelID = '1353959'


# Define sensor type and pin number. - Shujun
sensor = DHT.DHT22
pin = 27

# Writing the data to the csv file. - Shujun
def write_temp(temperature, humidity):
  with open("temp_humidity.csv", "a") as log:
    log.write("{0},{1},{2}\n".format(time.strftime("%H:%M:%S"),str(temperature),str(humidity)))

# Read the csv file and draw a graph using matplotlib. - Shujun
def graph():
  with open("temp_humidity.csv","r") as csvfile:
    plots = csv.reader(csvfile, delimiter=",")
    for row in plots:
      if row[0] not in x:
        x.append(row[0])
        y_tem.append(int(float(row[1])))
        y_hum.append(int(float(row[2])))
    plt.clf()   # wipe out the graph 
    rcParams['figure.figsize'] = 20,6  # set the size of the canvas 
    plt.plot(x, y_tem, label = "Temperature")
    plt.plot(x, y_hum, label = "Humidity")
    plt.xlabel("Time")
    plt.ylabel("Reading")
    plt.title("Temperature and Humidity Readings")
    plt.legend(loc=1) # put the legends on the upper right of the graph
    plt.grid(True,linestyle=":") # Adding grid to the graph
    plt.draw()  # draw out the graph

#conditionals sending variables to API statements - Xiaolang
def checkAvgTempForAcSwitch(tempValues, threshold):
  '''
  checkAvgTempForAC takes a list temp values, compute the average temperature, 
  compare it with the threshold. 
  params:
      tempValues: a list of temp values
      threshold: the threshold of the average temperature 
  return:
      a tuple of (average temperature, statement), where the statement is a string.
      if the average temperature > threshold, statement = "Switching on AC";
      otherwise "Switching off AC"
  '''
  avg = sum(tempValues) / len(tempValues)
  if avg > threshold:
    text="Switching on AC"
    sendtoSMS(text)    

# Connect with twilio and sending out messages - Brian
def sendtoSMS(statement):
  account_sid = 'AC96c973f5b3e4b88eca097ef809acc0f6'
  auth_token = 'af6e9952608904435b84c4707d086efd'
  client = Client(account_sid, auth_token)

  message = client.messages.create(body= statement, from_='+18507714790', to='+15857332025')

  print(message.sid)

# Connect with Thinkspeak, print out the readings and connection status.- Brian
def thingspeak(temperature, humidity):
    while True:
        params = urllib.parse.urlencode({'field1': temperature, 'field2': humidity, 'key':key }) 
        headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = http.client.HTTPConnection("api.thingspeak.com:80")
        try:
            conn.request("POST", "/update", params, headers)
            response = conn.getresponse()
            print(response.status, response.reason)
            data = response.read()
            conn.close()
        except:
            print("connection failed")
        break

sendtoSMS("The program is starting to run!")
while True:  
  temperature, humidity = DHT.read_retry(sensor, pin) # get readings from sensor
  print("Temperature is：",temperature, "\nHumidity is：",humidity)
  write_temp(temperature, humidity)
  graph()
  thingspeak(temperature, humidity)
  tempValues = y_tem
  threshold=32
  checkAvgTempForAcSwitch(tempValues, threshold)
  plt.pause(5) 
sendtoSMS("The program is stopped!")