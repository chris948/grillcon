#!/usr/bin/env python

import os

import sys

import sqlite3

import time

import datetime

import ConfigParser

import collections

# class of methods to access the sql database

class SQLHelpers:
    def __init__(self):
        pass

    # method for sending sql query and not returning anything
    @staticmethod
    def execute(database_location, sql, parameters=None):
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
    def query(database_location, sql, parameters=None):
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
    def large_query(database_location, sql, array_size=200):
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
    def query_one(database_location, sql, parameters=None):
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
    def query_scalar(database_location, sql, parameters=None):
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
    def query_text(database_location, sql, parameters=None):
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

    # convert rows from database into a list
    @staticmethod
    def chart_list(rows):
        chart_table = ""

        for row in rows[:-1]:
            rowstr = "['{0}', {1}, {2}],\n".format(str(row[0]), str(row[1]), str(row[2]))
            chart_table += rowstr

        row = rows[-1]
        rowstr = "['{0}', {1}, {2}],\n".format(str(row[0]), str(row[1]), str(row[2]))
        chart_table += rowstr

        return chart_table
