import os
import sys
from flask import Flask, request, session, url_for, flash, redirect, render_template, json, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import json
import sqlite3
import time
from threading import Event
import operator

# Event from threadigg is for delays
exit = Event()

# Initiate app
app = Flask(__name__)

import config 
from helpers import login_required, get_cat_id, get_user, item_query, db_extract
from dbconnect import DataBaseConnect
from flask_mysqldb import MySQL

#===developmemt or production===#
# config_class = 'BaseConfig'
config_class = 'DevelopmentConfig'
#===============================#

# FLASK APP CONFIG VARIABLES
app.config.from_object('config.' + config_class)

# Initiate Flask app's connection to MySQL server
mysql = MySQL(app)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Handle any 404s
@app.errorhandler(404)
def internal_error(error):
    db = mysql.connection.cursor()

    if session.get('user_id'):
        if session['user_id']:
            user = get_user(db, session['user_id'])
            return render_template('sorry.html', user=user, message="Sorry, this page does not exist.")
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')

# Handle any 500s
@app.errorhandler(500)
def server_error(error):
    db = mysql.connection.cursor()

    if session['user_id']:
        user = get_user(db, session['user_id'])
        return render_template('sorry.html', user=user, message="Sorry, there was an error on our end.")
    else:
        return redirect('/login')


# View functions ==========================================

@app.route("/sorry")
@login_required
def sorry(message):

    db = mysql.connection.cursor()

    if session['user_id']:
        
        user = get_user(db, session['user_id'])
        return render_template('sorry.html', user=user, message=message)
    else:
        return render_template('login.html')


@app.route("/home")
@app.route("/")
@login_required
def home():

    db = mysql.connection.cursor()

    if session['user_id']:

        db.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
        # fetchone() returns a dictionary?
        # fetchall() returns a tuple of tuples with values only?
        user = db.fetchone()['username']

        return render_template('index.html', user=user)

    return render_template('login.html')

@app.route("/login", methods=['GET', 'POST'])
def login():

    db = mysql.connection.cursor()

    # Empty session
    session.clear()

    try:
        # User reached route via POST (username/pw credentials submitted)
        if request.method == "POST":

            username = request.form.get("username")

            # Ensure username was submitted
            if not request.form.get("username"):
                print(0)
                return render_template('login.html')

            # Ensure password was submitted
            elif not request.form.get("password"):
                print(1)
                return render_template('login.html')

            # Query database for username
            db.execute("SELECT * FROM users WHERE username = %(username)s",
            {"username": username})

            user_data = db_extract(db)

            if not username == user_data[0]['username'] or not check_password_hash(user_data[0]['hash'], request.form.get('password')):
                print(2)
                return render_template('sorry.html')

            session["user_id"] = user_data[0]['id']

            # Redirect user to home page
            return render_template('index.html', user=user_data[0]['username'])

        # Else, render login page
        else:
            return render_template('login.html')
    except Exception as e:
        print(e)
        return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/login')

@app.route("/check", methods=['GET'])
def check():

    db = mysql.connection.cursor()

    #Get username
    try:
        username = request.args.get('username')
        print(username)

        db.execute("SELECT username FROM users")
        users = db.fetchall()

        # If username is already in database
        for user in users:
            if user['username'] == username:
                return json.dumps(False)

        # If username is not in database
        if not username == None:
            return json.dumps(True)

    except Exception as e:
        print(e)
        return jsonify({"query": "empty"})


