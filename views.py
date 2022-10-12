from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return  render_template("home.html")

@views.route('/eth')
def ethereum():
    return  render_template("ethereum.html")

@views.route('/btc')
def bitcoin():
    return  render_template("bitcoin.html")