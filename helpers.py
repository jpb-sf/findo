import os
import sqlite3
from flask import redirect, render_template, request, session
from functools import wraps

# Helper functions ==========================================

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if session.get("user_id") is None:
			return redirect("/login")
		return f(*args, **kwargs)
	return decorated_function


def get_user():
    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    # Get curent username
    if session['user_id']:
        userid = session['user_id']
        db.execute("SELECT username FROM users WHERE id=?", (userid,))
        get_user = db.fetchone()
        user = get_user[0]

        return user

    # If no userid, log user out
    else:
        return logout(); 

# Helper function that retreives category id, when category name is supplied
def get_cat_id(category):
    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    # "Incorrect number of bindings supplied." The current statement uses 1, and there are 8 supplied
    # Learn another way to this. ? and tuple with a comma. Comma is a must even if only one

    db.execute("SELECT catid FROM categories WHERE catname=:category", {'category': category})
    get = db.fetchone()
    get_cat_id = dict(zip([c[0] for c in db.description], get))
    catId = int(get_cat_id['catid'])
    return catId

# Function returns list of data from a row from the Store table matching itemid
def item_query(itemId):
    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    try:
        db.execute("SELECT * FROM store WHERE itemid=:itemid", {'itemid': itemId})
          # Collect data and insert into a list of dicts
        numcols = len(db.description)
        colnames = [db.description[i][0] for i in range(numcols)]
        itemData = []

        for row in db.fetchall():
            result = {}
            for i in range(numcols):
                result[colnames[i]] = row[i]
            itemData.append(result)
        return itemData

    except Exception as e:
        print(e)
        return 'False'

# Function returns all items in a specific category belonging to current user
def category_query(catid):
    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    userId = session['user_id']

    try:
        db.execute("SELECT * FROM store WHERE userid=:userid AND category=:catid", \
            {'userid': userId, 'catid': catid})
        numcols = len(db.description)
        colnames = [db.description[i][0] for i in range(numcols)]
        catData = []

        for row in db.fetchall():
            result = {}
            for i in range(numcols):
                result[colnames[i]] = row[i]
            catData.append(result)
        return catData

    except Exception as e:
        print(e)
        return 'False'



            