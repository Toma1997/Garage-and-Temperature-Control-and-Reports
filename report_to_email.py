import smtplib
import imaplib
import email as emailDecoder
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import time

def getEmailSender(brojMejla):
    _, msg = imap.fetch(str(int(brojMejla)), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            msg = emailDecoder.message_from_bytes(response[1])
            from_who = msg.get("From").split()[-1].replace("<","").replace(">","")
            return from_who

def fetchtempWeather2Umbrella():
    respWeather2Umbrella = requests.get("https://www.weather2umbrella.com/vremenska-prognoza-beograd-srbija-sr/trenutno")
    weather_per_hours = BeautifulSoup(respWeather2Umbrella.text, "html.parser").find('div', attrs={'class':'weather_per_hours'})
    hourly_temp = weather_per_hours.find_all('div', attrs={'class':'col-xs-2 col-sm-1 hourly_temp'})
    tempList = []
    for temp in hourly_temp:
        tempList.append(int(temp.p.text.replace("°","")))
    hours = int(time.strftime("%H"))
    start = (hours - 6) if (hours - 6) > 0 else 1
    tempWeather2Umbrella = []
    for i in range(start - 1, hours):
        tempWeather2Umbrella.append(tempList[i])

    # Add here to look for last 7 hours with previous day.
    if len(tempWeather2Umbrella) == 0:
        tempWeather2Umbrella = [0] * 7
    return tempWeather2Umbrella 

def fetchTempThingSpeak():
    respThingSpeak= requests.get("https://api.thingspeak.com/channels/1092688/feeds.json?api_key=ZR7N919RTEZO6MT7&results=7")
    values = respThingSpeak.json()['feeds']
    tempThingSpeak = []
    for val in values:
        tempThingSpeak.append(int(float(val['field1'])))
    return tempThingSpeak

def plotTemperatures(tempWeather2Umbrella, tempThingSpeak):
    f = plt.figure()
    plt.plot(range(1,8), tempWeather2Umbrella, color="green", label="Weather2Umbrella")
    plt.plot(range(1,8), tempThingSpeak, color="orange", label="ThingSpeak")
    plt.ylabel("Temperature")
    plt.xlabel("Samples")
    plt.legend()
    f.savefig("temperature.png")

def getCoolerHeaterAvg(lastReportNum):
    respThingSpeak= requests.get("https://api.thingspeak.com/channels/1092688/feeds.json?api_key=ZR7N919RTEZO6MT7")
    values = respThingSpeak.json()['feeds']
    coolerAllValues = []
    heaterAllValues = []
    for val in values:
        coolerAllValues.append(int(float(val['field2'])))
        heaterAllValues.append(int(val['field3']))
    afterLastReportCoolerValues = []
    afterLastReportHeaterValues = []
    for indx in range(lastReportNum, len(coolerAllValues)):
        afterLastReportCoolerValues.append(coolerAllValues[indx])
        afterLastReportHeaterValues.append(heaterAllValues[indx])
    lastReportNum = len(heaterAllValues)
    countHeatOn = 0
    for i in range(0, len(afterLastReportHeaterValues)):
        if afterLastReportHeaterValues[i] == 1 and (i == 0 or afterLastReportHeaterValues[i-1] == 0):
            countHeatOn += 1
    avgCoolerPower = round(sum(afterLastReportCoolerValues)/len(afterLastReportCoolerValues), 2) if len(afterLastReportCoolerValues) > 0 else 0
    return avgCoolerPower, countHeatOn, lastReportNum

def getNewGarageOpeningsCount(imap):
    response, newGarageOpenings = imap.search(None,'SUBJECT "Garage" UNSEEN')
    print("IMAP response searching for mail subject 'Garage': " + response)
    countNewGarageOpenings = len(newGarageOpenings[0].split())
    for i in newGarageOpenings[0].split():
        imap.store(i, '+FLAGS', '\\SEEN')
    return countNewGarageOpenings

def createReport(email, password, to, avgCoolerPower, countHeatOn, countNewGarageOpenings):
    report = MIMEMultipart()
    report["Subject"] = "RESPORT RESPONSE"
    report["From"] = email
    report["To"] = to
    mimeTextsValues = {time.strftime("%d.%m.%Y %H:%M"): "<b>Report at {}</b><br>", 
                    avgCoolerPower: "Average Cooler power since the last report: {0:.2f} %<br>",
                    countHeatOn: "Number of heater activation since the last report: {0:d}<br>",
                    countNewGarageOpenings: "Number of garage openings since the last report: {0:d}<br>" }
    for key in mimeTextsValues.keys():
        report.attach(MIMEText(mimeTextsValues[key].format(key), 'html'))
    report.attach(MIMEText("<img src='cid:image1'><br>",'html'))
    with open("temperature.png", 'rb') as filePlot:
        imgPlot = MIMEImage(filePlot.read())
        imgPlot.add_header('Content-ID', '<image1>')
    report.attach(imgPlot)
    smtpServer = smtplib.SMTP('smtp.gmail.com', 587)
    smtpServer.starttls()
    smtpServer.login(email, password)
    smtpServer.sendmail(email, to, report.as_string())
    smtpServer.quit()

def processDataAndCreateReport(request_mail_num, lastReportNum, imap, email, password):
    to = getEmailSender(request_mail_num)
    print("Fetching and processing temperatures from Thingspeak and Weather2Umbrella...")
    tempWeather2Umbrella = fetchtempWeather2Umbrella()
    tempThingSpeak = fetchTempThingSpeak()
    plotTemperatures(tempWeather2Umbrella, tempThingSpeak)
    print("Fetching and processing cooler and heater average values after last report...")
    avgCoolerPower, countHeatOn, lastReportNum = getCoolerHeaterAvg(lastReportNum)
    print("Getting garage openings emails since last report...")
    countNewGarageOpenings = getNewGarageOpeningsCount(imap)
    print("New report is creating...")
    createReport(email, password, to, avgCoolerPower, countHeatOn, countNewGarageOpenings)
    return lastReportNum

if __name__ == "__main__":
    lastReportNum = 0
    email = "toma.demo97@gmail.com"
    password = "Tomademo97+"
    while True:
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(email, password)
        print("Logged in!")
        imap.select("INBOX")
        response, report = imap.search(None, 'SUBJECT "IZVESTAJ" UNSEEN')
        print("IMAP response searching for mail subject 'IZVESTAJ': " + response)
        for request_mail_num in report[0].split():
            lastReportNum = processDataAndCreateReport(request_mail_num, lastReportNum, imap, email, password)
            