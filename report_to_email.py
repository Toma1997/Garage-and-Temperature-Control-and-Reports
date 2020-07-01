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

def crtanjePodataka(temW2U,tempThingSpeak):
    f = plt.figure()
    plt.plot(range(1,8),tempW2U,color="green",label="Weather2Umbrella")
    plt.plot(range(1,8),tempThingSpeak,color="orange",label="ThingSpeak")
    plt.ylabel("Temperature")
    plt.xlabel("Samples")
    plt.legend()
    f.savefig("temperature.jpg")

def dohvatanjeTempW2U():
    urlW2U = "https://www.weather2umbrella.com/vremenska-prognoza-beograd-srbija-sr/trenutno"
    respW2U = requests.get(urlW2U)
    weather_per_hours = BeautifulSoup(respW2U.text, "html.parser").find('div', attrs={'class':'weather_per_hours'})
    hourly_temp = weather_per_hours.find_all('div', attrs={'class':'col-xs-2 col-sm-1 hourly_temp'})
    tempList = list()
    for temp in hourly_temp:
        tempList.append(int(temp.p.text.replace("°","")))
    sati = int(time.strftime("%H"))
    tempW2U = list()
    pocetak = (sati-6) if(sati-6)>0 else 1
    for i in range(pocetak-1,sati):
        tempW2U.append(tempList[i])
    return tempW2U 

def dohvatanjeTempThingSpeak():
    respThingSpeak= requests.get("https://api.thingspeak.com/channels/1091866/feeds.json?api_key=547RK4B5HP5VKXHV&results=7")
    merenja = respThingSpeak.json()['feeds']
    tempThingSpeak = list()
    for m in merenja:
        tempThingSpeak.append(int(float(m['field1'])))
    return tempThingSpeak

def dohvatanjeOstalihPodatakaThingSpeak(slanjeIzvestaja):
    respThingSpeak= requests.get("https://api.thingspeak.com/channels/1091866/feeds.json?api_key=547RK4B5HP5VKXHV")
    merenja = respThingSpeak.json()['feeds']
    motor, grejac = list(), list()
    for m in merenja:
        motor.append(int(float(m['field2'])))
        grejac.append(int(m['field3']))
    print(motor, grejac)
    novoPodaciMotor, novoPodaciGrejac = list(), list()
    for broj in range(slanjeIzvestaja,len(motor)):
        novoPodaciMotor.append(motor[broj])
        novoPodaciGrejac.append(grejac[broj])
    print(novoPodaciMotor, novoPodaciGrejac)
    slanjeIzvestaja = len(grejac)
    brojPaljenjaGrejaca = sum([1 for stanje in novoPodaciGrejac if stanje == 1])
    if len(novoPodaciMotor)>0:
        prosecanRadVentilatora = round(sum(novoPodaciMotor)/len(novoPodaciMotor),2)
    else:
        prosecanRadVentilatora = 0
    return prosecanRadVentilatora, brojPaljenjaGrejaca, slanjeIzvestaja

def merenjaOtvaranjaGaraze(imap):
    _, novaOtvaranja = imap.search(None,'SUBJECT "Garage" UNSEEN')
    otvaranjeGaraze = len(novaOtvaranja[0].split())
    for i in novaOtvaranja[0].split():
        imap.store(i,'+FLAGS','\\SEEN')
    return otvaranjeGaraze

def kreiranjeIzvestaja(email, password, kome, prosecanRadVentilatora, brojPaljenjaGrejaca, otvaranjeGaraze):
    poruka = MIMEMultipart()
    poruka["Subject"] = "REZULTAT"
    poruka["From"] = email
    poruka["To"] = kome
    porukaTxt = MIMEText("<b>Izvestaj za {}</b><br>".format(time.strftime("%d.%m.%Y %H:%M")),'html')
    poruka.attach(porukaTxt)
    porukaTxt = MIMEText("Average Cooler power since the last report: {0:.2f} %<br>".format(prosecanRadVentilatora), 'html')
    poruka.attach(porukaTxt)
    porukaTxt = MIMEText("Number of heater activation since the last report: {0:d}<br>".format(brojPaljenjaGrejaca), 'html')
    poruka.attach(porukaTxt)
    porukaTxt = MIMEText("Number of garage openings since the last report: {0:d}<br>".format(otvaranjeGaraze), 'html')
    poruka.attach(porukaTxt)
    porukaTxt = MIMEText("<img src='cid:image1'><br>",'html')
    poruka.attach(porukaTxt)
    with open("temperature.jpg", 'rb') as filePlot:
        imgPlot = MIMEImage(filePlot.read())
        imgPlot.add_header('Content-ID', '<image1>')
    poruka.attach(imgPlot)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, kome, poruka.as_string())
    server.quit()

def odKogaJeMejl(brojMejla):
    res, msg = imap.fetch(str(int(brojMejla)), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            msg = emailDecoder.message_from_bytes(response[1])
            from_who = msg.get("From").split()[-1].replace("<","").replace(">","")
            return from_who

if __name__ == "__main__":
    sendReport = 0
    while True:
        email = "toma.demo@gmail.com"
        password = "Tomademo97+"
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(email,password)
        imap.select("INBOX")
        _, izvestaj = imap.search(None,'SUBJECT "IZVESTAJ" UNSEEN')
        for i in izvestaj[0].split():
            kome = odKogaJeMejl(i)
            tempW2U = dohvatanjeTempW2U()
            tempThingSpeak = dohvatanjeTempThingSpeak()
            crtanjePodataka(tempW2U, tempThingSpeak)
            prosecanRadVentilatora, brojPaljenjaGrejaca, sendReport = dohvatanjeOstalihPodatakaThingSpeak(sendReport)
            otvaranjeGaraze = merenjaOtvaranjaGaraze(imap)
            kreiranjeIzvestaja(email, password, kome,prosecanRadVentilatora, brojPaljenjaGrejaca,otvaranjeGaraze)