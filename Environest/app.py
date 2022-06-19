from flask import *
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask("angelhacks")
app.config['MONGO_URI'] = "mongodb://localhost:27017/angelhacks"
app.config['SECRET_KEY'] = "banana"

Bootstrap(app)

mongo = PyMongo(app)

@app.route('/',methods=['GET'])
def join():
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        doc = {}
        for item in request.form:
            doc[item] = request.form[item]
        mongo.db.users.insert_one(doc)
        flash('Account created successfully')
        return redirect('/login')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        doc = {'login-email': request.form['email'], 'login-password': request.form['password']}

        found = mongo.db.users.find_one(doc)
        print(found)
        if found is None:
            flash('The email and password you entered did not match out records. Please double-check and try again')
            return redirect('/login')
        else:
            session['user-info'] = {'firstName': found['first-name'], 'lastName': found['last-name'], 'email': found['login-email']}
            return redirect('/home')

@app.route('/home',methods=['GET'])
def home():
    if 'user-info' in session:
        return render_template('home.html')
    else:
        flash('You need to login first')
        return redirect('/login')

@app.route('/notes',methods=['GET','POST'])
def note_saver():
    if request.method == 'GET':
        documents = mongo.db.NoteCollection.find()
        return render_template('home.html', savedNotes=documents)
    elif request.method == 'POST':
        document = {}
        for item in request.form:
            document[item] = request.form[item]
        mongo.db.NoteCollection.insert_one(document)
        return redirect('/notes')

@app.route('/add',methods=['GET','POST'])
def food_adder():
    if request.method == 'GET':
        return render_template('add.html')
    elif request.method == 'POST':
        doc = {}
        for item in request.form:
            doc[item] = request.form[item]
        mongo.db.foods.insert_one(doc)
        return redirect('/home')

@app.route('/lookup',methods=['GET','POST'])
def food_selector():
    if request.method == 'GET':
        session['calories'] = {}
        found_foods = mongo.db.foods.find()
        return render_template('lookup.html', food=found_foods)

    elif request.method == 'POST':
        doc = {}
        for item in request.form:
            if int(request.form[item]) != 0:
                doc[item] = request.form[item]
        session['calories'] = doc
        return redirect('/addcalories')

@app.route('/add_exercises',methods=['GET','POST'])
def exercise_adder():
    if request.method == 'GET':
        return render_template('exerciseadd.html')
    elif request.method == 'POST':
        doc = {}
        for item in request.form:
            doc[item] = request.form[item]
        mongo.db.exercises.insert_one(doc)
        return redirect('/home')

@app.route('/lookup_exercises',methods=['GET','POST'])
def exercise_selector():
    if request.method == 'GET':
        session['burn'] = {}
        found_exercises = mongo.db.exercises.find()
        return render_template('exerciselookup.html', exercises=found_exercises)

    elif request.method == 'POST':
        doc = {}
        for item in request.form:
            if int(request.form[item]) != 0:
                doc[item] = request.form[item]
        session['burn'] = doc
        return redirect('/removecalories')

@app.route('/removecalories', methods=['GET'])
def remove_calories():
    if request.method == 'GET':
        totals = 0

        calorie_items = []

        amount = session['burn']
        print(amount)

        for ID in amount:
            found_item = mongo.db.exercises.find_one({'_id': ObjectId(ID)})
            found_item['bought'] = amount[ID]
            print(found_item['calories-burned'])
            found_item['item-total'] = int(found_item['calories-burned']) * int(found_item['bought'])
            calorie_items.append(found_item)
            totals += found_item['item-total']
            print(totals)

        return render_template('home.html', exercises=calorie_items, totals=totals)

@app.route('/addcalories', methods=['GET'])
def add_calories():
    if request.method == 'GET':
        total = 0
        prev_total = 0

        calorie_items = []

        amount = session['calories']
        print(amount)

        for ID in amount:
            found_item = mongo.db.foods.find_one({'_id': ObjectId(ID)})
            found_item['bought'] = amount[ID]
            print(found_item['calorie'])
            found_item['item-total'] = int(found_item['calorie']) * int(found_item['bought'])
            calorie_items.append(found_item)
            total += found_item['item-total']
            print(total)

        return render_template('home.html', foods=calorie_items, total=total)

@app.route('/delete/<identity>')
def delete_contact(identity):
    found = mongo.db.NoteCollection.find_one({'_id': ObjectId(identity)})
    mongo.db.NoteCollection.remove(found)
    return redirect('/home')

@app.route('/view',methods=['GET','POST'])
def viewer():
    if request.method == 'GET':
        return render_template('view.html')

@app.route('/logout')
def logout():
    session.pop('user-info')
    return redirect('/login')

app.run(debug=True)

