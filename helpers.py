import os
import sqlite3
from flask import redirect, render_template, request, session
from functools import wraps
# from dbconnect import DataBaseConnect

# Helper functions ==========================================

# Converts SQL query into list of dictionary values
def db_extract(query):
    if query:
        num_cols = len(query.description)
        col_names = [query.description[i][0] for i in range(num_cols)]
        data_list = []

        for row in query.fetchall():
            rows = {}
            for i in range(num_cols):
                # current_key = 
                rows[col_names[i]] = row[col_names[i]]
            data_list.append(rows)

        return data_list

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Returns username from user_id value
def get_user(db, session_usr_id):
    # Get curent username
    if session['user_id']:
        db.execute("SELECT username FROM users WHERE id=%s", (session_usr_id,))
        user = db.fetchone()['username']

        return user
    # If no userid, s user out
    else:
        return logout(); 
 
# Returns category id (cat_id) value from the category name value
def get_cat_id(category, db):
    catId = None
    try:
        db.execute("SELECT catid FROM categories WHERE category=%(category)s", {'category': category})
        catId = db.fetchone()['catid']
        return catId
    except Exception as e:
        print(e)
        return catId

def item_query(itemId, db):
    item_data = None
    # Check that item_id does contain only digits
    if str.isdigit(str(itemId)):
        try:
            # db.execute("SELECT * FROM store WHERE itemid=%(itemid)s", {'itemid': itemId})
            db.execute("SELECT item, itemid, location, comments, userid, store.catid, category FROM store INNER JOIN categories on categories.catid=store.catid WHERE itemid=%(itemid)s", {'itemid': itemId})
              # Collect data and insert into a list of dicts
            item_data = db_extract(db)

            return item_data

        except Exception as e:
            print(e)
            return item_data
    else:
        return item_data

# Function returns all items in a specific category belonging to current user
def category_query(db, catid, session_usr_id):
    try:
        db.execute("SELECT * FROM store WHERE userid=%(userid)s AND catid=%(catid)s", \
            {'userid': session_usr_id, 'catid': catid})

        cat_data = db_extract(db)

        return cat_data

    except Exception as e:
        print(e)
        return 'False'

