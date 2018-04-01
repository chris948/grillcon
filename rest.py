
#!/usr/bin/env python

from __future__ import generators  # needs to be at the top of your module
import os
import sys
import sqlite3
import time
import datetime
import cipher_functions
import shutil
from bottle import Bottle, route, run, debug, template, request, static_file, error, url, auth_basic, redirect
import ConfigParser
import collections
from sendAlert import sendAlert
from sqlhelpers import SQLHelpers
from queries import SQLQueries

# class to read the config settings file and update output variables
class ConfigSettings:
    def __init__(self, config_file):
        self.config_file = config_file
        #self.key_file = key_file
        self.parser = ConfigParser.ConfigParser()
        # parser.read("grillcon_settings.cfg")
        self.parser.read(self.config_file)

    # @staticmethod
    def get_settings_string(self, var):

        result = self.parser.get("grillcon_settings", var)
        result.strip('"')
        return str(result)

    # @staticmethod
    def get_settings_int(self, var):

        var = self.parser.get("grillcon_settings", var)
        return int(var)

    # @staticmethod
    def get_settings_dict(self):

        # list_tuples = []
        dict_settings = {}

        for name, value in self.parser.items("grillcon_settings"):
            dict_settings[name] = value
        return dict_settings

    # generate a list of the settings and values, this will be used to create an ordered dictionary
    # @staticmethod
    def get_settings_lists(self):

        key_a = []
        value_b = []

        for name, value in self.parser.items("grillcon_settings"):
            key_a.append(name)
            value_b.append(value)

        return key_a, value_b

    @staticmethod
    def update_settings_file(dict_new_settings):

        parser = ConfigParser.SafeConfigParser()
        parser.add_section('grillcon_settings')

        for key, value in dict_new_settings.iteritems():
            parser.set('grillcon_settings', key, value)

        with open('grillcon_settings.cfg', 'wb') as configfile:
            parser.write(configfile)

        print "updated settings file"
        time.sleep(1.0)

        RestartGrillcon.restart_script()

class RestartGrillcon:

    # function to restart the grillcon_rest script
    def restart_script():
        args = sys.argv[:]
        print "restarting program!!!!!"
        args.insert(0, sys.executable)
        if sys.platform == 'win32':
            args = ['"%s"' % arg for arg in args]

        os.execv(sys.executable, args)

class Validations:

    @staticmethod
    def validate_input_grill_int(send_cook_target, send_cook_finish):
        if (0 < send_cook_target <= 1000) and (0 < send_cook_finish <= 400):
            return True
        else:
            return False

    @staticmethod
    def validate_input(database_location, send_cook_name, send_cook_target, send_cook_finish):
	print'entering validations'
        try:
            send_cook_name = str(send_cook_name)
            send_cook_target = int(send_cook_target)
            send_cook_finish = int(send_cook_finish)
        except Exception:
            print "An validate input error occurred"

        # check that the option is within a specific range
        # if (send_cook_target > 0 and send_cook_target <= 1000) and (send_cook_finish > 0 and send_cook_finish <= 1000):
        if Validations.validate_input_grill_int(send_cook_target, send_cook_finish):
            print 'validated 1'
            if (send_cook_name == "Brisket" or
                    send_cook_name == "Shoulder Roast" or
                    send_cook_name == "Ribs" or
                    send_cook_name == "Other"):
                print 'validated 2'

                today = datetime.datetime.now().date()
                send_cook_name = send_cook_name + " " + str(today)
                tuple_send_cook = (send_cook_name, send_cook_target, send_cook_finish, 1,)

                SQLQueries().write_input(database_location, tuple_send_cook)
                print "ran write_input"

        else:
	    print 'returning none'
            return None

    @staticmethod
    def validate_input_modify(database_location, send_cook_target, send_cook_finish):
        try:
            send_cook_target = int(send_cook_target)
            send_cook_finish = int(send_cook_finish)
            # call last row of database, use name column result
            dict_variables_template = SQLQueries.variables_last_row_results(database_location)
            send_cook_name = dict_variables_template["name"]

            # check that the option is within a specific range
            if Validations.validate_input_grill_int(send_cook_target, send_cook_finish):
                tuple_send_cook = (send_cook_name, send_cook_target, send_cook_finish, 1,)
                SQLQueries().write_input(database_location, tuple_send_cook)
        except Exception:
            print "An modify cook error occurred"
        else:
            return None

