-- users and passwords table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL);

-- ingredients (fridges) table
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR NOT NULL,
    unit VARCHAR DEFAULT "pcs" NOT NULL,
    UNIQUE(name, unit));

-- recipes table
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    portions INTEGER DEFAULT 1 NOT NULL,
    tips TEXT DEFAULT "Combine all of the ingredients and you are done!" NOT NULL,
    image TEXT DEFAULT "images/recipe.png" NOT NULL,
    date_added TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
        UNIQUE(name, user_id));

-- shopping lists table
CREATE TABLE shopping_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    name VARCHAR UNIQUE NOT NULL,
    date_added TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id));

-- ingredients in recipes table
CREATE TABLE ing2rec (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity REAL DEFAULT 1 NOT NULL,
        FOREIGN KEY(recipe_id) REFERENCES recipes(id),
        FOREIGN KEY(ingredient_id) REFERENCES ingredients(id),
        UNIQUE(recipe_id, ingredient_id));

CREATE TABLE ing2list (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    list_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity REAL DEFAULT 1 NOT NULL,
        FOREIGN KEY(list_id) REFERENCES shopping_lists(id),
        FOREIGN KEY(ingredient_id) REFERENCES ingredients(id),
        UNIQUE(list_id, ingredient_id));

CREATE TABLE fridges (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    ingredient_id INTEGER UNIQUE NOT NULL,
    quantity REAL DEFAULT 1 NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(ingredient_id) REFERENCES ingredients(id),
        UNIQUE(user_id, ingredient_id));

