import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import re

from flask import redirect, render_template, session
from functools import wraps
from cs50 import SQL


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def floatify(string):
    """Change format of input to be : integer + "." + decimal"""
    string = string.replace("," , ".")
    string = string.replace(" " , "")
    return string


def check_float(string):
    """ Check if input is a valid floating point number."""
    pattern = r"[-+]?[0-9]*\.[0-9]+|[0-9]+"
    match = re.fullmatch(pattern, string)
    if match:
        return True
    return False

def compare_ingredients(recipe, fridge):
    """Compare ingredients with user's fridge - if any is missing return false"""
    if recipe == fridge:
        return True
    return False
