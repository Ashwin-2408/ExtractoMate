from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import pandas as pd
from transformers import pipeline
from flask_cors import CORS
from os import environ

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://extracto-mate.vercel.app", "http://localhost:3000"],
        "methods": ["POST", "GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
FILTERED_FOLDER = os.path.join(os.path.dirname(__file__), 'filtered_data')
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Update model to much smaller version
model_name = "deepset/minilm-uncased-squad2"
nlp = pipeline('question-answering', 
    model=model_name, 
    tokenizer=model_name,
    device=-1
)

# Configure app settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FILTERED_FOLDER'] = FILTERED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Add memory optimization
import gc
import torch

# Update model configuration for minimal memory usage
model_name = "deepset/tinyroberta-squad2"  # Even smaller model
nlp = pipeline('question-answering', 
    model=model_name, 
    tokenizer=model_name,
    device=-1,
    model_kwargs={'low_cpu_mem_usage': True}
)

# Add better memory management
def cleanup_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    
@app.route('/api/process', methods=['POST'])
def process_files():
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['FILTERED_FOLDER'], exist_ok=True)

        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400

        questions_input = request.form.get('questions')
        labels_input = request.form.get('labels')
        
        if not questions_input or not labels_input:
            return jsonify({'error': 'Questions and labels are required'}), 400

        questions = [q.strip() for q in questions_input.split(',')]
        labels = [l.strip() for l in labels_input.split(',')]

        result = {}
        files = request.files.getlist('files')
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        context = f.read()
                        if len(context) > 5000:  # Limit context size
                            context = context[:5000]

                    file_result = {}
                    for question, label in zip(questions, labels):
                        QA_input = {
                            'question': question,
                            'context': context
                        }
                        res = nlp(QA_input)
                        file_result[label] = res['answer']
                        cleanup_memory()

                    result[filename] = file_result
                except Exception as e:
                    print(f"Error processing file {filename}: {str(e)}")
                    continue
                finally:
                    # Clean up uploaded file
                    if os.path.exists(filepath):
                        os.remove(filepath)

        if not result:
            return jsonify({'error': 'No results generated'}), 500

        # Save results
        result_file_path = os.path.join(app.config['FILTERED_FOLDER'], 'result.json')
        with open(result_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)

        df = pd.DataFrame(result).T
        csv_file_path = os.path.join(app.config['FILTERED_FOLDER'], 'filtered_results.csv')
        df.to_csv(csv_file_path, index=True)

        cleanup_memory()  # Final cleanup
        return jsonify({
            'success': True,
            'csvUrl': '/api/download/filtered_results.csv',
            'jsonUrl': '/api/download/result.json'
        })
    except Exception as e:
        print(f"Error in process_files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['FILTERED_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