@app.route("/register", methods=['GET', 'POST'])
def register():

    db = mysql.connection.cursor()

    # Forget any user_id
    session.clear()

    # User reached route via POST 
    if request.method == "POST":

        # Backend validate form / check for errors
        error0 = "Sorry, there was an error registering."
        error1 = "Username must be 3 characters or more."
        error2 = "Password must be 3 characters or more."
        error3 = "Confirmation password doesn't match"

        if len(request.form.get('username')) < 3:
            return render_template('register.html',  error0=error0, error2=error1)

        if len(request.form.get('password')) < 3:
            return render_template('register.html', error0=error0, error1=error2)

        if not request.form.get('password') == request.form.get('confirmation'):
            return render_template('register.html',  error0=error0, error3=error3)

        # Query of user database
        username = request.form.get('username')
        db.execute('SELECT * FROM users')

        all_users = db_extract(db)

        # Loop through all usernames, check against received username from /registration
        
        for users in all_users:
            if users['username'] == username:
                userNameError = "Sorry, username is already taken"
                return render_template('register.html', error1=userNameError)

        # If no errors, then generate hash password for user
        hash = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)

        # Add username and password to database
        db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)",
            (request.form.get('username'), hash))

        mysql.connection.commit()

        # Select newly stored user information from user db
        db.execute("SELECT id, username FROM users WHERE username = %(username)s",
            {"username":request.form.get('username')})

        row = db.fetchone()
        #Apply MySQL generation user_id and set as session id. 
        session['user_id'] = row['id']
        user = row['username']
        # Generate index page with username value for jinja engine to insert into interface
        return render_template('index.html', user=user)

    else:
        return render_template('register.html')


@app.route("/add",methods=['GET', 'POST'])
@login_required
def add():
    db = mysql.connection.cursor()

    user = get_user(db, session['user_id'])

    if request.method == 'POST':

        category = request.form.get('category')
        item = request.form.get('item')
        location = request.form.get('location')
        comments = request.form.get('comments')

        #===================
        # Backend validate form / check for errors
        error0 = "Please enter a category."
        error1 = "Please enter an item."
        error2 = "Please enter a location."

        if category == None:
            return render_template('add.html', error0=error0)

        if item == "":
            return render_template('add.html', error1=error1)

        if location == "":
            return render_template('add.html', error2=error2)


        cat_id = get_cat_id(category, db)

        db.execute("INSERT INTO store (item, location, comments, catid, userid) \
         VALUES (%(item)s, %(location)s, %(comments)s, %(catid)s, %(userid)s)", \
          {'item': item, 'location': location, 'comments': comments, 'catid': cat_id, 'userid': session['user_id']})

        mysql.connection.commit()
        
        # Select all user's 'store' data from current category that user is adding to
        db.execute("SELECT * FROM store WHERE userid=%(userid)s AND catid=%(catid)s", \
            {'userid': session['user_id'], 'catid': cat_id})
        cat_data = db_extract(db)

        return render_template('category.html', user=user, category=category, userData=cat_data, side='sidebar')

    else:

        return render_template('add.html', user=user, side='sidebar')


@app.route("/category/<value>", methods=['GET'])
@login_required
def category(value):
    global sidebar
    
    db = mysql.connection.cursor()

    user = get_user(db, session['user_id'])
    userid = session['user_id']
    # Category is url parameter passed in from html id

    if not get_cat_id(value, db):
        return internal_error(404)
 
    try:
        category = value
        # Get corresponding category id number
        db.execute("SELECT catid FROM categories WHERE category=%(category)s", {'category': category})
        catid = db.fetchone()['catid']
  
        # Get store table data where userid = userid AND category=category id number
        db.execute("SELECT * FROM store WHERE userid=%(userid)s AND catid=%(catid)s", \
            {"userid": userid, "catid": catid})

        user_cat_data = db_extract(db)

        thelength = len(user_cat_data)

        # Send data base results to
        return render_template('category.html', userData=user_cat_data, listlength=thelength, category=category, user=user, side='sidebar')

    # If any errors direct user back to index page
    except Exception as e:
        print(e)
        return render_template('index.html')

# Function gather all user data that matched user's id and returns template displaying data
@app.route("/all", methods=['GET'])
@login_required
def all():
    db = mysql.connection.cursor()

    user = get_user(db, session['user_id'])
    userid = session['user_id']

    try:
        # Select all from s'tore' table and 'categories' table where userid is current userid
        db.execute("SELECT item, itemid, location, comments, userid, store.catid, category FROM store INNER JOIN categories on categories.catid=store.catid WHERE userid=%(userid)s", \
            {'userid': userid} )

        all_cat_data = db_extract(db)

        # sort a list of dictionaries by key name
        all_cat_data.sort(key=operator.itemgetter('catid'))

        return render_template('all.html', userData=all_cat_data, user=user, side='sidebar')

    except Exception as e:
        print(e)
        return render_template('index.html')



