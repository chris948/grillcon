#!/usr/bin/env python

#todo - make key file, 

import time
import os
import datetime
import math
import RPi.GPIO as GPIO
# import GPIO as GPIO # FOR DEBUGGING 
import sqlite3
# import signal
import cipher_functions
import sys
import ConfigParser
from sendAlert import sendAlert
import i2c_8574
import max31856
import socket

# CP 12-8-16 Adding IP Address
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    print (ip)
    s.close()
    return ip


# Class to create the config file if it does not exist
class ConfigCreate:
    # config_file = "/grillcon/grillcon_settings.cfg"

    def __init__(self, config_file):
        self.config_file = config_file

        if os.path.isfile(self.config_file):
            print "loaded config file"
        else:
            ConfigCreate.make_config_file(self)

    def make_config_file(self):

        parser = ConfigParser.SafeConfigParser()
        parser.add_section('grillcon_settings')
        parser.set('grillcon_settings', 'database_location', "/grillcon/templog.db")
        parser.set('grillcon_settings', 'fan_tolerance', '2')
        parser.set('grillcon_settings', 'fan_min', '6')
        parser.set('grillcon_settings', 'fan_multiplier', '10')
        parser.set('grillcon_settings', 'delta_temp', '15')
        parser.set('grillcon_settings', 'write_interval', '60')
        parser.set('grillcon_settings', 'email_address', 'johndoe@gmail.com')
        parser.set('grillcon_settings', 'email_password', 'w9Gm1uvQ1dA=')
        parser.set('grillcon_settings', 'send_to', 'janedoe@gmail.com')
        parser.set('grillcon_settings', 'alert_interval', '600')
        parser.set('grillcon_settings', 'fan_pin', '17')
        parser.set('grillcon_settings', 'led_pin', '14')
        parser.set('grillcon_settings', 'DO', '9')
        parser.set('grillcon_settings', 'DI', '10')
        parser.set('grillcon_settings', 'CS1', '25')
        parser.set('grillcon_settings', 'CS0', '8')
        parser.set('grillcon_settings', 'CLK', '11')

        # with open('grillcon_settings.cfg', 'w') as configfile:
        with open(self.config_file, 'w') as my_config_file:
            parser.write(my_config_file)

        print "created config file"
        RestartController()


class ConfigRead:
    def __init__(self, config_file):
        self.config_file = config_file
        config = ConfigParser.ConfigParser()
        config.read(self.config_file)

        self.database_location = config.get("grillcon_settings", "database_location")
        # self.database_location.strip('"')
        self.fan_tolerance = config.getint("grillcon_settings", "fan_tolerance")
        self.fan_min = config.getint("grillcon_settings", "fan_min")
        self.fan_multiplier = config.getint("grillcon_settings", "fan_multiplier")
        self.delta_temp = config.getint("grillcon_settings", "delta_temp")
        self.write_interval = config.getint("grillcon_settings", "write_interval")
        self.email_address = config.get("grillcon_settings", "email_address")
        # self.email_address.strip('"')
        self.email_password = config.get("grillcon_settings", "email_password")
        # self.email_password.strip('"')
        self.send_to = config.get("grillcon_settings", "send_to")
        # self.send_to.strip('"')
        self.alert_interval = config.getint("grillcon_settings", "alert_interval")
        self.fan_pin = config.getint("grillcon_settings", "fan_pin")
        self.led_pin = config.getint("grillcon_settings", "led_pin")
        self.DO = config.getint("grillcon_settings", "DO")
        self.DI = config.getint("grillcon_settings", "DI")
        self.CS1 = config.getint("grillcon_settings", "CS1")
        self.CS0 = config.getint("grillcon_settings", "CS0")
        self.CLK = config.getint("grillcon_settings", "CLK")


class ConfigSettings:
    config = ConfigParser.ConfigParser()
    config.read("grillcon_settings.cfg")

    def __init__(self):
        pass

    @staticmethod
    def get_setting_string(var):
        result = ConfigSettings.config.get("grillcon_settings", var)
        result.strip('"')
        return str(result)

    @staticmethod
    def get_settings_int(var):
        result = ConfigSettings.config.get("grillcon_settings", var)
        return int(result)


