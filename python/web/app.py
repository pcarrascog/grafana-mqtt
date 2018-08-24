#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
# Autor: Diego Caraballo
# www.pythondiario.com
 
from flask import Flask
app = Flask(__name__)
  
@app.route("/")
def hello():
    return "Hola Mundo!"
  
if __name__ == "__main__":
    app.run()
