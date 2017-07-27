from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Store, Product, User
from flask import session as login_session
from functools import wraps
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, flash
import requests


# Set environment variables
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Product Catalog"


# Connect to Database and create database session
engine = create_engine('sqlite:///products.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('login')
        return f(*args, **kwargs)
    return decorated_function


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Set up Google Login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already\
                                             connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 200px; height: 200px;border-radius: 150px;\
              -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Store & Product Information
@app.route('/store/<int:store_id>/JSON')
def storeJSON(store_id):
    items = session.query(Product).filter_by(
        store_id=store_id).all()
    return jsonify(Products=[i.serialize for i in items])


@app.route('/store/<int:store_id>/product/<int:product_id>/JSON')
def productJSON(store_id, product_id):
    product = session.query(Product).filter_by(id=product_id).one()
    return jsonify(Product=product.serialize)


@app.route('/store/JSON')
def storesJSON():
    stores = session.query(Store).all()
    return jsonify(stores=[r.serialize for r in stores])


# ROUTES
# Show all stores
@app.route('/')
@app.route('/store/')
def showStores():
    stores = session.query(Store).order_by(asc(Store.name))
    if 'username' not in login_session:
        return render_template('publicstores.html', stores=stores)
    else:
        return render_template('stores.html', stores=stores)


# Create a new store
@app.route('/store/new/', methods=['GET', 'POST'])
def newStore():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newStore = Store(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newStore)
        flash('New Store %s Successfully Created' % newStore.name)
        session.commit()
        return redirect(url_for('showStores'))
    else:
        return render_template('newStore.html')


# Edit a store
@app.route('/store/<int:store_id>/edit/', methods=['GET', 'POST'])
def editStore(store_id):
    editedStore = session.query(
        Store).filter_by(id=store_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedStore.user_id != login_session['user_id']:
        return '''<script>function myFunction() {alert('You are not authorized
         to edit this store. Please create your own store in order to edit.');}
         </script><body onload='myFunction()''>'''
    if request.method == 'POST':
        if request.form['name']:
            editedStore.name = request.form['name']
            flash('Store Successfully Edited %s' % editedStore.name)
            return redirect(url_for('showStores'))
    else:
        return render_template('editStore.html', store=editedStore)


# Delete a store
@app.route('/store/<int:store_id>/delete/', methods=['GET', 'POST'])
def deleteStore(store_id):
    storeToDelete = session.query(
        Store).filter_by(id=store_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if storeToDelete.user_id != login_session['user_id']:
        return '''<script>function myFunction() {alert('You are not authorized
         to delete this store. Please create your own store in order to delete.
         ');}</script><body onload='myFunction()''>'''
    if request.method == 'POST':
        session.delete(storeToDelete)
        flash('%s Successfully Deleted' % storeToDelete.name)
        session.commit()
        return redirect(url_for('showStores', store_id=store_id))
    else:
        return render_template('deleteStore.html', store=storeToDelete)


# Show a store's products
@app.route('/store/<int:store_id>/')
@app.route('/store/<int:store_id>/product/')
def showProduct(store_id):
    store = session.query(Store).filter_by(id=store_id).one()
    creator = getUserInfo(store.user_id)
    items = session.query(Product).filter_by(
        store_id=store_id).all()
    if 'username' not in login_session or creator.id != login_session[
            'user_id']:
        return render_template('publicproduct.html',
                               items=items, store=store, creator=creator)
    else:
        return render_template('product.html',
                               items=items, store=store, creator=creator)


# Create a new product item
@app.route('/store/<int:store_id>/product/new/', methods=['GET', 'POST'])
def newProduct(store_id):
    if 'username' not in login_session:
        return redirect('/login')
    store = session.query(Store).filter_by(id=store_id).one()
    if login_session['user_id'] != store.user_id:
        return '''<script>function myFunction() {alert('You are not authorized
         to add product items to this store. Please create your own store in
          order to add items.');}</script><body onload='myFunction()''>'''
    if request.method == 'POST':
            newItem = Product(name=request.form['name'],
                              description=request.form['description'],
                              price=request.form['price'],
                              size=request.form['size'],
                              category=request.form['category'],
                              store_id=store_id, user_id=store.user_id)
            session.add(newItem)
            session.commit()
            flash('New Product %s Successfully Created' % (newItem.name))
            return redirect(url_for('showProduct', store_id=store_id))
    else:
        return render_template('newproduct.html', store_id=store_id)


# Edit a product item
@app.route('/store/<int:store_id>/product/<int:product_id>/edit',
           methods=['GET', 'POST'])
def editProduct(store_id, product_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Product).filter_by(id=product_id).one()
    store = session.query(Store).filter_by(id=store_id).one()
    if login_session['user_id'] != store.user_id:
        return '''<script>function myFunction() {alert('You are not authorized
         to edit product items to this store. Please create your own store in
          order to edit items.');}</script><body onload='myFunction()''>'''
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['size']:
            editedItem.size = request.form['size']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['category']:
            editedItem.category = request.form['category']
        session.add(editedItem)
        session.commit()
        flash('Product Successfully Edited')
        return redirect(url_for('showProduct', store_id=store_id))
    else:
        return render_template('editproduct.html', store_id=store_id,
                               product_id=product_id, item=editedItem)


# Delete a product item
@app.route('/store/<int:store_id>/product/<int:product_id>/delete',
           methods=['GET', 'POST'])
def deleteProduct(store_id, product_id):
    if 'username' not in login_session:
        return redirect('/login')
    store = session.query(Store).filter_by(id=store_id).one()
    itemToDelete = session.query(Product).filter_by(id=product_id).one()
    if login_session['user_id'] != store.user_id:
        return '''<script>function myFunction() {alert('You are not authorized
         to delete product items to this store. Please create your own store in
          order to delete items.');}</script><body onload='myFunction()''>'''
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Product Successfully Deleted')
        return redirect(url_for('showProduct', store_id=store_id))
    else:
        return render_template('deleteproduct.html', item=itemToDelete)


# Disconnect user from Google login
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showStores'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showStores'))


# Main namespace
if __name__ == '__main__':
    app.secret_key = 'dev_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
