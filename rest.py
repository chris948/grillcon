from __future__ import generators  # needs to be at the top of your module
import os
import sys
import sqlite3
import time
import datetime
import cipher_functions
import shutil
from bottle import route, run, debug, template, request, static_file, error, url, auth_basic, redirect
import ConfigParser
import collections
from sendAlert import sendAlert

os_path = os.path.dirname(os.path.realpath(__file__))

settings_file = "grillcon_settings.cfg"
key_file = "key.txt"

grillcon_off_template = os_path + "/views/grillcon_main_off.tpl"
grillcon_on_template = os_path + "/views/grillcon_main_on.tpl"
grillcon_history_template = os_path + "/views/grillcon_history.tpl"
grillcon_admin_template = os_path + "/views/grillcon_admin.tpl"
grillcon_icon_file = os_path + "/static/favicon.ico"

config_file = os.path.join(os_path, settings_file)
key_file = os.path.join(os_path, key_file)


# class to read the config settings file and update output variables
class ConfigSettings:
    def __init__(self):
        # my_file_paths = settings_file
        self.parser = ConfigParser.ConfigParser()
        # parser.read("grillcon_settings.cfg")
        self.parser.read(config_file)

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

        # for item in key_a:
            # print item

        # for item in value_b:
            # print item

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

        restart_script()


# function to restart the grillcon_rest script
def restart_script():
    args = sys.argv[:]
    print "restarting program!!!!!"
    args.insert(0, sys.executable)
    if sys.platform == 'win32':
        args = ['"%s"' % arg for arg in args]

    os.execv(sys.executable, args)

my_config_settings = ConfigSettings()
database_location = my_config_settings.get_settings_string("database_location")
print "database location is %s" % database_location


# class of methods to access the sql database

class SqlHelpers:
    def __init__(self):
        pass

    # method for sending sql query and not returning anything
    @staticmethod
    def execute(sql, parameters=None):
        con = sqlite3.connect(database_location)
        cursor = con.cursor()
        # print sql
        # print parameters
        try:
            cursor.execute(sql, parameters)
            con.commit()
        except sqlite3.Error as e:
            print "An error occurred:", e.args[0]
        con.close()

    # method for sending sql query and returning all results
    @staticmethod
    def query(sql, parameters=None):
        con = sqlite3.connect(database_location)
        cursor = con.cursor()
        try:
            cursor.execute(sql, parameters)
            while True:
                row = cursor.fetchall()
                if row is None:
                    break
                yield row
        except Exception:
            print 'query error'
        con.close()

    # method for sending sql query and returning many results
    @staticmethod
    def large_query(sql, array_size=200):
        con = sqlite3.connect(database_location)
        cursor = con.cursor()
        cursor.execute(sql)
        while True:
            results = cursor.fetchmany(array_size)
            if not results:
                break
            for result in results:
                yield result
        con.close()

    # method for sending sql query and returning one row
    @staticmethod
    def query_one(sql, parameters=None):
        con = sqlite3.connect(database_location)
        cursor = con.cursor()
        if parameters is not None:
            cursor.execute(sql, parameters)
        else:
            cursor.execute(sql)
        row = cursor.fetchone()

        con.close()
        return row

    # method for returning one column of the sql query result
    @staticmethod
    def query_scalar(sql, parameters=None):
        con = sqlite3.connect(database_location)
        cursor = con.cursor()

        try:
            cursor.execute(sql, parameters)
            con.commit()
        except sqlite3.Error as e:
            print "A scalar error occurred:", e.args[0]

        row = cursor.fetchone()

        con.close()
        return row

    # query for returning text results
    @staticmethod
    def query_text(sql, parameters=None):
        con = sqlite3.connect(database_location)
        cursor = con.cursor()
        con.text_factory = str
        if parameters is not None:
            cursor.execute(sql, parameters)
        else:
            cursor.execute(sql)
        row = cursor.fetchall()

        con.close()
        return row