# Class of target variables taken from variables table, input is from user via webpage
class Target:
    def __init__(self, database_location):
        con = sqlite3.connect(database_location)
        cursor = con.cursor()

        cursor.execute(
            "select cook_name, target_temp, finish_temp, ifnull(status, 0) from variables ORDER BY rowid DESC LIMIT 1;")

        while True:
            row = cursor.fetchone()
            if row is None:
                break

            self.target_grill_temp = row[1]
            self.target_cook_name = str(row[0])
            self.target_meat_temp = row[2]
            self.target_status = row[3]
            if self.target_status == '':
                self.target_status = 0
        con.close()

        # CP 12-30-16 adding debugging fake outputs
        # self.target_grill_temp = 225
        # self.target_cook_name = 'test'
        # self.target_meat_temp = 200
        # self.target_status = 1

    def status(self):
        return self.target_status

    def grill_temp(self):
        return self.target_grill_temp

    def output(self):
        return self.target_grill_temp, self.target_meat_temp, self.target_cook_name

    def meat_target(self):
        return self.target_meat_temp


# Class of cook variables taken from grill
class Cook:
    def __init__(self, grill_sensor, meat_sensor):
        self.cook_grill_temp = int(0)
        self.cook_meat_temp = int(0)

        try:
            temp_grill_temp = grill_sensor.readThermocoupleTemp()
            if temp_grill_temp > 0:
                self.cook_grill_temp = int(temp_grill_temp * 9.0 / 5.0 + 32.0)
            else:
                temp_grill_temp = grill_sensor.readThermocoupleTemp()
                if temp_grill_temp > 0:
                    self.cook_grill_temp = int(temp_grill_temp * 9.0 / 5.0 + 32.0)

            temp_meat_temp = meat_sensor.readThermocoupleTemp()
            if temp_meat_temp > 0:
                self.cook_meat_temp = int(temp_meat_temp * 9.0 / 5.0 + 32.0)
            else:
                temp_meat_temp = meat_sensor.readThermocoupleTemp()
                if temp_meat_temp > 0:
                    self.cook_meat_temp = int(temp_meat_temp * 9.0 / 5.0 + 32.0)

        except Exception as e:
            print(e)

        self.cook_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # self.cook_fan_speed = fan_speed)

    def grill_temp(self):
        return self.cook_grill_temp

    def meat_temp(self):
        return self.cook_meat_temp

    def output(self):
        return self.cook_timestamp, self.cook_grill_temp, self.cook_meat_temp


# Class for fan calculation
class Fan:
    def __init__(self, fan_target_temp, fan_grill_temp, fan_min, fan_multiplier, fan_tolerance):
        self.fan_target_temp = fan_target_temp
        self.fan_grill_temp = fan_grill_temp
        self.fan_speed = 0
        self.fan_min = fan_min
        self.fan_multiplier = fan_multiplier
        self.fan_tolerance = fan_tolerance

        # Prevents pwm value from being too low and stalling fan at low temp
        # differences
        # fan_min = ConfigSettings.GetSettingsInt("fan_min")
        # Scales the formula to 1-100 for duty cycle
        # fan_multiplier = ConfigSettings.GetSettingsInt("fan_multiplier")
        # Difference in degrees below target before the fan turns on
        # fan_tolerance = ConfigSettings.GetSettingsInt("fan_tolerance")
        temp_difference = self.fan_target_temp - self.fan_grill_temp

        # simple algorithm to calculate fan speed based on temp difference.
        # sqrt attempts to slow the fan as it nears the target temp to prevent overshoot
        if fan_grill_temp > 0:
            if temp_difference > self.fan_tolerance:
                fan_speed = (math.sqrt(temp_difference) + self.fan_min) * fan_multiplier
                if fan_speed > 100:
                    fan_speed = 100
                self.fan_speed = int(fan_speed)
            else:
                self.fan_speed = int(0)
        else:
            self.fan_speed = int(40)

    def fan_change(self):
        pwm.ChangeDutyCycle(self.fan_speed)
        # if self.fan_speed > 1:
        # led_blink(.25,3)

    def fan_troubleshoot(self):
        print ("target %d" % self.fan_target_temp)
        print "grill temp %d" % self.fan_grill_temp
        print "fan speed %d" % self.fan_speed

    def output(self):
        return self.fan_speed


# class that calls sendEmail for alerts
# noinspection PyBroadException
class AlertSend:
    def __init__(self, login_name, login_pass, send_alert_to):
        self.loginName = login_name
        cipher_instance_alert = cipher_functions.CipherFunctions(key_file)
        self.loginPass = cipher_instance_alert.decode(login_pass)
        self.sendTo = send_alert_to

    def grill_temp_warning(self, grill_temp, target_temp):
        send_subject = "Grill Temp Warning"
        send_text = 'Temp Alert - Current Temp: %s, Target Grill Temp: %s' % (grill_temp, target_temp)
        # send_text = "test simple string"
        # send_text = str(send_text)
        print "sending email as %s and password %s" % (self.loginName, self.loginPass)

        try:
            sendAlert(self.loginName, self.loginPass, self.sendTo, send_subject, send_text)
        except Exception:
            return "grill temp warning email send error"

    def meat_temp_warning(self, grill_temp=0, meat_temp=0):
        send_subject = "Grill Temp Warning"
        send_text = ('Almost Done - Current Meat Temp: %s, Grill Temp is %s' % (meat_temp, grill_temp))
        print "sending email as %s and password %s" % (self.loginName, self.loginPass)

        try:
            sendAlert(self.loginName, self.loginPass, self.sendTo, send_subject, send_text)
        except:
            return "meat temp warning email send error"


