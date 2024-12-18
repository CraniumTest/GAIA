from flask import Flask, request, jsonify
from transformers import pipeline
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)

# Initialize NLP Pipeline
summarizer = pipeline("summarization")

# Sample Database connection using SQLAlchemy
DATABASE_URI = 'sqlite:///grants.db'
engine = create_engine(DATABASE_URI)

def create_tables():
    with engine.connect() as connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS grants (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                deadline DATE NOT NULL
            )
        ''')

@app.route('/analyze', methods=['POST'])
def analyze_text():
    data = request.json
    text_to_analyze = data.get('text')
    summarized_text = summarizer(text_to_analyze, max_length=50, min_length=25, do_sample=False)
    return jsonify({'summary': summarized_text})

@app.route('/add_grant', methods=['POST'])
def add_grant():
    data = request.json
    grant_name = data.get('name')
    description = data.get('description')
    deadline = data.get('deadline')
    
    with engine.connect() as connection:
        query = f"INSERT INTO grants (name, description, deadline) VALUES ('{grant_name}', '{description}', '{deadline}')"
        connection.execute(query)
        
    return jsonify({"status": "success", "message": "Grant added successfully"})

@app.route('/get_grants', methods=['GET'])
def get_grants():
    with engine.connect() as connection:
        result = connection.execute("SELECT * FROM grants")
        grants = [dict(row) for row in result]
    return jsonify(grants)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
