import os
from datetime import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required,  floatify, check_float, compare_ingredients

# File handling based on :
# https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/

# Configure upload folder for the images
UPLOAD_FOLDER = '/static'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///foodtrack.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        taken = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure username is unique
        if taken:
            return apology("this username is already taken", 400)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 400)

        # Ensure password was submitted
        if len(password) < 8:
            return apology("password too short - minimum 8 symbols", 400)

        # Ensure password was confirmed
        if not confirmation:
            return apology("must provide password confirmation", 400)

        # Ensure password and confirmation is the same
        if password != confirmation:
            return apology("provided passwords do not match", 400)

        else:
            hashcode = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashcode)
            user = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
            session["user_id"] = user[0]["id"]
            flash("Registration successful!")
            return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    username = request.form.get("username")
    password = request.form.get("password")
    conifrmation = request.form.get("confirmation")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Flash login message
        flash("Logged in.")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    flash("Logged out")

    # Redirect user to login form
    return redirect("/")

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user's password."""
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("change_password.html")

    else:
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            return apology("passwords do not match")

        # Get a new password's hash and update db
        new_hash = generate_password_hash(password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, user_id)
        flash("Password changed successfully")
        return redirect("/")

@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
    """Homepage that shows your fridge"""
    user_id = session["user_id"]

    if request.method == "GET":
        # Get user's fridge content
        fridge_db = db.execute("SELECT ingredient_id, quantity FROM fridges WHERE user_id = ?", user_id)
        content_db = []
        for item in range(len(fridge_db)):
            content = db.execute("SELECT name, unit FROM ingredients WHERE id = ?", \
                                fridge_db[item]["ingredient_id"])[0]
            content["quantity"] = fridge_db[item]["quantity"]
            content_db.append(content)

        # Display user's fridge content
        return render_template("index.html", content_db=content_db, items=range(len(content_db)), fridge_db=fridge_db)
    else:
        # Get data which button was clicked on what ingredient
        button_clicked = request.form.get("button_clicked")[:3]
        ing_ID = request.form.get("button_clicked")[3:]
        if button_clicked == "mod":
            # Get and validate new quantity of ingredient
            quantity = request.form.get("quantity")
            if quantity is None:
                return apology("there was an error, try again")
            # quantity = floatify(quantity)
            if not check_float(quantity):
                return jsonify(quantity, check_float(quantity))
                return apology("quantity must be a number (eg.10 000.750)")
            # If all is good update fridges table
            db.execute("UPDATE fridges SET quantity = ? WHERE user_id = ? AND ingredient_id = ?", \
                       quantity, user_id, ing_ID)
            flash("Updated.")
            return redirect("/")
        elif button_clicked == "del":
            # Delete selected ingredient
            db.execute("DELETE FROM fridges WHERE user_id = ? AND ingredient_id = ?", user_id, ing_ID)
            flash("Deleted.")
            return redirect("/")
        else:
            return apology("something went wrong, try again")