# function to blink the LED for display purposes at the box
def led_blink(length, loop):
    for i in range(0, loop):
        GPIO.output(14, GPIO.HIGH)
        time.sleep(length)
        GPIO.output(14, GPIO.LOW)
        time.sleep(length)


# class to write the the database
# noinspection PyUnboundLocalVariable
class DatabaseWrite:
    def __init__(self):
        pass

    @staticmethod
    def log_temperature(database_location, log_timestamp, log_grill_temp, log_meat_temp,
                        log_target_temp, log_fan_speed, log_cook_name):

        con = sqlite3.connect(database_location)
        cursor = con.cursor()

        if log_grill_temp > 0:
            try:
                cursor.execute('''INSERT INTO temps(timestamp, grill_temp,
                            meat_temp, target_temp, fan_speed, cook_name)
                            VALUES(?,?,?,?,?,?)''',
                               (log_timestamp, log_grill_temp,
                                log_meat_temp, log_target_temp,
                                log_fan_speed, log_cook_name))
                print "values written to database"
                print (log_timestamp, log_grill_temp, log_meat_temp, log_target_temp, log_fan_speed, log_cook_name)
                con.commit()
            except Exception as e:
                con.rollback()
                raise e
            finally:
                con.close()

    @staticmethod
    def create_database(database_location):
        connection_est = False
        try:
            con = sqlite3.connect(database_location)
            cursor = con.cursor()
            connection_est = True
            sql = ("create table if not exists " + "variables" + "(cook_name TEXT, target_temp INTEGER, "
                                                                 "finish_temp INTEGER, status INTEGER, "
                                                                 "timestamp DATETIME)")
            cursor.execute(sql)
            con.commit()
            cursor.execute("select Count(*) from variables")
            result = cursor.fetchone()
            number_of_rows = result[0]
            if number_of_rows > 0:
                print ("using existing variables table")
            else:
                cursor.execute("INSERT INTO variables(timestamp) VALUES (?)",
                               (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
                con.commit()

            sql = ("create table if not exists " + "temps" + "(timestamp DATETIME, grill_temp INTEGER,"
                                                             "meat_temp INTEGER, target_temp INTEGER,"
                                                             "fan_speed INTEGER, cook_name TEXT)")
            cursor.execute(sql)
            con.commit()
            cursor.execute("select Count(*) from temps")
            result = cursor.fetchone()
            number_of_rows = result[0]
            if number_of_rows > 0:
                print "using existing temp table"
            else:
                cursor.execute("INSERT INTO temps(timestamp) VALUES (?)",
                               (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
                con.commit()

            sql = ("create table if not exists " + "users" + "(role TEXT, username TEXT, password TEXT)")
            cursor.execute(sql)
            con.commit()
            cursor.execute("select Count(*) from users")
            result = cursor.fetchone()
            number_of_rows = result[0]
            if number_of_rows > 0:
                print "using existing users table"
            else:
                cursor.execute("INSERT INTO users(role, username, password) VALUES (?,?,?)",
                               ("admin", "admin", "admin"))
                con.commit()
        except Exception as e:
            if connection_est:
                con.rollback()
            raise e
        finally:
            con.close()

class RestartController:

        def __init__(self):
            args = sys.argv[:]
            print "restarting program!!!!!"
            args.insert(0, sys.executable)
            if sys.platform == 'win32':
                args = ['"%s"' % arg for arg in args]

            os.execv(sys.executable, args)


class LCDDisplay:
    def __init__(self):
        self.mylcd = i2c_8574.lcd()

    # noinspection PyBroadException
    # @staticmethod
    def writelines(self, grill_temp, meat_temp, target_temp=0, fan_speed=0):

        for i in reversed(xrange(16)):
            # row 1, column 1
            self.mylcd.lcd_display_string_pos(("Grill: %s" % grill_temp) + chr(223) + "       ", 1, i)

            time.sleep(.25)
            # row 2, column 2
            self.mylcd.lcd_display_string_pos(("Meat: %s" % meat_temp) + chr(223) + "       ", 2, i)
        time.sleep(2)
        self.mylcd.lcd_clear()
        if target_temp == 0:
            ip_address_string = "Unavailable"
            try:
                ip_address_string = get_ip_address()
                ip_address_string = ip_address_string.ljust(15, ' ')

            except Exception:
                print 'IP address read error'
                pass


            lcd_ip_string = "IP:%s" % ip_address_string
            x=16

		    #Add blank lines to the end of the string if less than 16 characters for the LCD screen
            if len(lcd_ip_string) < 16:
                lcd_ip_string = '{:16}'.format(lcd_ip_string)

            for i in reversed(xrange(len(lcd_ip_string))):
                #print i
                self.mylcd.lcd_display_string_pos("Status: Off    ", 1, i)  # row 1, column 1
                time.sleep(.25)
                self.mylcd.lcd_display_string_pos(lcd_ip_string, 2, i)  # row 2, column 2
               
			    #if the lcd string is longer than 16 characters, start cutting the beginning of the string to read the end
                x = x-1
                if x < 1:
                    lcd_ip_string = lcd_ip_string[1:]
        else:
            for i in reversed(xrange(16)):
                # row 1, column 1
                self.mylcd.lcd_display_string_pos(("Target: %s" % target_temp) + chr(223) + "      ", 1, i)
                time.sleep(.25)
                # row 2, column 3
                self.mylcd.lcd_display_string_pos(("Fan Spd: %s" % fan_speed) + "%      ", 2, i)
        time.sleep(2)
        self.mylcd.lcd_clear()

    # @staticmethod
    def clear_off(self):

        self.mylcd.lcd_clear()
        self.mylcd.backlight(0)

class Controller:
    
    def __init__(self):

        self.use_LCD = True
        self.debug = True

        self.path = os.path.dirname(os.path.realpath(__file__))
        self.config_file_name = "grillcon_settings.cfg"
        self.key_file_name = "key.txt"
        self.config_file_location = os.path.join(self.path, self.config_file_name)
        self.key_file_location = os.path.join(self.path, self.key_file_name)

        self.mylcd = i2c_8574.lcd()

        myConfigCreate = ConfigCreate(self.config_file_location)
        #ConfigCreate(self.config_file_location)
        self.settings_object = ConfigRead(self.config_file_location)

        # Board Setup
        GPIO.setmode(GPIO.BCM)  # This example uses the BCM pin numbering
        self.fan_pin = self.settings_object.fan_pin
        self.led_pin = self.settings_object.led_pin

        # Output Setup
        GPIO.setup(self.fan_pin, GPIO.OUT)  # GPIO 17 is set for the fan output.
        GPIO.setup(self.led_pin, GPIO.OUT)  # GPIO 14 is set for the LED output.

        # SPI config
        self.CLK = self.settings_object.CLK
        self.CS0 = self.settings_object.CS0
        self.CS1 = self.settings_object.CS1   
        self.DO = self.settings_object.DO
        self.DI = self.settings_object.DI
        self.grill_sensor = max31856.max31856(self.CS0, self.DO, self.DI, self.CLK)
        self.meat_sensor = max31856.max31856(self.CS1, self.DO, self.DI, self.CLK)

        # PWM logic
        self.pwm = GPIO.PWM(17, 60)  # pwm is an object on BCM pin 17 and default is 60hz)
        self.pwm.start(0)  # Starts the pwm set to off

        self.database_location = self.settings_object.database_location

        # check to see if tables exist and create if necessary
        DatabaseWrite.create_database(self.database_location)

        # counter = datetime.datetime.now()
        self.counter = datetime.datetime.now()
        self.database_write = datetime.datetime.now() - datetime.timedelta(seconds=60)

        # counter for back light timeout
        self.timeout = 0

        self.cipher_instance = cipher_functions.CipherFunctions(self.key_file_location)

        self.config_modified = os.path.getmtime(self.config_file_location)
        

        if self.debug == True:
            print 'full path is %s' % self.config_file_location
            print 'cs0 pin %s ' % self.CS0
            print 'cs1 pin %s ' % self.CS1
            print "grillcon config last modified on %s" % self.config_modified
            print "Email address is %s" % self.settings_object.email_address
            print "Password is %s" % self.settings_object.email_password
            print "Password is %s" % self.cipher_instance.decode(self.settings_object.email_password)

    def start(self):

        while True:
            try:
                # change class to SQL query
                self.target_instance = Target(self.database_location)
                if self.target_instance.status() == 0:
                    # led_blink(2,2)
                    self.pwm.ChangeDutyCycle(0)    
                    if self.timeout < 20:
                        # create a cook object that gets current temps from both thermometers
                        self.cook_instance = Cook(self.grill_sensor, self.meat_sensor)
                        if self.use_LCD:
                            self.my_LCD = LCDDisplay()
                            self.my_LCD.writelines(self.cook_instance.grill_temp(), self.cook_instance.meat_temp())
                    elif self.timeout == 20 and self.use_LCD:
                        self.my_LCD = LCDDisplay()
                        self.my_LCD.clear_off()
                        print "turned LCD off"

                    else:
                        time.sleep(5)
                    self.timeout += 1
                    print "waiting"
                    self.counter = datetime.datetime.now()

                elif self.target_instance.status() == 1:
                    try:
                        print "target is %s" % (self.target_instance.grill_temp())
                        # create a cook object that gets current temps from both thermometers
                        self.cook_instance = Cook(self.grill_sensor, self.meat_sensor)
                        print "grill temp is %s" % (self.cook_instance.grill_temp())
                        print "meat temp is %s" % (self.cook_instance.meat_temp())
                        # create an object of the fan class passing the target grill temp and the current grill temp
                        self.fan_instance = Fan(self.target_instance.grill_temp(), self.cook_instance.grill_temp(),
                                           self.settings_object.fan_min, self.settings_object.fan_multiplier,
                                           self.settings_object.fan_tolerance)
                        # create variables for the log_temperature function
                        self.my_timestamp, self.my_grill_temp, self.my_meat_temp = self.cook_instance.output()
                        self.my_target_grill_temp, self.my_target_meat_temp, self.my_cook_name = self.target_instance.output()
                        self.my_fan_speed = self.fan_instance.output()

                        # troubleshooting method below, prints out speed
                        if self.debug == True:
                            self.fan_instance.fan_troubleshoot()
                        # change fan speed
                        self.fan_instance.fan_change()

                        # log temperature function
                        self.write_interval = self.settings_object.write_interval
                        if datetime.datetime.now() > (self.database_write + datetime.timedelta(seconds=self.write_interval)):
                            self.database_write = datetime.datetime.now()
                            if self.my_grill_temp > 0:
                                DatabaseWrite.log_temperature(self.database_location, self.my_timestamp, self.my_grill_temp, 
                                                              self.my_meat_temp, self.my_target_grill_temp,
                                                              self.my_fan_speed, self.my_cook_name)

                        # if temperature is +-20 from target, and 10 minutes has elapsed,
                        # send alert
#Todo move these variables where they aren't constantly redefined
                        self.alert_interval = self.settings_object.alert_interval
                        if datetime.datetime.now() > (self.counter + datetime.timedelta(seconds=self.alert_interval)):
                            self.delta_temp = self.settings_object.delta_temp
                            self.email_address = self.settings_object.email_address
                            self.email_password = self.settings_object.email_password
                            self.send_to = self.settings_object.send_to
                            if self.my_grill_temp > (self.target_instance.grill_temp() + self.delta_temp) or self.my_grill_temp < \
                                    (self.target_instance.grill_temp() - self.delta_temp):
                                AlertSend(self.email_address, self.email_password, self.send_to).grill_temp_warning(self.my_grill_temp,
                                                                                                     self.my_target_grill_temp)
                                # if meat is within 1 degree of target, send SMS
                            if self.my_meat_temp > (self.my_target_meat_temp - 2):
                                AlertSend(self.email_address, self.email_password, self.send_to).meat_temp_warning(self.my_grill_temp,
                                                                                                    self.my_meat_temp)
                            # when thermister value is wrong, method returns grill temp as 0.
                            # if 0, sens SMS
                            if self.my_grill_temp < 1:
                                AlertSend(self.email_address, self.email_password, self.send_to).grill_temp_warning(my_grill_temp,
                                                                                                     my_target_grill_temp)
                            self.counter = datetime.datetime.now()
                        if self.use_LCD:
                            self.my_LCD = LCDDisplay()
                            self.my_LCD.writelines(self.my_grill_temp, self.my_meat_temp, self.my_target_grill_temp, self.my_fan_speed)
                        # CP 10/16 modifying path for system.d
                        # if config_modified != os.path.getmtime('grillcon_settings.cfg'):
                        if self.config_modified != os.path.getmtime(self.config_file_location):
                            RestartController()
                            # time.sleep(5)
                    except:
                        print "Unexpected error:"  # , test.info()[0]
                        raise

            except IOError:
                print("IO Error")
            except KeyboardInterrupt:
                GPIO.cleanup()  # clean up GPIO on CTRL+C exit
                sys.exit()
