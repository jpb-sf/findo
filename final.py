import os
import sys
from flask import Flask, request, session, url_for, flash, redirect, render_template, json, jsonify
from helpers import login_required, get_user, get_cat_id, item_query, category_query
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
app.config["SECRET_KEY"] = "bb8NfvRFyHRewqtF_UkOaA"

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
  
# sidebar = "<a> hello </a>\n" \
# + "<p> testing </p>"

# sidebar =   "<div>\n
#                 <div class="nav__sidebar--outerwrapper">
#                     <div class="nav__sidebar--innerwrapper"> 
#                         <ul>
#                             <a class="textdec__none" href="/category/household">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle household"></div>
#                                     <p class="color__3 btn__sidebar">Household</p>
#                                 </div>
#                             </a>
#                             <a class="textdec__none" href="/category/cooking">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle cooking"></div>
#                                     <p class="color__3 btn__sidebar">Cooking</p>
#                                 </div>
#                             </a>
#                             <a class="textdec__none" href="/category/hobbies">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle hobbies"></div>
#                                     <p class="color__3 btn__sidebar">Hobbies</p>
#                                 </div>
#                             </a>
#                             <a class="textdec__none" href="/category/electronics">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle electronics"></div>
#                                     <p class="color__3 btn__sidebar">Electronics</p>
#                                 </div>
#                             </a>
#                             <a class="textdec__none" href="/category/keepsakes">
#                             <a class="textdec__none" href="/category/holiday">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle holiday"></div>
#                                     <p class="color__3 btn__sidebar">Holiday</p>
#                                 </div>
#                             </a>
#                             <a class="textdec__none" href="/category/tools">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle tools"></div>
#                                     <p class="color__3 btn__sidebar">Tools</p>
#                                 </div>
#                             </a>
#                             <a class="textdec__none" href="/category/paperwork">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle paperwork"></div>
#                                     <p class="color__3 btn__sidebar">Paperwork</p>
#                                 </div>
#                             </a>
#                             <a class="textdec__none" href="/category/yard">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle yard"></div>
#                                     <p class="color__3 btn__sidebar">Yard</p>
#                                 </div>
#                             </a>
#                             <a class="textdec__none" href="/category/clothing">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle clothing"></div>
#                                     <p class="color__3 btn__sidebar">Clothing</p>
#                                 </div>
#                             </a>
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle keepsakes"></div>
#                                     <p class="color__3 btn__sidebar">Keepsakes</p>
#                                 </div>
#                             </a>
#                             <a class="textdec__none" href="/category/work">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle work"></div>
#                                     <p class="color__3 btn__sidebar">Work</p>
#                                 </div>
#                             </a>
#                             <a class="textdec__none" href="/category/misc">
#                                 <div class="nav__sidebar--container bg__color--white">
#                                     <div class="nav__sidebar--circle misc"></div>
#                                     <p class="color__3 btn__sidebar">Misc</p>
#                                 </div>
#                             </a>
#                         </ul>
#                     </div>
#                 </div>
#             </div>






# View functions ==========================================

# Python decorator
@app.route("/home")
@app.route("/")
@login_required
def home():
    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    userid = session['user_id']
    print(userid)
    db.execute("SELECT username FROM users WHERE id=?", (userid,))
    get_user = db.fetchone()
    user = get_user[0] 
    # return render_template('layout.html')
    return render_template('index.html', user=user)

@app.route("/login", methods=['GET', 'POST'])
def login():

    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")

        # Ensure username was submitted
        if not request.form.get("username"):
            print(0)
            return render_template('sorry.html')

        # Ensure password was submitted
        elif not request.form.get("password"):
            print(1)
            return render_template('sorry.html')

        # Query database for username

        db.execute("SELECT * FROM users WHERE username=:username",
            #sqlite3 wants this bracket/ json format now (?)
        {"username": username})

        # Or fetchall option will it inside a list
        row = db.fetchone()
        
        rowDict = dict(zip([c[0] for c in db.description], row))

        # print(rowDict)

        # Check if their is not a username match in database,
        # and whether accompanying password checks
        if not username == rowDict["username"] or not check_password_hash(rowDict["hash"], request.form.get('password')):
            print(2)
            return render_template('sorry.html')


        session["user_id"] = rowDict["id"]

        # Redirect user to home page
        return render_template('index.html', user=username)
    
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return render_template('login.html')

@app.route("/check", methods=['GET'])
def check():

    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    #username
    try:

        # Get username
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
           
    except (KeyError):
        return jsonify({"query": "empty"})