class GetSettings():

	def __init__(self):
	
	        self.os_path = os.path.dirname(os.path.realpath(__file__))
	
	        self.settings_file = "grillcon_settings.cfg"
	        self.key_file = "key.txt"
	
	        self.grillcon_off_template = self.os_path + "/views/grillcon_main_off.tpl"
	        self.grillcon_on_template = self.os_path + "/views/grillcon_main_on.tpl"
	        self.grillcon_history_template = self.os_path + "/views/grillcon_history.tpl"
	        self.grillcon_admin_template = self.os_path + "/views/grillcon_admin.tpl"
	        self.grillcon_icon_file = self.os_path + "/static/favicon.ico"
	
	        self.settings_file = os.path.join(self.os_path, self.settings_file)
	        self.key_file = os.path.join(self.os_path, self.key_file)
    
                self.read_config_settings = ConfigSettings(self.settings_file)
    	        self.database_location = self.read_config_settings.get_settings_string("database_location")
       		print "database location is %s" % self.database_location
		
	def getOffTemplate(self):
		return self.grillcon_off_template
	
	def getOnTemplate(self):
		return self.grillcon_on_template

	def getHistoryTemplate(self):
		return self.grillcon_history_template

	def getAdminTemplate(self):
		return self.grillcon_admin_template
	
	def getIconFile(self):
		return self.grillcon_icon_file

	def getKeyFile(self):
		return self.key_file

	def getSettingsFile(self):
		return self.settings_file

	def getDatabaseFile(self):
		return self.database_location