class SQLQueries(object):
    # method to return the last row in the variables database
    @staticmethod
    def variables_last_row_results():

        last_row_query = "select cook_name, target_temp, finish_temp, ifnull(status, 0) " \
                         "from variables ORDER BY rowid DESC LIMIT 1;"
        row = SqlHelpers.query_one(last_row_query)
        # if row == None:
        # return ##fix 
        variables_cook_name = str(row[0])
        variables_grill_temp = row[1]
        variables_finish_temp = row[2]
        variables_status = row[3]

        dict_variables_template = {"name": variables_cook_name, "target": variables_grill_temp,
                                   "finish": variables_finish_temp, "status": variables_status}
        return dict_variables_template

    # method to return the last row in the temps database
    @staticmethod
    def temps_last_row_results():

        last_row_query = "SELECT * FROM temps WHERE cook_name IS NOT NULL ORDER BY rowid DESC limit 1;"
        row = SqlHelpers.query_one(last_row_query)

        temps_timestamp = str(row[0])
        temps_grill_temp = str(row[1])
        temps_meat_temp = str(row[2])
        temps_fan = str(row[4])

        return temps_timestamp, temps_grill_temp, temps_meat_temp, temps_fan

    # method to return a dictionary of the last row in the temps database
    @staticmethod
    def dict_temps_last_row_results():

        last_row_query = "SELECT * FROM temps WHERE cook_name IS NOT NULL ORDER BY rowid DESC limit 1;"
        row = SqlHelpers.query_one(last_row_query)

        temps_timestamp = str(row[0])
        temps_grill_temp = row[1]
        temps_meat_temp = row[2]
        temps_fan = row[4]
        temps_cook_name = row[5]

        dict_temps_template = {"timestamp": temps_timestamp, "grill_temp": temps_grill_temp,
                               "meat_temp": temps_meat_temp, "fan": temps_fan, "name": temps_cook_name}
        return dict_temps_template

    # method to return the rows given a cook name
    @staticmethod
    def cook_rows(cook_name):

        if cook_name != "":
            cook_name = (cook_name,)
            cook_name_query = "SELECT * FROM temps WHERE cook_name = ?"

            for result in SqlHelpers.query(cook_name_query, cook_name):
                return result
                # print "returning %s" % (result)

        else:
            # return rows([datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0, 0])
            pass

    # method to select a list of previous cooks
    @staticmethod
    def cook_history():

        list_history = []
        cook_history_query = "SELECT DISTINCT cook_name FROM temps ORDER BY timestamp DESC;"

        for result in SqlHelpers.query_text(cook_history_query):
            list_history.append(str(result[0]))

        return list_history

    # method to return the notes given a cook name
    @staticmethod
    def cook_notes(cook_name):
        cook_name = (cook_name,)
        cook_name_query = "SELECT cook_notes FROM notes WHERE cook_name = ?"
        result = str(SqlHelpers.query_scalar(cook_name_query, cook_name))
        return result

    # method to return the specified role in users table
    @staticmethod
    def user_query(role):
        # type: (object) -> object
        role = (role,)
        user_query = "SELECT * FROM users WHERE role = ?"

        row = SqlHelpers.query_one(user_query, role)
        # for row in all_rows:
        role = row[0]
        username = row[1]
        password = row[2]
        list_user = [role, username, password]
        return list_user

    # method to update the user row in users table
    @staticmethod
    def update_user(tuple_update_user):

        update_user_query = "UPDATE users SET username=?, password=? WHERE role=?"
        # tuple_update_user = (user_row["username"], user_row["password"], user_row["role"])
        SqlHelpers.execute(update_user_query, tuple_update_user)
        print "SQL database updated with role %s, user %s, password %s" % \
              (tuple_update_user[2], tuple_update_user[0], tuple_update_user[1])

    # method to delete all rows of specified cook name
    @staticmethod
    def delete_cook(cook_name):

        delete_cook_query = "DELETE FROM temps WHERE cook_name=?"
        tuple_cook_name = (cook_name,)
        SqlHelpers.execute(delete_cook_query, tuple_cook_name)
        print "deleted the %s cook" % tuple_cook_name

    # method to write cook variables into the database
    @staticmethod
    def write_input(tuple_send_cook):

        write_input_query = "INSERT INTO variables(cook_name, target_temp, finish_temp, status) VALUES(?,?,?,?)"
        SqlHelpers.execute(write_input_query, tuple_send_cook)

    # method to update the notes table
    @staticmethod
    def update_notes(new_note, cook_name=None):

        if cook_name is None:
            # call last row of database, use name column result
            dict_variables_template = SQLQueries.variables_last_row_results()
            cook_name = dict_variables_template["name"]

        tuple_cook_name = (cook_name,)
        select_name_query = "SELECT cook_notes FROM notes WHERE cook_name = ?"
        my_result = SqlHelpers.query_one(select_name_query, tuple_cook_name)
        print (my_result)
        if my_result is None:
            print "None"
            tuple_new_note = (cook_name, new_note,)
            select_name_query = "INSERT INTO notes(cook_name, cook_notes) VALUES(?,?)"
            SqlHelpers.execute(select_name_query, tuple_new_note)
        else:
            print "not None"
            tuple_new_note = (new_note, cook_name,)
            update_notes_query = "UPDATE notes SET cook_notes=? WHERE cook_name=?"
            SqlHelpers.execute(update_notes_query, tuple_new_note)
        print "SQL database updated with note %s, table %s" % (tuple_new_note[0], tuple_new_note[1])

    # Create timestamped database copy
    @staticmethod
    def sqlite3_backup():
        con = sqlite3.connect(database_location)
        cursor = con.cursor()

        # backup_location = ConfigSettings.get_settings_string("backup_location")
        backup_file = 'templog.db' + time.strftime("-%Y%m%d-%H%M%S")

        # Lock database before making a backup
        cursor.execute('begin immediate')
        # Make new backup file
        shutil.copyfile(database_location, backup_file)
        print ("\nCreating {}...".format(backup_file))
        # Unlock database
        con.rollback()
        con.close()


