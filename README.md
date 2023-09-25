# FoodTr@ack
#### Hello CS50!

##### I built a web based application using PSET 9 : "Finance" distribution code that allows users to:
1) register, login, log out and change their password.
2) view homepage with their current fridge content (list of ingredients available) with a possibility of manual updates,
3) create, save in db and make a shopping list out of a recipe,
4) create and save in db a shopping list,
5) modify shopping list's content and confirm bought items to add them to the fridge,
6) propose a recipe to cook based on all of ingredients' names that can be found in the fridge.

UPDATE: I made the application live on pythonanywhere! You are welcome to check it out. :)
###### To start [Click Here](http://kttrojan.pythonanywhere.com/login)

## Functions description:

### foodtrack.db
The .schema of the database can be found in the main project directory. Database consists of:
#### users table
For storing usernames and passwords' hashes.
#### ingredients table
For storing ingredient names and units
#### recipes table
For storing each user's recipes' names, portions, tips, photos and time of creation
#### shopping lists table
For storing each user's shopping lists' names and time of creation
#### ing2rec table
For storing ingredient_ID, quantity and recipe_ID pairs for each user
#### ing2list table
For storing ingredient_ID, quantity, list_ID pairs for each user
#### fridges table
For storing ingredient_ID and quantity for each user's fridge (or kitchen)

## Layout.html
Standard template for building html pages. Based on distribution code for CS50x PSET 9 "Finance".

## JS Scripts
Directory
>static/js
contains all the scripts i used for:
+ filtering html table rows based on elements' name (search.js, search_ings.js),
+ sort html table rows alphabetically (sort.js),
+ adding or removing rows from html table,
+ submitting user's input (quantity.js).

Aside from the last script which basically prompts for user input, and returns the value, all of the remaining are based on an online foundings. Links are included in scripts files.


### app.py
Here are descriptions of all the routes user can take.

#### /register route:
The route for registering a new user. After submitting the form from "register.html" template, input is being veryfied and if it checks out user account is created. Verification process includes:
+ checking for username input and if it is not already taken
+ checking for password input and if it is not shorter than 8 characters
+ checking for confirmation input and if it matches the password input

After verificating inputs, user password is being hashed and stored together with username in user's table in foodtrack.db.

#### /login route:
Standard route for loging the user in. Verification process includes:
checking for username input
checking for password input
querying database for username-hash pair

#### /logout route:
Logs user out.

#### /change_password route:
Allows user to provide new password for their account. Verifies password and confirmation input then, if it matches, creates new password's hash and updates hash in users table.

### / route:
Homepage of the application.
##### GET method
Selects all ingredients from fridges table based on logged-in user's ID, then displays it in the table using index.html template. Index.html table also contains buttons for editing quantity and deleting ingredients from fridge. There is also a fixed button in a corner of the page that allows to add new ingredients.
##### POST method
Parses which button was clicked (delete or edit) on which ingredient. If it was delete, then according ingredient is removed from fridge table based on user's ID.
If edit was clicked then the new quantity is obtained, verified and updated in the fridge table.

### /add_ings route:
##### GET method
Returns the template add_ings.html consisting of table of inputs for adding ingredients to fridge.
##### POST method
Obtains user's input ingredients, then verifies them as follows:
+ checks for empty ingredient names or quantities,
+ checks if quantity input is valid decimal number,
+ checks if all units had been selected.

If the verification is successful ingredients and fridges table are updated accordingly and user is redirected to homepage.

### /recipes route:
##### GET method
Returns the template recipes.html consisting of table of all user's recipes and a buttons for:\
+ creating new ones,
+ viewing selected recipe,
+ deleting selected recipe,
+ making a new shopping list with all of recipe's ingredients
##### POST method
Returns template for adding new recipe if user clicked on "Add recipe" button.

### /add_recipe route:
##### POST method
Processes recipe info provided by the user. Files are managed according to the [Flask's documentation](https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/) and stored in /static directory. Then recipe metadata is verified through process similiar to the ones described above and inserted to recipes table. Then the function loops through all ingredients of the recipe, updates ingredients table for any new ingredient then stores recipe ingredients in ing2rec table.

### /view_recipe route:
Returns standard html template for viewing recipe metadata, ingredients and tips.

### /delete_recipe route:
Deletes recipe data from db based on which button the user clicked.

### /lists route:
Similar to recipes : get method displays all of user's shopping lists data and post method renders a template for adding new shopping lists.

### /add_list, view_list, delete_list routes:
Similar to add_recipe, view_recipe and delete_list.

### /modify_list route:
Allows user to modify shopping list content by editing quantities, units, removing or adding ingredients and updating db accordingly.

### /rec2list route:
##### GET method
Makes a new shopping list with all ingredients of a recipe that was selected by the user.
Then redirects user to modify_list template with recipe ingredients already selected.
User can edit quantities, units, add or remove ingredients.
##### POST method
When users confirms changes a function silmilar to /modify_list route takes over, verifies all of the ingredients and updates the database accordingly.

### /add2fridge route:
Updates the fridges table with content of selected shopping list while updating ingredients table for any newfound ingredient. The list is deleted after the process is completed

#### /what_can_i_cook route:
###### This is the function that i struggled with the most. It was supposed to compare user's fridge content with all of recipes ingredients and select recipes for which user has all of the ingredients in required quantity to prepare a meal. However, allowing users to use various units caused the need to keep track of unified quantity of each ingredient. That caused a lot of problems, e.g. using ingredients densities, as provided [here](https://www.fao.org/3/ap815e/ap815e.pdf). Considering the fact that FoodTr@ck was supposed to be a light-weight and user friendly application the what_can_i_cook function was decided to work as follows:

Fridge ingredient names are parsed from the database. All of recipes ingredients are parsed from database. Then names (and only names) are compared between fridge ingredients and a given recipe ingredients. Then if a match if found the matching recipe is added to the table of recipes that user could cook.

###### Note that the user could lack some amounts of some ingredients. The functionality of this route then, could be described as proposition of user's recipes that can be cooked to use part of the remaining ingredients in the fridge.