class BottleServer(Bottle):

    def __init__(self):

        super(BottleServer, self).__init__()

	mySettings = GetSettings()
	

	self.grillcon_off_template = mySettings.getOffTemplate()
	self.grillcon_on_template = mySettings.getOnTemplate()
	self.grillcon_history_template = mySettings.getHistoryTemplate()
	self.grillcon_admin_template = mySettings.getAdminTemplate()
        self.grillcon_icon_file = mySettings.getIconFile()
	
	self.my_key_file = mySettings.getKeyFile()
	self.my_settings_file = mySettings.getSettingsFile()
	self.database_location = mySettings.getDatabaseFile()

        #self._host = host
        #self._port = port
        #self._app = Bottle()
        self.route('/main', method=['GET', 'POST'], callback=self.main)
        self.route('/history', method=['GET', 'POST'], callback=self.history)
        self.route('/admin', callback=self.admin)
        self.route('/admin', method='POST', callback=self.admin_post)
        self.route('/json', callback=self.json)
        self.route('/getupdate.json', callback=self.json_getupdates)
        #self.route('/favicon.ico', method='GET', callback=self.get_favicon)
        self.route('/', callback=self.index)
        self.route('/static/css<filepath:re:.*\.css>', callback=self.css)
        self.route('/static/ico<filepath:re:.*\.ico>', callback=self.ico)
        self.route('error(403)', callback=self.mistake403)
        self.route('error(404)', callback=self.mistake404)
        
    def auth_check(username, password):

	mySettings = GetSettings()
	database_location = mySettings.getDatabaseFile()

        list_user = SQLQueries().user_query(database_location, 'admin')

        if username == list_user[1] and password == list_user[2]:
            return True

    def main(self):
        # if user sends post data to start the grill, validate fields and
        # set status in temps database to 1, where grillcon is looking
        if request.POST.get('Start Grill Controller', '').strip():
            self.send_cook_name = request.POST.get('option_cook_name', '').strip()
            self.send_cook_target = request.POST.get('option_target_temp', '').strip()
            self.send_cook_finish = request.POST.get('option_finish_temp', '').strip()
            # send user inputs to validate function
            print 'trying validations'
            Validations.validate_input(self.database_location, self.send_cook_name, self.send_cook_target, self.send_cook_finish)
            time.sleep(7.0)
            redirect('/main')

        if request.POST.get('Modify Current Cook', '').strip():
            self.send_cook_target = request.POST.get('option_target_temp', '').strip()
            self.send_cook_finish = request.POST.get('option_finish_temp', '').strip()
            # send to validate data function
            Validations.validate_input_modify(self.database_location, send_cook_target, send_cook_finish)
            time.sleep(5.0)
            redirect('/main')

        # if receive option off, create tuple with None and 0 turning off the controller
        if request.POST.get('option_off', '').strip():
            self.tuple_send_cook = (None, None, None, 0)
            SQLQueries().write_input(self.database_location, self.tuple_send_cook)
            print "Option Off Received!!"
            return template(self.grillcon_off_template, get_url=url)

        # if notesSubmit, update the notes table for the current cook
        if request.forms.get('notesSubmit'):
            print 'notes received'

            self.new_notes = request.POST.get("notes", '').strip()

            SQLQueries().update_notes(self.database_location, new_notes)
            redirect('/main')

        else:
	    print "DATABASE LOCATION"
	    print self.database_location
            # call last row results into a dictionary
            self.dict_variables_template = SQLQueries.variables_last_row_results(self.database_location)
            # if 'status' == 1 the grill controller is on
            if self.dict_variables_template["status"] == 1:
                # populate the dictionary to create the web page showing the controller as on
                self.dict_variables_row = self.dict_variables_template
                # get last row cook name
                self.dict_temps_row = SQLQueries.dict_temps_last_row_results(self.database_location)
                self.last_cook_name = self.dict_temps_row["name"]
                # get records for last row cook name
                self.cook_row_result = SQLQueries.cook_rows(self.database_location, self.last_cook_name)
                # make chart for last row cook name
                self.cook_graph = SQLHelpers.chart_list(self.cook_row_result)
                # get notes for the last cook
                self.cook_notes = SQLQueries.cook_notes(self.database_location, self.last_cook_name)

                return template(self.grillcon_on_template, get_url=url, rows=self.cook_graph,
                                dict_variables_row=self.dict_variables_row, dict_temps_row=self.dict_temps_row, cook_notes=self.cook_notes)

            else:
                # print "file path is %s /n template path is %s /n complete file is %s" %
                # (path, grillcon_off_template, template_path)
                return template(self.grillcon_off_template, get_url=url)


    #@route('/history', method=['GET', 'POST'])
    def history(self):
        if request.forms.get('historyName'):
            # postdata = request.body.read()
            # show data received from client for debugging purposes
            # print postdata
            # graph value equals the user input selecting a cook name to populate a graph
            self.graph_value = request.forms.get('historyName')
            # get records for the last cook name
            self.cook_row_result = SQLQueries().cook_rows(self.database_location, self.graph_value)
            # make chart for last cook name
            self.cook_graph = SQLHelpers.chart_list(self.cook_row_result)
            self.cook_list = SQLQueries().cook_history(self.database_location)
            self.cook_notes = SQLQueries.cook_notes(self.database_location, self.graph_value)

            return template(self.grillcon_history_template, get_url=url, rows=self.cook_graph, list=self.cook_list,
                            cook_notes=self.cook_notes, graph_value=self.graph_value)

        # if notesSubmit, update the notes table for the specified cook
        if request.forms.get('notesSubmit'):
            # print 'history notes received'
            self.cook_name = request.POST.get("hidden", '').strip()
            self.new_notes = request.POST.get("notes", '').strip()
            # print 'new_notes are %s' % (new_notes)
            # print "the notes cook name is %s" % (cook_name)
            SQLQueries().update_notes(self.database_location, self.new_notes, self.cook_name)

            # redundant with above, possible method?

            self.graph_value = self.cook_name
            # get records for the last cook name
            self.cook_row_result = SQLQueries().cook_rows(self.graph_value)
            # make chart for last cook name
            self.cook_graph = SQLHelpers.chart_list(self.cook_row_result)
            self.cook_list = SQLQueries().cook_history()
            self.cook_notes = SQLQueries.cook_notes(self.graph_value)

            return template(self.grillcon_history_template, get_url=url, rows=self.cook_graph, list=self.cook_list,
                            cook_notes=self.cook_notes, graph_value=self.graph_value)

        else:

            self.dict_temps_row = SQLQueries.dict_temps_last_row_results(self.database_location)
            # print SQLQueries.temps_last_row_results(self.database_location)
            # get last row cook name
            self.last_cook_name = self.dict_temps_row["name"]
            # get records for the last cook name
            self.cook_row_result = SQLQueries.cook_rows(self.database_location, self.last_cook_name)
            # make chart for last cook name
            self.cook_graph = SQLHelpers.chart_list(self.cook_row_result)
            self.cook_list = SQLQueries().cook_history(self.database_location)
            self.cook_notes = SQLQueries.cook_notes(self.database_location, self.last_cook_name)

            return template(self.grillcon_history_template, get_url=url, rows=self.cook_graph, list=self.cook_list,
                            cook_notes=self.cook_notes, graph_value=self.last_cook_name)


    @auth_basic(auth_check)
    def admin(self):
        # print 'authorized request received',
        # print request.auth
        # print 'remote_address', request.remote_addr
        self.my_settings = ConfigSettings(self.my_settings_file)
        self.dict_settings = self.my_settings.get_settings_dict()
        self.list_user = SQLQueries().user_query(self.database_location, 'admin')

        # to keep the list in order, get_settings_lists returns 2 lists, key and value
        # they are combined to make a OrderedDict dictionary
        self.list_a, self.list_b = self.my_settings.get_settings_lists()
        self.list_settings = collections.OrderedDict(zip(self.list_a, self.list_b))

        # cipher_instance = cipher_functions.CipherFunctions(key_file)
        # print "Plaintext password is %s" % cipher_instance.decode(dict_settings['email_password'])

        return template(self.grillcon_admin_template,
                        cook_list=SQLQueries().cook_history(self.database_location),
                        dict_settings=self.dict_settings,
                        list_settings=self.list_settings,
                        get_url=url,
                        list_user=self.list_user,
                        )

    #@route('/admin', method='POST')
    def admin_post(self):
        # postdata = request.body.read()
        # print postdata  # this goes to log file only, not to client

        if request.forms.get('settingsSubmit'):
            print "settings info received"
            self.dict_new_settings = ({
                "database_location": request.POST.get("database_location", '').strip(),
                "fan_min": request.POST.get("fan_min", '').strip(),
                "fan_tolerance": request.POST.get("fan_tolerance", '').strip(),
                "fan_multiplier": request.POST.get("fan_multiplier", '').strip(),
                "delta_temp": request.POST.get("delta_temp", '').strip(),
                "write_interval": request.POST.get("write_interval", '').strip(),
                "email_address": request.POST.get("email_address", '').strip(),
                "email_password": request.POST.get("email_password", '').strip(),
                "send_to": request.POST.get("send_to", '').strip(),
                "alert_interval": request.POST.get("alert_interval", '').strip(),
                "fan_pin": request.POST.get("fan_pin", '').strip(),
                "led_pin": request.POST.get("led_pin", '').strip(),
                "clk": request.POST.get("clk", '').strip(),
                "cs0": request.POST.get("cs0", '').strip(),
                "cs1": request.POST.get("cs1", '').strip(),
                "do": request.POST.get("do", '').strip(),
                "di": request.POST.get("di", '').strip(),
            })
            self.cipher_instance = cipher_functions.CipherFunctions(key_file)
            self.dict_new_settings["email_password"] = \
                cipher_instance.encode(self.dict_new_settings["email_password"])
            ConfigSettings.update_settings_file(self.dict_new_settings)

        if request.forms.get('backupSubmit'):
            # print 'backup request received'
            SQLQueries.sqlite3_backup(self.database_location)

        if request.forms.get('historyName'):
            # print 'history delete request received'
            self.value = request.POST.get('historyName')
            SQLQueries().delete_cook(self.database_location, self.value)

        if request.forms.get('userSubmit'):

            self.tuple_new_users = (
                request.POST.get("user_username", '').strip(),
                request.POST.get("user_password", '').strip(),
                request.POST.get("user_role", '').strip(),
            )

            SQLQueries().update_user(self.database_location, self.tuple_new_users)

        if request.POST.get('testMail', '').strip():
            print 'test_mail received'
            try:
                self.dict_settings = my_config_file.get_settings_dict()
                self.login_name = dict_settings['email_address']
                self.cipher_instance = cipher_functions.CipherFunctions(self.key_file)
                self.login_pass = cipher_instance.decode(self.dict_settings['email_password'])
                self.send_to = dict_settings['send_to']
                self.send_subject = 'test from grillcon'
                self.send_text = 'test sent at %s ' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                sendAlert(self.login_name, self.login_pass, self.send_to, self.send_subject, self.send_text)
            except Exception:
                return "a testmail error occurred"

        redirect('/admin')


    #@route('/json')
    def json(self):
        return template('json')


    #@route('/getupdate.json')
    def json_getupdates(self):
        # postdata = request.body.read()
        # print postdata  # this goes to log file only, not to client
        self.temps_timestamp, self.temps_grill_temp, self.temps_meat_temp, self.temps_fan = SQLQueries.temps_last_row_results(self.database_location)

        self.items = {"0": self.temps_grill_temp, "1": self.temps_meat_temp, "2": self.temps_fan, "3": self.temps_timestamp}
        # print items["1"]
        return self.items

    def get_favicon(self):
        return self.static_file('favicon.ico', root='/static/')
        # return grillcon_icon_file

    def index(self):
        redirect('/main')
    # return { 'get_url': get_url }

    def css(self, filepath):
        return static_file(filepath, root='static/css')

    def ico(self, filepath):
        return static_file(filepath, root='static/ico')

    def mistake403(self):
        return 'There is a mistake in your url! - grillcon_rest'

    def mistake404(self):
        return 'Sorry, this page does not exist! - grillcon_rest'

if __name__ == "__main__":
    myWebApp = BottleServer()
    myWebApp.run(host='localhost', port=8080)
    #myWebApp.run(host='localhost', port=8080, debug=True)

