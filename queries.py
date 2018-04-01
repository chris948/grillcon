#!/usr/bin/env python

from sqlhelpers import SQLHelpers


class SQLQueries():

    # method to return the last row in the variables database
    @staticmethod
    def variables_last_row_results(database_location):

        last_row_query = "select cook_name, target_temp, finish_temp, ifnull(status, 0) " \
                         "from variables ORDER BY rowid DESC LIMIT 1;"
        row = SQLHelpers.query_one(database_location, last_row_query)
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
    def temps_last_row_results(database_location):

        last_row_query = "SELECT * FROM temps WHERE cook_name IS NOT NULL ORDER BY rowid DESC limit 1;"
        row = SQLHelpers.query_one(database_location, last_row_query)

        temps_timestamp = str(row[0])
        temps_grill_temp = str(row[1])
        temps_meat_temp = str(row[2])
        temps_fan = str(row[4])

        return temps_timestamp, temps_grill_temp, temps_meat_temp, temps_fan

    # method to return a dictionary of the last row in the temps database
    @staticmethod
    def dict_temps_last_row_results(database_location):

        last_row_query = "SELECT * FROM temps WHERE cook_name IS NOT NULL ORDER BY rowid DESC limit 1;"
        row = SQLHelpers.query_one(database_location, last_row_query)

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
    def cook_rows(database_location, cook_name):

        if cook_name != "":
            cook_name = (cook_name,)
            cook_name_query = "SELECT * FROM temps WHERE cook_name = ?"

            for result in SQLHelpers.query(database_location, cook_name_query, cook_name):
                return result
                # print "returning %s" % (result)

        else:
            # return rows([datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0, 0])
            pass

    # method to select a list of previous cooks
    @staticmethod
    def cook_history(database_location):

        list_history = []
        cook_history_query = "SELECT DISTINCT cook_name FROM temps ORDER BY timestamp DESC;"

        for result in SQLHelpers.query_text(database_location, cook_history_query):
            list_history.append(str(result[0]))

        return list_history

    # method to return the notes given a cook name
    @staticmethod
    def cook_notes(database_location, cook_name):
        cook_name = (cook_name,)
        cook_name_query = "SELECT cook_notes FROM notes WHERE cook_name = ?"
        result = str(SQLHelpers.query_scalar(database_location, cook_name_query, cook_name))
        return result

    # method to return the specified role in users table
    @staticmethod
    def user_query(database_location, role):
        # type: (object) -> object
        role = (role,)
        user_query = "SELECT * FROM users WHERE role = ?"

        row = SQLHelpers.query_one(database_location, user_query, role)
        # for row in all_rows:
        role = row[0]
        username = row[1]
        password = row[2]
        list_user = [role, username, password]
        return list_user

    # method to update the user row in users table
    @staticmethod
    def update_user(database_location, tuple_update_user):

        update_user_query = "UPDATE users SET username=?, password=? WHERE role=?"
        # tuple_update_user = (user_row["username"], user_row["password"], user_row["role"])
        SQLHelpers.execute(database_location, update_user_query, tuple_update_user)
        print "SQL database updated with role %s, user %s, password %s" % \
              (tuple_update_user[2], tuple_update_user[0], tuple_update_user[1])

    # method to delete all rows of specified cook name
    @staticmethod
    def delete_cook(database_location, cook_name):

        delete_cook_query = "DELETE FROM temps WHERE cook_name=?"
        tuple_cook_name = (cook_name,)
        SQLHelpers.execute(database_location, delete_cook_query, tuple_cook_name)
        print "deleted the %s cook" % tuple_cook_name

    # method to write cook variables into the database
    @staticmethod
    def write_input(database_location, tuple_send_cook):

        write_input_query = "INSERT INTO variables(cook_name, target_temp, finish_temp, status) VALUES(?,?,?,?)"
        SQLHelpers.execute(database_location, write_input_query, tuple_send_cook)

    # method to update the notes table
    @staticmethod
    def update_notes(database_location, new_note, cook_name=None):

        if cook_name is None:
            # call last row of database, use name column result
            dict_variables_template = SQLQueries.variables_last_row_results(database_location)
            cook_name = dict_variables_template["name"]

        tuple_cook_name = (cook_name,)
        select_name_query = "SELECT cook_notes FROM notes WHERE cook_name = ?"
        my_result = SQLHelpers.query_one(database_location, select_name_query, tuple_cook_name)
        print (my_result)
        if my_result is None:
            print "None"
            tuple_new_note = (cook_name, new_note,)
            select_name_query = "INSERT INTO notes(cook_name, cook_notes) VALUES(?,?)"
            SQLHelpers.execute(database_location, select_name_query, tuple_new_note)
        else:
            print "not None"
            tuple_new_note = (new_note, cook_name,)
            update_notes_query = "UPDATE notes SET cook_notes=? WHERE cook_name=?"
            SQLHelpers.execute(database_location, update_notes_query, tuple_new_note)
        print "SQL database updated with note %s, table %s" % (tuple_new_note[0], tuple_new_note[1])

    # Create timestamped database copy
    @staticmethod
    def sqlite3_backup(database_location):
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