@app.route("/register", methods=['GET', 'POST'])
def register():

    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    
    # Forget any user_id
    session.clear()
    
    # User reached route via POST 
    if request.method == "POST":

        # Backend validate form / check for errors
        error0 = "Sorry, there was an error registering."
        error1 = "Username must be 3 characters or more."
        error2 = "Password must be 3 characters or more."
        error3 = "Confirmation must match"

        if len(request.form.get('username')) < 3:
            return render_template('register.html',  error0=error0, error2=error1)

        if len(request.form.get('password')) < 3:
            return render_template('register.html', error0=error0, error1=error2)

        if not request.form.get('password') == request.form.get('confirmation'):
            return render_template('register.html',  error0=error0, error3=error3)

        # Backend regristration error prevention, if username already taken
        username = request.form.get('username')
        db.execute('SELECT * FROM users')

        # ===============
        # Oh wow. THIS IS FOR FETCHALL a list of dicts!
        numcols = len(db.description)
        colnames = [db.description[i][0] for i in range(numcols)]
        userData = []

        for row in db.fetchall():
            res = {}
            for i in range(numcols):
                res[colnames[i]] = row[i]
            userData.append(res)

        #===============   

        # Loop through all usernames, check against received username from /registration
        for users in userData:
            print(users['username'])
            if users['username'] == username:
                userNameError = "Sorry, username is already taken"
                return render_template('register.html', error1=userNameError)

        # If no errors, then generate hash password for user  
        hash = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)

        #================
        # ALT SYNTAX [not using]
        # db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
        #     {"username":request.form.get('username'), "hash": hash})
        #================

         # Add username and password to database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
            (request.form.get('username'), hash))

        conn.commit()

        # Auto-login when registered
        db.execute("SELECT id, username FROM users WHERE username = :username",
            {"username":request.form.get('username')})

        # Send username to homescreen greeting, AND store user_id in sessions list
        row = db.fetchone()
        rowDict = dict(zip([c[0] for c in db.description], row))
        session['user_id'] = rowDict['id']
        user = rowDict['username']

        return render_template('index.html', user=user)
    
    else:
        print("no query")
        return render_template('register.html')


@app.route("/add",methods=['GET', 'POST'])
@login_required
def add():

    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    
    user = get_user()

    if request.method == 'POST':

        userid = session['user_id']
        category = request.form.get('category')
        item = request.form.get('item')
        # description = request.form.get('description')
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

        # "Incorrect number of bindings supplied." The current statement uses 1, and there are 8 supplied
        # Learn another way to this. ? and tuple with a comma. Comma is a must even if only one
        # db.execute("SELECT catid FROM categories WHERE category=?", (category,))
        # get = db.fetchone()
        # catId = dict(zip([c[0] for c in db.description], get))
        
        catId = get_cat_id(category)

        db.execute("INSERT INTO store (item, location, comments, category, userid) \
         VALUES (?, ?, ?, ?, ?)", (item, location, comments, catId, userid))

        conn.commit()
        conn.close()
        catData = category_query(catId)

        return render_template('category.html', user=user, category=category, userData=catData, side='sidebar')

    else:

        return render_template('add.html', user=user, side='sidebar')


@app.route("/category/<value>", methods=['GET'])
@login_required
def category(value):
    global sidebar
    try:
        conn = sqlite3.connect('final.db')
        conn.row_factory = sqlite3.Row
        db = conn.cursor()

        user = get_user()

        userid = session['user_id']
        
        # Category is url parameter passed in from html id
        category = value

        # Get corresponding category id number
        db.execute("SELECT catid FROM categories WHERE catname=?", (category,))
        get = db.fetchone()
        catid = get[0]

        # ============ Old way ================
        # get_cat_id = dict(zip([c[0] for c in db.description], get))
        # catId = get_cat_id['catid']
        # =====================================
           
        # Get store table data where userid = userid AND category=category id number
        db.execute("SELECT * FROM store WHERE userid=:userid AND category=:category", \
            {"userid": userid, "category": catid})

        # Combine result into a list of dicts!
        numcols = len(db.description)
        colnames = [db.description[i][0] for i in range(numcols)]
        userData = []

        for row in db.fetchall():
            result = {}
            for i in range(numcols):
                result[colnames[i]] = row[i]
            userData.append(result)
        # print(userData)
        # Send data base results to 
        return render_template('category.html', userData=userData, category=category, user=user, side='sidebar')

    # If any errors direct user back to index page
    except Exception as e:
        print(e)
        return render_template('index.html')

