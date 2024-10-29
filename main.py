#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import time

import ST7789V		# LCD driver
from PIL import Image,ImageDraw,ImageFont
import BME280	# Atmospheric Pressure/Temperature and humidity
import WS2812 		# RGB LED driver
from rpi_ws281x import Color

import GPIOCFG
import DS3231	# RTC
import os
from datetime import datetime, time
import calendar

# Configuration
dir = os.getcwd()

numpicdir = dir + "/numpic/C/"
menupicdir = dir + "/menupic/B/"

debouncetime = 0.09 #50ms debounce time, Prevent button accidental touch

# displaySeconds = False

# Hardware cheatsheet
# Display 0 is left, 5 is right

print("1. LCD init")
BlackLightLev =  8
lcd = ST7789V.LCD1in14(BlackLightLev)
lcd.Init()
lcd.clearAll()
W = lcd.width
H = lcd.height

print("2. Set RGB Color")
rgb = WS2812.WS2812()

CL = {'White':[255,255,255], 'Red':[255,0,0], 'Green':[0,255,0], 'Blue':[0,0,255], 'Yellow':[255,255,0], 'Cyan':[0,255,255], 'Purple':[255,0,255]}
rgbColor = [CL['Red'],CL['Yellow'],CL['Green'],CL['Cyan'],CL['Blue'],CL['Purple']]
rgbCoolWhite = [244, 253, 255]
rgbWarmWhite = [253, 244, 220]

# rgb.Close()
rgb.SetRGB(rgbColor)

print("3. Get pressure temp hum")
bme280 = BME280.BME280()

print("4. RTC init")
rtc = DS3231.DS3231()
rtc.SET_Hour_Mode(24)

gpios = GPIOCFG.GPIOCFG()

def getRTCDateTime():
    year, month, day = rtc.Read_Calendar()
    hour, minute, second = rtc.Read_Time()
    tzinfo = None
    
    return datetime(year, month, day, hour, minute, second, tzinfo = tzinfo)

def getNumberImage(number):
    return Image.open(numpicdir + str(number)+'.jpg')

def getDateImage():
    date = getRTCDateTime()
    
    fontLarge = ImageFont.truetype(('Font.ttc'), 100)
    fontSmall = ImageFont.truetype(('Font.ttc'), 50)
    
    image = Image.new("RGB", (135,240), "black")
    draw = ImageDraw.Draw(image)

    textDayName = calendar.day_abbr[date.weekday()].upper()
    _, _, w, h = draw.textbbox((0, 0), textDayName, font=fontSmall)
    draw.text(((W-w)/2, ((H*.25)-h)/2), textDayName, font=fontSmall, fill="red")

    textDay = str(date.day)
    _, _, w, h = draw.textbbox((0, 0), textDay, font=fontLarge)
    draw.text(((W-w)/2, (H-h)/2), textDay, font=fontLarge, fill="white")

    textMonth = calendar.month_abbr[date.month].upper()
    _, _, w, h = draw.textbbox((0, 0), textMonth, font=fontSmall)
    draw.text(((W-w)/2, ((H*.25)-h)/2+(H*.75)), textMonth, font=fontSmall, fill="red")

    return image

def getTempImage():
    bme280.get_calib_param()
    bme = []
    bme = bme280.readData()
    pressure = round(bme[0], 2) 
    temp = round(bme[1], 2) 
    hum = round(bme[2], 2)

    print("pressure : %7.2f hPa" %pressure)
    print("temp : %-6.2f °C" %temp)
    print("hum : %6.2f ％" %hum)
    
    fontLarge = ImageFont.truetype(('Font.ttc'), 100)
    fontSmall = ImageFont.truetype(('Font.ttc'), 50)
    
    image = Image.new("RGB", (135,240), "black")
    draw = ImageDraw.Draw(image)

    # textDay = str(date.day)
    # _, _, w, h = draw.textbbox((0, 0), textDay, font=fontLarge)
    # draw.text(((W-w)/2, (H-h)/2), textDay, font=fontLarge, fill="white")

    return image

