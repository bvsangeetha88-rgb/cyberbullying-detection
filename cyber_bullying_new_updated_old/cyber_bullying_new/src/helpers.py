

from flask import redirect, render_template, request, session
import os, random
from cs50 import SQL
from src import meme
import re


def ensure_user_tables(db, username):
    # Only allow alphanumeric and underscore usernames to avoid SQL injection
    if not re.match(r'^\w+$', username):
        return

    posts_table = username
    social_table = username + 'Social'

    # Create posts table if it doesn't exist
    db.execute(f"CREATE TABLE IF NOT EXISTS \"{posts_table}\" (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, nature TEXT, image TEXT, timestamp DATETIME DEFAULT (datetime('now','localtime')), likes INTEGER DEFAULT 0)")

    # Create social/following table if it doesn't exist
    db.execute(f"CREATE TABLE IF NOT EXISTS \"{social_table}\" (id INTEGER PRIMARY KEY AUTOINCREMENT, following TEXT)")

def UserInfo(db, username = None):
    if not username:
        user_id_info = db.execute("SELECT * FROM users WHERE id = :id", id = session["user_id"])[0]
        # Ensure per-user tables exist for the logged-in user
        try:
            ensure_user_tables(db, user_id_info['username'])
        except Exception:
            pass
        dp = "static/dp/" + user_id_info['username'] + "." + user_id_info['dp']
        if not os.path.exists(dp):
            dp = "../static/dp/"+"default.png"
        else:
            dp = "../static/dp/" + user_id_info['username'] + "." + user_id_info['dp']
    else:
        user_id_info = db.execute("SELECT * FROM users WHERE username = :username", username = username)[0]
        # Ensure per-user tables exist for the looked-up user
        try:
            ensure_user_tables(db, user_id_info['username'])
        except Exception:
            pass
        dp = "static/dp/" + user_id_info['username'] + "." + user_id_info['dp']
        if not os.path.exists(dp):
            dp = "../static/dp/"+"default.png"
        else:
            dp = "../static/dp/" + user_id_info['username'] + "." + user_id_info['dp']
    return user_id_info, dp

def error(message, code=400):
    meme.meme(message)
    # The random variable prevents browser caching by adding a
    # randomly generated query string to each request for the dynamic image.
    print(message)
    return render_template("error.html", random=random.randint(1,32500),random1=random.randint(1,32500))