# Function gather all user data that matched user's id and returns template displaying data
@app.route("/all", methods=['GET'])
@login_required
def all():
    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    user = get_user()
    userid = session['user_id']

    try:
        # Select all from store table where userid is current userid
        # db.execute("SELECT * FROM store WHERE userid=:userid", {'userid': userid})
        
        db.execute("SELECT item, itemid, description, location, comments, userid, catname, catid FROM store INNER JOIN categories on categories.catid=store.category WHERE userid=:userid", \
            {'userid': userid} )

        # Get column names to convert to dict key words
        numcols = len(db.description) #6
        colnames = [db.description[i][0] for i in range(numcols)]
        userData = []

        for row in db.fetchall():
            result = {}
            for i in range(numcols):
                result[colnames[i]] = row[i]
            # Append the new dict to userData list
            userData.append(result)

        print(userData)
        
        # sort a list of dictionaries by key name
        userData.sort(key=operator.itemgetter('catid'))

        return render_template('all.html', userData=userData, user=user,side='sidebar')

    except Exception as e:
        print(e)
        return render_template('index.html')



# Edit or delete entry function
@app.route("/modify", methods=['GET', 'POST'])
@login_required
def modify():
    conn = sqlite3.connect('final.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    try:
        user = get_user()
        userid = session['user_id']

        itemId = request.args.get('itemId')

        #If itemid argument can be converted to int
        if int(itemId):
            itemId = int(itemId)

        # # Check if itemid is valid number for database search
        # if isinstance(itemId, int):

            # Make sql query of item, and retrieve all data in its row
            itemData = item_query(itemId)
         
            # Does current user own selected entry (itemid)?      
            if userid == itemData[0]['userid'] and itemId == itemData[0]['itemid']:
            
                # If action is delete, delete entry
                if request.args.get('action') == "delete":
                    db.execute("DELETE FROM store WHERE itemid=:itemid", {'itemid': itemId})
                    conn.commit()
                    conn.close

                # If action is edit, return itemId to get request, where JS will route to /edit
                if request.args.get('action') == "edit":
                    # after item id number is verified to be owned by user, return to user
                    return str(itemId)
                
                # If the action is delete, return true, prompting document reload
                return "True"

        else:
            return "False"

    except Exception as e:
        print(e)
        return render_template('index.html')

# Function allows user to make edits to entries.
# Function receives id for item, and returns editable data in the html form

@app.route("/edit/<itemId>", methods=['GET'])
@login_required
def edit(itemId):

    try:
        conn = sqlite3.connect('final.db')
        conn.row_factory = sqlite3.Row
        db = conn.cursor()
        user = get_user()
        userId = session['user_id']
        itemId = itemId
        
        # Make sql query of item, and retrieve all data in its row
        itemData = item_query(itemId)
        
        catId = itemData[0]['category']

        # Get category name from catid
        db.execute("SELECT * FROM categories WHERE catid=:catId", {'catId': catId})

        for row in db.fetchall():
            category = row[1]

        # Does current user own selected entry (itemid)?      
        if userId == itemData[0]['userid'] and int(itemId) == itemData[0]['itemid']:
                # Return edit page with fields completed with previously entered info
                return render_template('/edit.html', user=user, userData=itemData, category=category, side="sidebar")

        else:
            return render_template('/index.html', user=user, category=category)
    
    # If any erros, render index page
    except Exception as e:
        print(e)
        return render_template('index.html')

# Function allows user to make edits to entries, but Post request only.
# Second step of process: receives form of the changes made, updates database
@app.route("/change", methods=['POST'])
@login_required
def change():
        
        try:
            conn = sqlite3.connect('final.db')
            conn.row_factory = sqlite3.Row
            db = conn.cursor()
            user = get_user()
    
            userId = session['user_id']
            # Receive post request
            receivedData=request.get_json()
            itemId = int(receivedData['itemId'])
       
            # Make sql query of item, and retrieve all data in its row
            itemData = item_query(itemId)

            # Does current user own selected entry (itemid)?      
            if userId == itemData[0]['userid'] and itemId == itemData[0]['itemid']:
        
                category = receivedData['category']
                print(category)
                # Call helper function
                catId = get_cat_id(category)
                print(catId)
                # description = receivedData['description']
                location = receivedData['location']
                comments = receivedData['comments']
        

                db.execute("UPDATE store SET category=:catId,location=:location, \
                comments=:comments WHERE itemid=:itemId", {'catId': catId,
                'location': location, 'comments': comments, 'itemId': itemId})
                
                conn.commit()
                conn.close()

            return "True"

        # If any errors, render index page
        except Exception as e:
            print(e)
            return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
