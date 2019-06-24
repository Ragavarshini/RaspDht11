#################################################
# Python code for RaspberryPi (3B+) that :
#
# 1) Checks the temperature and 
#    humidity using a DHT11 sensor.
# 2) Logs the data into CSV.
# 3) Sends data to ThingSpeak (live tracking).
# 4) Sends a warning incase the temperature 
#    rises above 30C and Humidity above 90%.
#
# By SUSHANT KADAM
#
#################################################

# Importing required files and library
import RPi.GPIO as GPIO
import dht11
import sys
import urllib2
from time import sleep
import datetime
import csv
import smtplib

#Global variables
MAX_TEMP = 32
MIN_TEMP = 15
MAX_HUMIDITY = 70
MIN_HUMIDITY = 35
SENDER = "yourid@gmail.com"
RECEIVER = "theirid@live.com"

#function that sends a warning email to
#a set user
def send_warning(val):
    try:
	#set values for email
	sender = SENDER
	receiver = RECEIVER
	
	#set SMTP information
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.ehlo()
	server.starttls()
	server.login(sender, "#password")
	
	#dummy messages
	subject = "Warning"
	text = "Please check the room humidity and temperature!"
	
	#Set subject
	if val == 0:
	    subject = "Temperature risen above %d C!" % MAX_TEMP
	    text = "Warning the temperature has increased above %d" % MAX_TEMP
	elif val == 1:
	    subject = "Humdity risen above %d percent!" % MAX_HUMIDITY
	    text = "Warning the humidity has increased above %d" % MAX_HUMIDITY
	
	#Create an email format
	from email.Message import Message
	m = Message()
	m['X-Priority'] = '2' #set high importance
	m['Subject'] = subject
	m.set_payload(text)

	#Send email
	server.sendmail(sender,receiver,m.as_string())
	
	#display success on terminal
	print("Warning sent")

    except Exception, ex:
	#Print execptions if any
	print(ex)

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# read data using Pin GPIO21 for capturing data
instance = dht11.DHT11(pin=21)

# Here starts the main logic of the code
# This look will repeat until it is "break"-ed
while True:
    try:
	#Capture the result
        result = instance.read()
        
	#If data is succefully captured
	if result.is_valid():
            
	    #gather the raw data into var
	    temp = result.temperature
            humi = result.humidity

	    if int(temp) > MAX_TEMP:
		send_warning(0)
	    if int(humi) > MAX_HUMIDITY:
		send_warning(1)
	    
	    #capture the current date and time
	    currentDT = datetime.datetime.now()
	    date = currentDT.strftime("%Y/%m/%d")
	    time = currentDT.strftime("%H:%M:%S")
	    
	    #create a row element to be inserted
	    #into CSV
	    myCsvRow = [date, time, temp, humi]
	    
	    #print the same onto the terminal
	    print(myCsvRow)
	    
	    #Append the row into the CSV
	    with open(r'TempHumidity.csv', 'a') as fd:
		writer = csv.writer(fd);
		writer.writerow(myCsvRow)
	    
	    #Following code sends the data
	    #to the ThingSpeak site
	    
	    #ThingSpeak needs a "Write API Key"
	    #So that we are able to send data
	    #Our own channel
	    
            #API Write key send data
            myAPI = 'CBFP8AE0778SB523' 
            
	    #URL where we will send the data, 
	    #Don't change it
            baseURL = 'https://api.thingspeak.com/update?api_key=%s' % myAPI 
            
	    #To the URL append the fields
	    #field1 is temperature
	    #field2 is humidity
            url = urllib2.urlopen(baseURL + 
	    '&field1=%s&field2=%s' % (temp, humi))

	    #Wait for 2 minutes to capture the 
	    #next data
	    sleep(120)
	    
        else:
	    #If there is some error while
	    #reading the result from GPIO
            print("Error while accessing GPIO, \
	    data will be ready after 2 seconds")
	    
	    # DHT11 requires 2 seconds to 
	    # give a reading, so make sure 
	    # to add delay of 2 seconds in
	    # case of error
	    sleep(2)
	    
    except Exception as e:
	#Catch exception and print while
	#1) Reading GPIO
	#2) Sending data to ThingSpeak
	#3) Writing CSV 
        print (e)
        break
	
#ENDWHILE