# Edit or delete entry function
@app.route("/modify", methods=['POST'])
@login_required
def modify():
    db = mysql.connection.cursor()
    
    try:
        user = get_user(db, session['user_id'])
        user_id = session['user_id']
        item_id = request.get_json()['itemId']

        print('item_id is')
        print(request.get_json()['itemId'])
        print(request.get_json()['action'])

        #If item_id argument can be converted to int
        if int(item_id):
            item_id = int(item_id)

        # # # Check if item_id is valid number for database search
        # if isinstance(item_id, int):
            
            # Make sql query of item, and retrieve all data in its row
            item_data = item_query(item_id, db)
         
            # Does current user own selected entry (item_id)?      
            if user_id == item_data[0]['userid'] and item_id == item_data[0]['itemid']:
            
                # If action is delete, delete entry
                if request.get_json()['action'] == "delete":
                    db.execute("DELETE FROM store WHERE itemid=%(itemid)s AND userid=%(userid)s" , {'itemid': item_id, 'userid': user_id})
                    mysql.connection.commit()

                # If action is edit, return itemId to get request, where JS will route to /edit
                elif request.get_json()['action'] == "edit":
                    # after item id number is verified to be owned by user, return to user
                    return str(item_id)
                
                # If the action is delete, return true, prompting document reload
                return "True"

        else:
            return "False"

    except Exception as e:
        print(e)
        return render_template('index.html')

# Function allows user to make edits to entries.
# Function receives id for item, and returns editable data in the html form

@app.route("/edit/<item_id>", methods=['GET'])
@login_required
def edit(item_id):
    
    db = mysql.connection.cursor()

    # if function returns None, value contains characters other than digits (manually entered in address bar)
    if item_query(item_id, db) is None:
        return internal_error(404)
    
    try:
        user = get_user(db, session['user_id'])
        user_id = session['user_id']
        
        # Make sql query of item, and retrieve all data in its row
        item_data = item_query(item_id, db)
        print('item_data is')
        print(item_data)

        # Does current user own selected entry (itemid)?      
        if user_id == item_data[0]['userid'] and int(item_id) == item_data[0]['itemid']:
                # Return edit page with fields completed with previously entered info
                return render_template('/edit.html', user=user, userData=item_data, side='sidebar')

        else: 
            return sorry(message='There was an error matching this item to your account.')
    
    # If any erros, render index page
    except Exception as e:
        print(e)
        return sorry(message='There was an error matching this item to your account.')

# Function allows user to make edits to entries, but Post request only.
# Second step of process: receives form of the changes made, updates database
@app.route("/change", methods=['POST'])
@login_required
def change():
        try:
            db = mysql.connection.cursor()

            user_id = session['user_id']
            # Receive post request
            print('hello')
            received_changes=request.get_json()
            print('received changes is ')
            print(received_changes)
            item_id = int(received_changes['itemId'])
       
            # Make sql query of item, and retrieve all data in its row
            item_data = item_query(item_id, db)

            # Does current user own selected entry (itemid)?      
            if user_id == item_data[0]['userid'] and item_id == item_data[0]['itemid']:
                
                # Get new, possibly updated category
                category = received_changes['category']
                # Call helper function
                cat_id = get_cat_id(category, db)
                # description = received_changes['description']
                location = received_changes['location']
                comments = received_changes['comments']
        
                db.execute("UPDATE store SET catid=%(catId)s,location=%(location)s, \
                comments=%(comments)s WHERE itemid=%(itemId)s AND userid = %(userid)s", {'itemId': item_id, 'userid': session['user_id'],\
                'catId': cat_id, 'location': location, 'comments': comments})

                mysql.connection.commit()
                
                return "True"
            else:
                return "False"

        # If any errors, render index page
        except Exception as e:
            print(e)
            return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