def validate_input_grill_int(send_cook_target, send_cook_finish):
    if (0 > send_cook_target > 1000) and (0 > send_cook_finish >= 1000):
        return True
    else:
        return False



def validate_input(send_cook_name, send_cook_target, send_cook_finish):
    try:
        send_cook_name = str(send_cook_name)
        send_cook_target = int(send_cook_target)
        send_cook_finish = int(send_cook_finish)
    except Exception:
        print "An validate input error occurred"

    # check that the option is within a specific range
    # if (send_cook_target > 0 and send_cook_target <= 1000) and (send_cook_finish > 0 and send_cook_finish <= 1000):
    if validate_input_grill_int(send_cook_target, send_cook_finish):
        # print 'validated 1'
        if (send_cook_name == "Brisket" or
                send_cook_name == "Shoulder Roast" or
                send_cook_name == "Ribs" or
                send_cook_name == "Other"):
            # print 'validated 2'

            today = datetime.datetime.now().date()
            send_cook_name = send_cook_name + " " + str(today)
            tuple_send_cook = (send_cook_name, send_cook_target, send_cook_finish, 1,)

            SQLQueries().write_input(tuple_send_cook)

    else:
        return None



def validate_input_modify(send_cook_target, send_cook_finish):
    try:
        send_cook_target = int(send_cook_target)
        send_cook_finish = int(send_cook_finish)
        # call last row of database, use name column result
        dict_variables_template = SQLQueries.variables_last_row_results()
        send_cook_name = dict_variables_template["name"]

        # check that the option is within a specific range
        if validate_input_grill_int(send_cook_target, send_cook_finish):
            tuple_send_cook = (send_cook_name, send_cook_target, send_cook_finish, 1,)
            SQLQueries().write_input(tuple_send_cook)
    except Exception:
        print "An modify cook error occurred"
    else:
        return None


# convert rows from database into a list
def chart_list(rows):
    chart_table = ""

    for row in rows[:-1]:
        rowstr = "['{0}', {1}, {2}],\n".format(str(row[0]), str(row[1]), str(row[2]))
        chart_table += rowstr

    row = rows[-1]
    rowstr = "['{0}', {1}, {2}],\n".format(str(row[0]), str(row[1]), str(row[2]))
    chart_table += rowstr

    return chart_table


def auth_check(username, password):
    list_user = SQLQueries().user_query('admin')
    # return username == 'admin' and password == 'admin'
    if username == list_user[1] and password == list_user[2]:
        return True


