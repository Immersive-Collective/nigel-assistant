from flask import Flask, render_template, send_from_directory, request, redirect, url_for
import os
from datetime import datetime
import pdfplumber
import json
import logging
import re
from transformers import pipeline

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
TXT_FOLDER = 'documents/txt'
NER_FOLDER = 'documents/ner'
SUMMARY_FOLDER = 'documents/summary'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TXT_FOLDER'] = TXT_FOLDER
app.config['NER_FOLDER'] = NER_FOLDER
app.config['SUMMARY_FOLDER'] = SUMMARY_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TXT_FOLDER, exist_ok=True)
os.makedirs(NER_FOLDER, exist_ok=True)
os.makedirs(SUMMARY_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ner_model = pipeline("ner", model="dslim/bert-large-NER", tokenizer="dslim/bert-large-NER", grouped_entities=True)
summarization_model = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nerf-processor')
def nerf_processor():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files_data = []
    for file in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        file_stat = os.stat(file_path)
        txt_file = os.path.splitext(file)[0] + '.txt'
        ner_file = os.path.splitext(file)[0] + '.json'
        summary_file = os.path.splitext(file)[0] + '.summary.txt'
        txt_file_path = os.path.join(app.config['TXT_FOLDER'], txt_file)
        ner_file_path = os.path.join(app.config['NER_FOLDER'], ner_file)
        summary_file_path = os.path.join(app.config['SUMMARY_FOLDER'], summary_file)
        processed = os.path.exists(txt_file_path)
        ner_processed = os.path.exists(ner_file_path)
        summary_processed = os.path.exists(summary_file_path)
        files_data.append({
            'id': file_stat.st_ino,
            'date': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'name': file,
            'processed': processed,
            'ner_processed': ner_processed,
            'summary_processed': summary_processed
        })
    return render_template('nerf_processor.html', files=files_data)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/documents/txt/<filename>')
def txt_file(filename):
    return send_from_directory(app.config['TXT_FOLDER'], filename)

@app.route('/documents/ner/<filename>')
def ner_file(filename):
    return send_from_directory(app.config['NER_FOLDER'], filename)

@app.route('/documents/summary/<filename>')
def summary_file(filename):
    return send_from_directory(app.config['SUMMARY_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logger.error('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        logger.error('No selected file')
        return redirect(request.url)
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        logger.info(f'File {file.filename} uploaded')
        return redirect(url_for('nerf_processor'))

@app.route('/process/<filename>')
def process_file(filename):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    txt_filename = os.path.splitext(filename)[0] + '.txt'
    txt_path = os.path.join(app.config['TXT_FOLDER'], txt_filename)
    ner_filename = os.path.splitext(filename)[0] + '.json'
    ner_path = os.path.join(app.config['NER_FOLDER'], ner_filename)
    summary_filename = os.path.splitext(filename)[0] + '.summary.txt'
    summary_path = os.path.join(app.config['SUMMARY_FOLDER'], summary_filename)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''.join([page.extract_text() + '\n' for page in pdf.pages])
        with open(txt_path, 'w') as txt_file:
            txt_file.write(text)
        logger.info(f'Processing {filename} completed and text extracted')

        ner_results = ner_model(text)
        entities = [{"text": ent['word'], "label": ent['entity_group']} for ent in ner_results]

        cleaned_entities = post_process_entities(entities)
        with open(ner_path, 'w') as ner_file:
            json.dump(cleaned_entities, ner_file)
        logger.info(f'NER processing for {filename} completed')

        summary = generate_summary(cleaned_entities, text)
        with open(summary_path, 'w') as summary_file:
            summary_file.write(summary)
        logger.info(f'Summary generation for {filename} completed')

        return redirect(url_for('nerf_processor'))
    except Exception as e:
        logger.error(f'Error processing {filename}: {e}')
        return str(e), 500

def post_process_entities(entities):
    cleaned = []
    for ent in entities:
        text, label = ent['text'], ent['label']
        
        text = text.strip()
        
        if label == 'PERSON' and not any(char.isalpha() for char in text):
            continue

        if label == 'GPE' and 'Phone' in text:
            text = text.replace(' Phone', '').strip()
        
        if label == 'PHONE' and not re.match(r'^\+?\d{10,15}$', text):
            continue

        if label == 'EMAIL' and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', text):
            continue
        
        if text.startswith('##'):
            if cleaned:
                cleaned[-1]['text'] += text.replace('##', '')
            continue
        
        cleaned.append({'text': text, 'label': label})
    
    return cleaned

def generate_summary(entities, text):
    summary_data = {
        "name": [],
        "job_titles": [],
        "organizations": [],
        "locations": [],
        "skills": [],
        "emails": [],
        "phones": [],
        "dates": [],
        "degrees": [],
        "achievements": [],
        "urls": []
    }
    
    ENTITY_CATEGORIES = {
        "PER": "name",
        "ORG": "organizations",
        "LOC": "locations",
        "DATE": "dates",
        "EMAIL": "emails",
        "PHONE": "phones",
        "TITLE": "job_titles",
        "SKILL": "skills",
        "DEGREE": "degrees",
        "ACHIEVEMENT": "achievements",
        "URL": "urls"
    }
    
    for entity in entities:
        category = ENTITY_CATEGORIES.get(entity["label"], None)
        if category:
            summary_data[category].append(entity["text"])

    for key in summary_data:
        summary_data[key] = list(set(summary_data[key]))

    summary_text = []

    if summary_data["name"]:
        summary_text.append(f"{summary_data['name'][0]} is a professional with experience in roles such as {', '.join(summary_data['job_titles'])}.")
    
    if summary_data["organizations"]:
        summary_text.append(f"They have worked at organizations including {', '.join(summary_data['organizations'])} in locations such as {', '.join(summary_data['locations'])}.")
    
    if summary_data["skills"]:
        summary_text.append(f"Their key skills include {', '.join(summary_data['skills'])}.")
    
    if summary_data["degrees"]:
        summary_text.append(f"They hold degrees such as {', '.join(summary_data['degrees'])}.")
    
    if summary_data["achievements"]:
        summary_text.append(f"Some notable achievements are {', '.join(summary_data['achievements'])}.")
    
    if summary_data["emails"]:
        summary_text.append(f"You can contact them at {', '.join(summary_data['emails'])}.")
    
    if summary_data["phones"]:
        summary_text.append(f"Alternatively, reach them by phone at {', '.join(summary_data['phones'])}.")
    
    if summary_data["urls"]:
        summary_text.append(f"More information can be found at their website: {', '.join(summary_data['urls'])}.")

    input_text = " ".join(summary_text)
    summarized_text = summarization_model(input_text, max_length=150, min_length=40, do_sample=False)

    return summarized_text[0]['summary_text']

if __name__ == '__main__':
    app.run(debug=True)