def showFullClock():
    Time = rtc.Read_Time()

    # Show date on leftmost display  
    lcd.ShowImage(0, getDateImage())

    lcd.ShowImage(1, getNumberImage(Time[0]//10))
    lcd.ShowImage(2, getNumberImage(Time[0]%10))
    lcd.ShowImage(3, getNumberImage(Time[1]//10))
    lcd.ShowImage(4, getNumberImage(Time[1]%10))

    # Show temperature on rightmost display
    lcd.ShowImage(5, getTempImage()) 


MenuChoseRect = [(0,0),(133,0),(133,239),(0,239),(0,0)]  

mode_flg = 0
left_flg = 0
right_flg = 0
NowId = 1
ShowMenuFlg = 1
    
def ShowMenuFun():
    global ShowMenuFlg
    global mode_flg
    global left_flg
    global right_flg
    # global NowId
    global NowId
    LastPicId = 1
    pic1 = Image.open(menupicdir + '1.jpg')
    pic2 = Image.open(menupicdir + '2.jpg')
    pic3 = Image.open(menupicdir + '3.jpg')
    pic4 = Image.open(menupicdir + '4.jpg')
    pic5 = Image.open(menupicdir + '5.jpg')
    pic6 = Image.open(menupicdir + '6.jpg')  
    # print("Now id = %d" %NowId)
    # print("ShowMenuFlg = %d" %ShowMenuFlg)
    if(ShowMenuFlg == 1):
        ShowMenuFlg = 0
        if(NowId == 1):
            draw = ImageDraw.Draw(pic1)
        elif(NowId == 2):
            draw = ImageDraw.Draw(pic2)
        elif(NowId == 3):
            draw = ImageDraw.Draw(pic3)
        elif(NowId == 4):
            draw = ImageDraw.Draw(pic4)
        elif(NowId == 5):
            draw = ImageDraw.Draw(pic5)
        elif(NowId == 6):
            draw = ImageDraw.Draw(pic6)
        print("Show Menu")
        draw.line(MenuChoseRect, fill=255, width=10)
        lcd.ShowImage(0, pic1)
        lcd.ShowImage(1, pic2)
        lcd.ShowImage(2, pic3)
        lcd.ShowImage(3, pic4)
        lcd.ShowImage(4, pic5)
        lcd.ShowImage(5, pic6)
        
    if gpios.ReadLeftPin():
        time.sleep(debouncetime)
        if gpios.ReadLeftPin():
            while(gpios.ReadLeftPin() != 0):
                left_flg = 1
                
            LastPicId = NowId
            NowId = NowId - 1
            if(NowId == 0):
                NowId = 6
            
            print("L: NowId = %d, LastPicId = %d" %(NowId, LastPicId))
                                    
    if gpios.ReadRightPin():
        time.sleep(debouncetime)
        if gpios.ReadRightPin():
            while(gpios.ReadRightPin() != 0):
                right_flg = 1
            LastPicId = NowId
            NowId = NowId + 1
            if(NowId == 7):
                NowId = 1
            # print("R")
            # print("NowId = %d" %NowId)
            # print("LastPicId = %d" %LastPicId)
            print("R: NowId = %d, LastPicId = %d" %(NowId, LastPicId))

    if gpios.ReadModePin():
        time.sleep(debouncetime)
        if gpios.ReadModePin():
            while(gpios.ReadModePin() != 0):
                mode_flg = 1
            modelist = ["SetTime", "SetAnAlarm", "SetRGB", "SetBrightnesslevel", "ShowT&H", "Return"]
            print("Mode:", modelist[NowId-1])
            
    #show menu pic
    if(left_flg == 1 or right_flg == 1):
        NowPicName = Image.open(menupicdir + str(NowId)+ '.jpg')                
        drawNowPic = ImageDraw.Draw(NowPicName)
        drawNowPic.line(MenuChoseRect, fill=255, width=10)
        lcd.ShowImage(NowId - 1, NowPicName)                
        if(NowId != LastPicId):#first time donot show last pic,because first time not last pic
            LastPicName = Image.open(menupicdir + str(LastPicId)+ '.jpg')
            drawLastPic = ImageDraw.Draw(LastPicName)                
            lcd.ShowImage(LastPicId - 1, LastPicName)
        right_flg = 0
        left_flg = 0


def updateRGBFun(now):
    onHour = 8
    offHour = 21
    onDuration = offHour - onHour
    
    if(onHour < now.hour < offHour):
        rgb.strip.setBrightness(200)
    else:
        rgb.strip.setBrightness(0)

    shift = (now.hour - onHour) / onDuration

    # Red increses from cool to warm
    # Green and blue decrease from cool to warm
    redDiff = rgbWarmWhite[0] - rgbCoolWhite[0]
    red = round(rgbCoolWhite[0] + shift * redDiff)
    greenDiff = rgbWarmWhite[1] - rgbCoolWhite[1]
    green = round(rgbCoolWhite[1] + shift * greenDiff)
    blueDiff = rgbWarmWhite[2] - rgbCoolWhite[2]
    blue = round(rgbCoolWhite[2] + shift * blueDiff)

##    print(shift, redDiff, greenDiff, blueDiff, red, green, blue, sep=', ')

    for i in range(0, rgb.strip.numPixels(), 1):
        rgb.strip.setPixelColor(
            i, Color(red, green, blue))

    rgb.strip.show()

def doShutdownFun():
    # Display shutdown message
    font1 = ImageFont.truetype(('Font.ttc'), 150)
    imageShowShutdown = Image.new('RGB', (135,240), 'WHITE')
    drawShutdown = ImageDraw.Draw(imageShowShutdown)
    drawShutdown.text((0,0), 'SHUTDOWN', font=font1, fill='red')
    lcd.ShowImage(0, imageShowShutdown)

    # Turn of LEDs
    off = [0,0,0]
    rgb.SetRGB([off, off, off, off, off, off])

    # Shutdown
    os.system("shutdown now")

def KeyListen():
    global mode_flg
    global left_flg
    global right_flg    
    global NowId
    global ShowMenuFlg
    
    if(gpios.ReadModePin() != 0):
        time.sleep(debouncetime)
        if gpios.ReadModePin():
            while(gpios.ReadModePin() != 0):
                mode_flg = 0
        # pic1 = Image.new('RGB', (135, 240), "WHITE") 
   
        print ("KeyListen Start")      
        while(1):
            ShowMenuFun()
                
            if(mode_flg == 1):#mode key is down
                mode_flg = 0
                if(NowId == 1): # Shutdown
                    doShutdownFun()
            
                #if(NowId == 2):#Set AnAlarm
                    #No Op
                    
                #if(NowId == 3):
                    #SetRGBFun()
                    
                #if(NowId == 4):
                    #SetBLFun()
                
                #if(NowId == 5):
                    #ShowTemHumFun()
                    
                if(NowId == 6):#return
                    # ReturnFun()
                    ShowMenuFlg = 1
                    NowId = 1
                    showFullClock()
                    # KeyListenFlg = 0
                    return 1
        return 0
                    

# Print current RTC date and time, system date and time
print("Current RTC date and time: ", getRTCDateTime().strftime("%c"))

now = datetime.now()
print("Local sytem date and time: " + now.strftime("%c"))

# Set RTC to system date and time
rtc.SET_Calendar(now.year, now.month, now.day)
rtc.SET_Time(now.hour, now.minute, now.second)

print ("mainThread Start")

showFullClock()

while(1):   # Loop forever to keep updating the time
    if(KeyListen() == 1):
        showFullClock()
    
    dt = getRTCDateTime()

    # Update only the displays that need to change, to minimize write actions to the LCD screens
    if(dt.second == 0): # Seconds == 0, so update minute units digit
        lcd.ShowImage(4, getNumberImage(dt.minute % 10))

        if((dt.minute % 10) == 0): # Minute units digit is 0, so update minute tens digit
            lcd.ShowImage(3, getNumberImage(dt.minute // 10))

            if((dt.minute // 10) == 0): # Minutes == 0, so update hours units digit
                lcd.ShowImage(2, getNumberImage(dt.hour % 10))

                if((dt.hour % 10) == 0): # Hours units digit is 0, so update hours tens digit (and the date while we're at it)
                    lcd.ShowImage(1, getNumberImage(dt.hour // 10))
                    lcd.ShowImage(0, getDateImage())
    
    # At midnight, update the real time clock
    if dt.time() == time(0, 0, 0):
        now = datetime.now()
        rtc.SET_Time(now.hour, now.minute, now.second)
        rtc.SET_Calendar(now.year, now.month, now.day)
        print("RTC updated to: " + now.strftime("%c"))

    # RGB LED dimming at night
    updateRGBFun(dt)
##    if dt.time() == time(21, 0, 0):
##        rgb.Close()
##    if dt.time() == time(7, 0, 0):
##        rgb.SetRGB(rgbColor)


print ("beepThread Stop")

rgb.Close()
gpios.Beep()
gpios.destory()
