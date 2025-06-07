import pickle 
from flask import g 

def init_model():
    with open("pickles/pipeline.pkl", "rb") as f:
        g.pipeline = pickle.load(f)
    
    return "200 | Success"