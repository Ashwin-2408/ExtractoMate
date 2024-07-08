from flask import Flask, request, render_template, send_from_directory
import os
import json
import pandas as pd
from transformers import pipeline

app = Flask(__name__)
DATA_FOLDER = ''#give the path to the directory containing the files you want to process
FILTERED_FOLDER = 'filtered_data'
app.config['DATA_FOLDER'] = DATA_FOLDER
app.config['FILTERED_FOLDER'] = FILTERED_FOLDER


model_name = "deepset/roberta-base-squad2"
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_files():
    result = {}
    questions_input = request.form['questions']
    questions = [q.strip() for q in questions_input.split(',')]
    labels_input = request.form['labels']
    labels = [l.strip() for l in labels_input.split(',')]

    files = os.listdir(app.config['DATA_FOLDER'])  

    for file_name in files:
        file_path = os.path.join(app.config['DATA_FOLDER'], file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            context = file.read()

        file_result = {}
        for question, label in zip(questions, labels):
            QA_input = {
                'question': question,
                'context': context
            }
            res = nlp(QA_input)
            file_result[label] = res['answer']

        result[file_name] = file_result

    
    result_file_path = os.path.join(app.config['FILTERED_FOLDER'], 'result.json')
    with open(result_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)

    
    df = pd.DataFrame(result).T
    csv_file_path = os.path.join(app.config['FILTERED_FOLDER'], 'filtered_results.csv')
    df.to_csv(csv_file_path, index=True)

    return render_template('result.html', csv_file_name='filtered_results.csv', json_file_name='result.json')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['FILTERED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(FILTERED_FOLDER):
        os.makedirs(FILTERED_FOLDER)
    app.run(debug=True)
