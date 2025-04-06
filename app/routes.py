from flask import Blueprint, render_template, current_app
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from flask import render_template
from app import create_app
from app import db 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/plots')
def plots():
    return render_template('plots.html')