@route('/main', method=['GET', 'POST'])
def main():
    # if user sends post data to start the grill, validate fields and
    # set status in temps database to 1, where grillcon is looking
    if request.POST.get('Start Grill Controller', '').strip():
        send_cook_name = request.POST.get('option_cook_name', '').strip()
        send_cook_target = request.POST.get('option_target_temp', '').strip()
        send_cook_finish = request.POST.get('option_finish_temp', '').strip()
        # send user inputs to validate function
        validate_input(send_cook_name, send_cook_target, send_cook_finish)
        time.sleep(7.0)
        redirect('/main')

    if request.POST.get('Modify Current Cook', '').strip():
        send_cook_target = request.POST.get('option_target_temp', '').strip()
        send_cook_finish = request.POST.get('option_finish_temp', '').strip()
        # send to validate data function
        validate_input_modify(send_cook_target, send_cook_finish)
        time.sleep(5.0)
        redirect('/main')

    # if receive option off, create tuple with None and 0 turning off the controller
    if request.POST.get('option_off', '').strip():
        tuple_send_cook = (None, None, None, 0)
        SQLQueries().write_input(tuple_send_cook)
        print "Option Off Received!!"
        return template(grillcon_off_template, get_url=url)

    # if notesSubmit, update the notes table for the current cook
    if request.forms.get('notesSubmit'):
        print 'notes received'

        new_notes = request.POST.get("notes", '').strip()

        SQLQueries().update_notes(new_notes)
        redirect('/main')

    else:
        # call last row results into a dictionary
        dict_variables_template = SQLQueries.variables_last_row_results()
        # if 'status' == 1 the grill controller is on
        if dict_variables_template["status"] == 1:
            # populate the dictionary to create the web page showing the controller as on
            dict_variables_row = dict_variables_template
            # get last row cook name
            dict_temps_row = SQLQueries.dict_temps_last_row_results()
            last_cook_name = dict_temps_row["name"]
            # get records for last row cook name
            cook_row_result = SQLQueries.cook_rows(last_cook_name)
            # make chart for last row cook name
            cook_graph = chart_list(cook_row_result)
            # get notes for the last cook
            cook_notes = SQLQueries.cook_notes(last_cook_name)

            return template(grillcon_on_template, get_url=url, rows=cook_graph,
                            dict_variables_row=dict_variables_row, dict_temps_row=dict_temps_row, cook_notes=cook_notes)

        else:
            # print "file path is %s /n template path is %s /n complete file is %s" %
            # (path, grillcon_off_template, template_path)
            return template(grillcon_off_template, get_url=url)


@route('/history', method=['GET', 'POST'])
def history():
    if request.forms.get('historyName'):
        # postdata = request.body.read()
        # show data received from client for debugging purposes
        # print postdata
        # graph value equals the user input selecting a cook name to populate a graph
        graph_value = request.forms.get('historyName')
        # get records for the last cook name
        cook_row_result = SQLQueries().cook_rows(graph_value)
        # make chart for last cook name
        cook_graph = chart_list(cook_row_result)
        cook_list = SQLQueries().cook_history()
        cook_notes = SQLQueries.cook_notes(graph_value)

        return template(grillcon_history_template, get_url=url, rows=cook_graph, list=cook_list,
                        cook_notes=cook_notes, graph_value=graph_value)

    # if notesSubmit, update the notes table for the specified cook
    if request.forms.get('notesSubmit'):
        # print 'history notes received'
        cook_name = request.POST.get("hidden", '').strip()
        new_notes = request.POST.get("notes", '').strip()
        # print 'new_notes are %s' % (new_notes)
        # print "the notes cook name is %s" % (cook_name)
        SQLQueries().update_notes(new_notes, cook_name)

        # redundant with above, possible method?

        graph_value = cook_name
        # get records for the last cook name
        cook_row_result = SQLQueries().cook_rows(graph_value)
        # make chart for last cook name
        cook_graph = chart_list(cook_row_result)
        cook_list = SQLQueries().cook_history()
        cook_notes = SQLQueries.cook_notes(graph_value)

        return template(grillcon_history_template, get_url=url, rows=cook_graph, list=cook_list,
                        cook_notes=cook_notes, graph_value=graph_value)

    else:

        dict_temps_row = SQLQueries.dict_temps_last_row_results()
        # print SQLQueries.temps_last_row_results()
        # get last row cook name
        last_cook_name = dict_temps_row["name"]
        # get records for the last cook name
        cook_row_result = SQLQueries.cook_rows(last_cook_name)
        # make chart for last cook name
        cook_graph = chart_list(cook_row_result)
        cook_list = SQLQueries().cook_history()
        cook_notes = SQLQueries.cook_notes(last_cook_name)

        return template(grillcon_history_template, get_url=url, rows=cook_graph, list=cook_list,
                        cook_notes=cook_notes, graph_value=last_cook_name)



