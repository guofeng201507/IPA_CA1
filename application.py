# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 20:47:18 2017
@author: gf_admin
"""
import datetime
import sqlite3
from uuid import uuid4

from flask import Flask, request, g, jsonify

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=()):
    cur = get_db().cursor()
    cur.execute(query, args)

    rv = cur.fetchall()  # Retrive all rows
    cur.close()
    return rv
    # return (rv[0] if rv else None) if one else rv


def update_db(query, args=(), one=False):
    conn = get_db()
    conn.execute(query, args)
    conn.commit()
    conn.close()
    return "DB updated"


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")  # take note of this decorator syntax, it's a common pattern
def home():
    return "API is up and running..."


@app.route('/update_case', methods=['GET', 'POST'])
def raise_case():
    country = request.args.get('country')
    confirmed_no = request.args.get('confirmed_no')
    icu_no = request.args.get('icu_no')
    death_no = request.args.get('death_no')

    time_stamp = str(datetime.datetime.now())
    # case_id = int(time.mktime(rpt_time.timetuple()))

    tmp_list = [country, confirmed_no, icu_no, death_no, time_stamp]

    update_db("INSERT INTO TB_CASE (COUNTRY, CONFIRMED_NO, ICU_NO, DEATH_NO, TIME_STAMP) VALUES (?,?,?,?,?);",
              tmp_list)

    return "Cases updated with time stamp as " + time_stamp


@app.route('/query_case', methods=['GET', 'POST'])
def search_case():
    search_country = request.args.get('country')

    tmp_list = [search_country]

    rows = query_db("SELECT * from TB_CASE WHERE COUNTRY = ?", tmp_list)

    return jsonify(rows)


@app.route('/init', methods=['POST'])
def init_db():
    sql_create_table = """ CREATE TABLE IF NOT EXISTS TB_CASE (
                                          COUNTRY text NOT NULL,
                                          CONFIRMED_NO integer NOT NULL,
                                          ICU_NO integer NOT NULL,
                                          DEATH_NO integer NOT NULL,
                                          TIME_STAMP text NOT NULL
                                      ); """

    update_db(sql_create_table)
    return "DB created!"


if __name__ == '__main__':
    DATABASE = "./db/demo.db"

    # Generate a globally unique address for this node
    node_identifier = str(uuid4()).replace('-', '')

    print(node_identifier)
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port, debug=True)