@app.route("/add_ings", methods= ["GET", "POST"])
@login_required
def add_ings():
    """Add ingredients to fridge"""
    user_id = session["user_id"]
    if request.method == "GET":
        return render_template("add_ings.html")
    else:
        # Get data from form
        ingredients = request.form.getlist('ingredient[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        unit_options = ["pcs", "g", "kg", "l", "ml", "cm", "tsp", "tbsp", "cups"]
        items = range(len(ingredients))

        # Check for empty inputs
        for item in items:
            if ingredients[item] == "" or quantities[item] == 0:
                return apology("all ingredients must have names, quantities and units")
            # Check if quantity is a number
            quantities[item] = floatify(quantities[item])
            if not check_float(quantities[item]):
                return apology("quantity must be a number (eg.10 000.750")
            # Check if unit is selected from the list
            if units[item] not in unit_options :
                return apology("select unit from given options")

            # In ingredients table insert ingredient if it does not yet exist
            db.execute("INSERT OR IGNORE INTO ingredients (name, unit) VALUES (?,?)", ingredients[item], units[item])

            # Get ingredient's ID
            ing_id = db.execute("SELECT id FROM ingredients WHERE name = ? AND unit = ?", \
                                 ingredients[item], units[item])[0]["id"]

            # Check if ingredient is already in fridge
            check = db.execute("SELECT id FROM fridges WHERE user_id = ? AND ingredient_id = ?", \
                               user_id, ing_id)
            if not check:
                # Insert ingredient into user's fridge
                db.execute("INSERT INTO fridges (user_id, ingredient_id, quantity) VALUES (?, ?, ?)", \
                            user_id, ing_id, quantities[item])
                return redirect("/")
            else:
                # Get current ingredient's quantity in the user's fridge
                curr_quantity = db.execute("SELECT quantity FROM fridges WHERE user_id = ? AND ingredient_id = ?", \
                                           user_id, ing_id)[0]["quantity"]

                overall = float(curr_quantity) + float(quantities[item])
                # Update the fridge with the sum of the current and added quantity
                db.execute("UPDATE fridges SET quantity = ? WHERE user_id = ? AND ingredient_id = ?", \
                           overall, user_id, ing_id)
            return redirect("/")

@app.route("/recipes", methods = ["GET", "POST"])
@login_required
def recipes():
    """Show user's recipes, allow to create a new one."""
    user_id = session["user_id"]

    if request.method == "GET":
        # Get recipes info from db
        recipes_db = db.execute(
        "SELECT id, name, portions, tips, image, date_added FROM recipes WHERE user_id = ? ORDER BY date_added DESC"\
                 , user_id)

        # If no recipes found prompt to add one
        if not recipes_db:
            flash("No recipes found! Please add a recipe.")

        return render_template("recipes.html", recipes_db = recipes_db, items = range(len(recipes_db)))

    else:
        return render_template("add_recipe.html")


@app.route("/add_recipe", methods = ["GET", "POST"])
@login_required
def add_recipe():
    """Page for allowing users to add new recipes"""
    user_id = session["user_id"]
    if request.method == "GET":
        return render_template("add_recipe.html")
    else:
        # Verify uploaded recipe image
        f = request.files

        file = request.files['file']

        # If no image has been uploaded default to standard recipe img
        if file.filename == '':
            photo = "recipe.png"

        # If it has then verify the filename and upload the image
        else:
            if allowed_file(file.filename):
                photo = secure_filename(file.filename)
                file.save(photo)
            else:
                return apology("invalid file type")

        # METADATA
        recipe_title = request.form.get("recipe").title()
        portions = request.form.get("portions")
        tips = request.form.get("tips")


        # Check if there is a title and if the title isnt all digits
        if not recipe_title:
            return apology("enter recipe's title")

        if recipe_title.isnumeric():
            return apology("recipe's title cannot be all numbers")

        # Check if there already exist a recipe with the same title
        recipe_ID = db.execute("SELECT id FROM recipes WHERE name = ? AND user_id = ?", recipe_title, user_id)
        if recipe_ID :
            return apology("you already have a recipe with this title")

        if not portions:
            return apology("enter portions per recipe")
        else:
            portions = int(portions)

        if not tips :
            tips = "Combine all of the ingredients and you are done!"

        # INGREDIENTS
        # Get data from form
        ingredients = request.form.getlist('ingredient[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        unit_options = ["pcs", "g", "kg", "l", "ml", "cm", "tsp", "tbsp", "cups"]
        items = range(len(ingredients))


        recipe_date = datetime.now()


        # Check for empty inputs
        for item in items:
            if ingredients[item] == "" or quantities[item] == 0:
                return apology("all ingredients must have names, quantities and units")
            # Check if quantity is a number
            quantities[item] = floatify(quantities[item])
            if not check_float(quantities[item]):
                return apology("quantity must be a number (eg.10 000.750")
            # Check if unit is selected from the list
            if units[item] not in unit_options :
                return apology("select unit from given options")

        db.execute(
        # Insert recipe's metadata into db
            "INSERT INTO recipes (user_id, name, portions, tips, image, date_added) VALUES (?,?,?,?,?,?)", user_id,
            recipe_title, int(portions), tips, photo, recipe_date)

        # Get recipe's ID for inserting ingredients
        recipe_ID = db.execute("SELECT id FROM recipes WHERE name = ? AND user_id =?", recipe_title, user_id)[0]["id"]
        for item in items:
            # Insert into ingredients table except if that ingredient already exist in the table
            db.execute(
                "INSERT OR IGNORE INTO ingredients (name, unit) VALUES (?,?)", ingredients[item], units[item]
            )

            # Select now this ingredient ID for inserting into ing2rec
            ing_ID = db.execute(
                "SELECT id FROM ingredients WHERE name = ? AND unit = ?", ingredients[item], units[item]
                )[0]["id"]
            # return jsonify(ing_ID)

            # Insert ingredient data into ing2rec table
            db.execute(
                "INSERT INTO ing2rec (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)", recipe_ID, ing_ID, \
                    quantities[item])
        flash("Recipe added!")
        return redirect("/recipes")


@app.route("/view_recipe")
def view_recipe():
    """View selected recipe"""
    button_clicked = int(request.args.get("action"))
    # Get data of the chosen recipe

    # Recipe's metadata - ID of recipe based on which button was clicked
    recipe_db = db.execute(
        "SELECT name, portions, tips, image FROM recipes WHERE id = ?", button_clicked
        )
    # Get ingredients IDs and quantities from ing2rec
    ing_ID_db = db.execute(
        "SELECT ingredient_id, quantity FROM ing2rec WHERE recipe_id = ?", button_clicked
        )
    # Loop through all ingredients' IDs and get their info from ingredients table
    ing_db = []
    for item in range(len(ing_ID_db)):
        ing_info = db.execute("SELECT name, unit from ingredients WHERE id = ?", ing_ID_db[item]["ingredient_id"])[0]
        ing_info["quantity"] = ing_ID_db[item]["quantity"]
        ing_db.append(ing_info)

    # return jsonify(ing_db)
    return render_template("view_recipe.html", recipe_db=recipe_db, ing_db=ing_db, items=range(len(ing_db)))


@app.route("/delete_recipe")
def delete_recipe():
    """Delete selected recipe"""
    button_clicked = request.args.get("action")
    recipe_id = int(button_clicked[3:])

    # Delete recipe ingredients
    db.execute("DELETE FROM ing2rec WHERE recipe_id=?", recipe_id)
    # Delete recipe metadata
    db.execute("DELETE FROM recipes WHERE id=?", recipe_id)

    flash("Recipe deleted")

    return redirect("/recipes")


@app.route("/lists", methods=["GET", "POST"])
@login_required
def lists():
    """Page for viewing and editing user's shopping lists"""
    user_id = session["user_id"]

    if request.method == "GET":
        # Get recipes info from db
        shop_lists_db = db.execute(
            "SELECT id, name, date_added FROM shopping_lists WHERE user_id = ? ORDER BY date_added DESC", user_id)

        # If no recipes found prompt to add one
        if not shop_lists_db:
            flash("No shopping lists found! Create a new shopping list.")

        return render_template("lists.html", shop_lists_db = shop_lists_db, items = range(len(shop_lists_db)))

    else:
        return render_template("add_list.html")

@app.route("/add_list", methods=["GET", "POST"])
@login_required
def add_list():
    """Page for adding a new shopping lists"""
    if request.method == "GET":
        return render_template("add_list.html")
    else:
        user_id = session["user_id"]

        list_title = request.form.get("list").title()

        # Check if there is a title
        if not list_title:
            return apology("enter shopping list title")

        # Check if there already exist a list with the same title
        list_ID = db.execute("SELECT id FROM shopping_lists WHERE name = ? AND user_id = ?", list_title, user_id)
        if list_ID :
            return apology("you already have a shopping list with this title")

        # INGREDIENTS
        # Get data from table
        ingredients = request.form.getlist('ingredient[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        unit_options = ["pcs", "g", "kg", "l", "ml", "cm", "tsp", "tbsp", "cups"]
        items = range(len(ingredients))
        list_date = datetime.now()


    # Check for empty inputs
    for item in items:
        if ingredients[item] == "" or quantities[item] == 0:
            return apology("all ingredients must have names, quantities and units")
        # Check if quantity is a floating point number or intiger
        quantities[item] = floatify(quantities[item])
        if not check_float(quantities[item]):
            return apology("quantity must be a number (e.g. 10 000.525 )")
        # Check if unit is selected from the list
        if units[item] not in unit_options :
            return apology("select unit from given options")

    # Insert list's metadata into db
    db.execute(
        "INSERT INTO shopping_lists (user_id, name, date_added) VALUES (?,?,?)", user_id,
        list_title, list_date)

    # Get list's ID for inserting ingredients
    list_ID = db.execute("SELECT id FROM shopping_lists WHERE name = ? AND user_id =?", list_title, user_id)[0]["id"]
    # return jsonify(list_ID)
    for item in items:
            # Insert into ingredients table except if that ingredient already exist in the table
            db.execute(
                "INSERT OR IGNORE INTO ingredients (name, unit) VALUES (?,?)", ingredients[item], units[item]
            )

            # Select now this ingredient ID for inserting into ing2rec
            ing_ID = db.execute(
                "SELECT id FROM ingredients WHERE name = ? AND unit = ?", ingredients[item], units[item]
                )[0]["id"]

            # Insert ingredient data into ing2list table
            db.execute("INSERT INTO ing2list (list_id, ingredient_id, quantity) VALUES (?, ?, ?)", list_ID, ing_ID, quantities[item])

    return redirect("/lists")


@app.route("/view_list", methods=["GET", "POST"])
@login_required
def view_list():
    """Allows users to view lists content."""
    button_clicked = int(request.form.get("action"))

    # List's metadata - ID of recipe based on which button was clicked
    list_db = db.execute("SELECT name FROM shopping_lists WHERE id = ?", button_clicked)
    # Get ingredients IDs and quantities from ing2rec
    ing_ID_db = db.execute(
        "SELECT ingredient_id, quantity FROM ing2list WHERE list_id = ?", button_clicked
        )
    # Loop through all ingredients' IDs and get their info from ingredients table
    ing_db = []
    for item in range(len(ing_ID_db)):
        ing_info = db.execute("SELECT name, unit from ingredients WHERE id = ?", ing_ID_db[item]["ingredient_id"])[0]
        ing_info["quantity"] = ing_ID_db[item]["quantity"]
        ing_db.append(ing_info)

    # return jsonify(ing_db)
    return render_template("view_list.html", list_db=list_db, ing_db=ing_db, items=range(len(ing_db)))


@app.route("/delete_list", methods=["GET", "POST"])
@login_required
def delete_list():
    """Allows users to delete shopping lists."""
    button_clicked = request.args.get("action")
    list_id = int(button_clicked[3:])

    # Delete recipe ingredients
    db.execute("DELETE FROM ing2list WHERE list_id = ?", list_id)
    # Delete recipe metadata
    db.execute("DELETE FROM shopping_lists WHERE id = ?", list_id)

    flash("Shopping list deleted")

    return redirect("/lists")


@app.route("/modify_list", methods=["GET", "POST"])
@login_required
def modify_list():
    """Allows users to modify shopping lists content."""
    if request.method == "GET":
        list_id = int(request.args.get("action")[3:])

        # Recipe's metadata - ID of recipe based on which button was clicked
        list_db = db.execute("SELECT id, name FROM shopping_lists WHERE id = ?", list_id)

        # Get ingredients IDs and quantities from ing2rec
        ing_ID_db = db.execute(
            "SELECT ingredient_id, quantity FROM ing2list WHERE list_id = ?", list_id
            )
        # Loop through all ingredients' IDs and get their info from ingredients table
        ing_db = []
        for item in range(len(ing_ID_db)):
            ing_info = db.execute("SELECT name, unit from ingredients WHERE id = ?", \
                                  ing_ID_db[item]["ingredient_id"])[0]
            ing_info["quantity"] = ing_ID_db[item]["quantity"]
            ing_db.append(ing_info)

        return render_template("modify_list.html", list_db=list_db, ing_db=ing_db, items=range(len(ing_db)))

    # POST METHOD
    else:
        user_id = session["user_id"]

        list_title = request.form.get("list").title()

        # Check if there already exist a list with the same title
        list_ID = db.execute("SELECT id FROM shopping_lists WHERE name = ? AND user_id = ?", list_title, user_id)

        # INGREDIENTS
        # Get data from table
        ingredients = request.form.getlist('ingredient[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        unit_options = ["pcs", "g", "kg", "l", "ml", "cm", "tsp", "tbsp", "cups"]
        items = range(len(ingredients))
        list_date = datetime.now()


        # Check for empty inputs
        for item in items:
            if ingredients[item] == "" or quantities[item] == 0:
                return apology("all ingredients must have names, quantities and units")
            # Check if quantity is a floating point number or intiger
            quantities[item] = floatify(quantities[item])
            if not check_float(quantities[item]):
                return apology("quantity must be a number (e.g. 10 000.525 )")
            # Check if unit is selected from the list
            if units[item] not in unit_options :
                return apology("select unit from given options")
                # return jsonify(units[item])

        # Get list's ID
        list_ID = db.execute("SELECT id FROM shopping_lists WHERE name = ? AND user_id =?", list_title, \
                             user_id)[0]["id"]

        # Update list's metadata
        db.execute("UPDATE shopping_lists SET name = ?, date_added = ? WHERE id = ?", list_title, list_date, list_ID)

        for item in items:
                # Insert into ingredients table except if that ingredient already exists in the table
                db.execute("INSERT OR IGNORE INTO ingredients (name, unit) VALUES (?,?)", ingredients[item], \
                           units[item])

                # Select now this ingredient ID for inserting into ing2list
                ing_ID = db.execute(
                    "SELECT id FROM ingredients WHERE name = ? AND unit = ?", ingredients[item], units[item]
                    )[0]["id"]

                # Check if this ing is already in this list
                check_ID = db.execute("SELECT id FROM ing2list WHERE list_id = ? AND ingredient_id = ?", list_ID, \
                                      ing_ID)
                if not check_ID:
                    # Insert ingredient data into ing2list table
                    db.execute("INSERT INTO ing2list (list_id, ingredient_id, quantity) VALUES (?, ?, ?)", list_ID, \
                               ing_ID, quantities[item])
                else:
                    # If it exists - update it
                    db.execute("UPDATE ing2list SET quantity = ? WHERE id = ?", quantities[item], check_ID[0]["id"])

        return redirect("/lists")

@app.route("/rec2list", methods=["GET", "POST"])
@login_required
def rec2list():
    """Allows users to modify shopping lists content."""
    user_id = session["user_id"]
    now = datetime.now()
    if request.method == "GET":
        button_clicked = request.args.get("action")[4:]
        recipe_id = int(button_clicked)

        # Get recipe's name to insert as list name
        recipe_name = db.execute("SELECT name FROM recipes WHERE id = ?", recipe_id)[0]["name"]

        # Check if there is already a list with this name
        check = db.execute("SELECT id FROM shopping_lists WHERE name = ?", recipe_name)
        if check :
            return apology("You already have a shopping list with this name")


        # Create a new shopping list with the name of the recipe
        db.execute("INSERT INTO shopping_lists (user_id, name, date_added) VALUES (?,?,?)", user_id, recipe_name, now)

        # Get this ID now
        list_db = db.execute("SELECT id, name FROM shopping_lists WHERE name = ?", recipe_name)
        # Get ingredients IDs and quantities from ing2rec
        ing_ID_db = db.execute("SELECT ingredient_id, quantity FROM ing2rec WHERE recipe_id = ?", recipe_id)
        # Loop through all ingredients' IDs and get their info from ingredients table
        ing_db = []
        for item in range(len(ing_ID_db)):
            ing_info = db.execute("SELECT name, unit from ingredients WHERE id = ?", \
                                  ing_ID_db[item]["ingredient_id"])[0]
            ing_info["quantity"] = ing_ID_db[item]["quantity"]
            ing_db.append(ing_info)
        # return jsonify(list_db)

        return render_template("modify_list.html", list_db=list_db, ing_db=ing_db, items=range(len(ing_db)))

    # POST METHOD
    else:
        user_id = session["user_id"]
        list_title = request.form.get("list").title()

        # Check if there is a title
        if not list_title:
            return apology("enter shopping list title")

        # Check if there already exist a list with the same title
        list_ID = db.execute("SELECT id FROM shopping_lists WHERE name = ? AND user_id = ?", list_title, user_id)

        # INGREDIENTS
        # Get data from table
        ingredients = request.form.getlist('ingredient[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        unit_options = ["pcs", "g", "kg", "l", "ml", "cm", "tsp", "tbsp", "cups"]
        items = range(len(ingredients))
        list_date = datetime.now()


        # Check for empty inputs
        for item in items:
            if ingredients[item] == "" or quantities[item] == 0:
                return apology("all ingredients must have names, quantities and units")
            # Check if quantity is a floating point number or intiger
            quantities[item] = floatify(quantities[item])
            if not check_float(quantities[item]):
                return apology("quantity must be a number (e.g. 10 000.525 )")
            # Check if unit is selected from the list
            if units[item] not in unit_options :
                return apology("select unit from given options")
                # return jsonify(units[item])

        # Get list's ID
        list_ID = db.execute("SELECT id FROM shopping_lists WHERE name = ? AND user_id =?", list_title, \
                             user_id)[0]["id"]

        # Update list's metadata
        db.execute("UPDATE shopping_lists SET name = ?, date_added = ? WHERE id = ?", list_title, list_date, list_ID)

        for item in items:
                # Insert into ingredients table except if that ingredient already exists in the table
                db.execute("INSERT OR IGNORE INTO ingredients (name, unit) VALUES (?,?)", ingredients[item], \
                           units[item])

                # Select now this ingredient ID for inserting into ing2rec
                ing_ID = db.execute(
                    "SELECT id FROM ingredients WHERE name = ? AND unit = ?", ingredients[item], units[item]
                    )[0]["id"]

                # Check if this ing is already in this list
                check_ID = db.execute("SELECT id FROM ing2list WHERE list_id = ? AND ingredient_id = ?", list_ID, \
                                      ing_ID)[0]["id"]
                if not check_ID:
                    # Insert ingredient data into ing2list table
                    db.execute("INSERT INTO ing2list (list_id, ingredient_id, quantity) VALUES (?, ?, ?)", list_ID, \
                               ing_ID, quantities[item])
                else:
                    # If it exists - update it
                    db.execute("UPDATE ing2list SET quantity = ? WHERE id = ?", quantities[item], check_ID)

        return redirect("/lists")


@app.route("/add2fridge", methods=["GET", "POST"])
@login_required
def add2fridge():
    """Add ingredients from shopping list to user's fridge then delete the shopping list"""
    user_id = session["user_id"]
    list_id = int(request.args.get("action")[6:])

    # Get list content
    list_db = db.execute("SELECT ingredient_id, quantity FROM ing2list WHERE list_id = ?", list_id)


    # Insert or update ingredients data into fridges table
    for item in range(len(list_db)):
        check = db.execute("SELECT id FROM fridges WHERE user_id = ? AND ingredient_id = ?", \
                           user_id, list_db[item]["ingredient_id"])
        if not check:
            db.execute("INSERT INTO fridges (user_id, ingredient_id, quantity) VALUES (?, ?, ?)", user_id, \
                list_db[item]["ingredient_id"], list_db[item]["quantity"])
        else:
            curr_quantity = db.execute("SELECT quantity FROM fridges WHERE user_id = ? AND ingredient_id = ?", \
                                       user_id, list_db[item]["ingredient_id"])[0]["quantity"]
            db.execute("UPDATE fridges SET quantity = ? WHERE user_id = ? AND ingredient_id = ?", \
                       curr_quantity + list_db[item]["quantity"], user_id, list_db[item]["ingredient_id"])

    # After updating fridges remove shopping list from db
    db.execute("DELETE FROM ing2list WHERE list_id = ?", list_id)
    db.execute("DELETE FROM shopping_lists WHERE id = ?", list_id)
    return redirect("/")


@app.route("/what_can_i_cook", methods=["GET", "POST"])
@login_required
def what_can_i_cook():
    user_id = session["user_id"]

    if request.method == "GET":
        # Get user's fridge content
        fridge_db = db.execute("SELECT name FROM ingredients WHERE id IN \
                               (SELECT ingredient_id FROM fridges WHERE user_id = ?)", user_id)
        fridge_ings_names = [fridge_ing["name"] for fridge_ing in fridge_db]

        # Get all user's recipes and their names
        recipes_db = db.execute("SELECT id, name FROM recipes WHERE user_id = ?", user_id)
        recipes_info = {recipe["id"]: recipe["name"] for recipe in recipes_db}

        # Initialize a list to store recipe matches as tuples (recipe_id, recipe_name)
        recipe_matches = []

        # Loop through all recipes
        for recipe_id, recipe_name in recipes_info.items():
            # Get the ingredients needed for this recipe
            recipe_ingredients_db = db.execute("SELECT name FROM ingredients WHERE id IN \
                                         (SELECT ingredient_id FROM ing2rec WHERE recipe_id = ?)", recipe_id)
            recipe_ingredients = [ing["name"] for ing in recipe_ingredients_db]

            # Initialize a list for matched ingredients for this recipe
            ing_matches = []

            # Loop through the ingredients of this recipe
            for recipe_ing in recipe_ingredients:
                # Check if the ingredient is in the fridge
                if recipe_ing in fridge_ings_names:
                    ing_matches.append(recipe_ing)

            # Check if all ingredients of the recipe are in the fridge
            if sorted(ing_matches) == sorted(recipe_ingredients):
                # Append a tuple (recipe_id, recipe_name) to the list
                recipe_matches.append((recipe_id, recipe_name))

        # Now, `recipe_matches` is a list of tuples where each tuple contains (recipe_id, recipe_name)
        return render_template("recipe_results.html", recipe_matches=recipe_matches, items=range(len(recipe_matches)))


@app.route("/canceled")
def canceled():
    """Cancel an action"""
    return redirect("/")