@route('/admin')
@auth_basic(auth_check)
def admin():
    # print 'authorized request received',
    # print request.auth
    # print 'remote_address', request.remote_addr
    # my_config_settings = ConfigSettings()
    dict_settings = my_config_settings.get_settings_dict()
    list_user = SQLQueries().user_query('admin')

    # to keep the list in order, get_settings_lists returns 2 lists, key and value
    # they are combined to make a OrderedDict dictionary
    list_a, list_b = my_config_settings.get_settings_lists()
    list_settings = collections.OrderedDict(zip(list_a, list_b))

    # cipher_instance = cipher_functions.CipherFunctions(key_file)
    # print "Plaintext password is %s" % cipher_instance.decode(dict_settings['email_password'])

    return template(grillcon_admin_template,
                    cook_list=SQLQueries().cook_history(),
                    dict_settings=dict_settings,
                    list_settings=list_settings,
                    get_url=url,
                    list_user=list_user,
                    )



@route('/admin', method='POST')
def admin():
    # postdata = request.body.read()
    # print postdata  # this goes to log file only, not to client

    if request.forms.get('settingsSubmit'):
        print "settings info received"
        dict_new_settings = ({
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
        cipher_instance = cipher_functions.CipherFunctions(key_file)
        dict_new_settings["email_password"] = \
            cipher_instance.encode(dict_new_settings["email_password"])
        ConfigSettings.update_settings_file(dict_new_settings)

    if request.forms.get('backupSubmit'):
        # print 'backup request received'
        SQLQueries.sqlite3_backup()

    if request.forms.get('historyName'):
        # print 'history delete request received'
        value = request.POST.get('historyName')
        SQLQueries().delete_cook(value)

    if request.forms.get('userSubmit'):
        # print 'user request received'
        # dict_new_users = ({
        # "role" : request.POST.get("user_role", '').strip(),
        # "username" : request.POST.get("user_username", '').strip(),
        # "password" : request.POST.get("user_password", '').strip(),
        # })
        tuple_new_users = (
            request.POST.get("user_username", '').strip(),
            request.POST.get("user_password", '').strip(),
            request.POST.get("user_role", '').strip(),
        )

        SQLQueries().update_user(tuple_new_users)

    if request.POST.get('testMail', '').strip():
        print 'test_mail received'
        try:
            dict_settings = my_config_settings.get_settings_dict()
            login_name = dict_settings['email_address']
            cipher_instance = cipher_functions.CipherFunctions(key_file)
            login_pass = cipher_instance.decode(dict_settings['email_password'])
            send_to = dict_settings['send_to']
            send_subject = 'test from grillcon'
            send_text = 'test sent at %s ' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            sendAlert(login_name, login_pass, send_to, send_subject, send_text)
        except Exception:
            return "a testmail error occurred"

    redirect('/admin')


@route('/json')
def jsontest():
    return template('json')


@route('/getupdate.json')
def json_getupdates():
    # postdata = request.body.read()
    # print postdata  # this goes to log file only, not to client
    temps_timestamp, temps_grill_temp, temps_meat_temp, temps_fan = SQLQueries.temps_last_row_results()

    items = {"0": temps_grill_temp, "1": temps_meat_temp, "2": temps_fan, "3": temps_timestamp}
    # print items["1"]
    return items


@route('/favicon.ico', method='GET')
def get_favicon():
    return static_file('favicon.ico', root='/static/')
    # return grillcon_icon_file


@route('/')
# @view('index')
def index():
    redirect('/main')
# return { 'get_url': get_url }


@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')


@error(403)
def mistake403():
    return 'There is a mistake in your url! - Chris'


@error(404)
def mistake404():
    return 'Sorry, this page does not exist! - Chris'


debug(True)
# run(reloader=True)
# remember to remove reloader=True and debug(True) when you move your application
run(port=8080, host='0.0.0.0', reloader=True)
