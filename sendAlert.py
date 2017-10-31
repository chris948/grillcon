#!/usr/bin/python

import smtplib
import os


# Use sms gateway provided by mobile carrier:
# at&t:     number@mms.att.net
# t-mobile: number@tmomail.net
# verizon:  number@vtext.com
# sprint:   number@page.nextel.com


def sendAlert(loginName, loginPass, sendTo, subject, text):
    try:

        message = 'Subject: %s\n\n%s' % (subject, text)
        # Establish a secure session with gmail's outgoing SMTP server using your gmail account
        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.starttls()

        server.login(loginName, loginPass)

        # Send text message through SMS gateway of destination number
        # server.sendmail( 'chris.pangburn@gmail.com (Chris)', '4044292504@tmomail.net', 'Test' )
        server.sendmail(loginName, sendTo, message)
        return "success"

    except:
        return "error"
