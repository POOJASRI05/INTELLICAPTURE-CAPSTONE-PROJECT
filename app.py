import os
import pandas as pd
from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
from extract_tables import extract_tables_from_pdf, extract_text_from_pdf
from googletrans import Translator
import pyttsx3
import tempfile
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# Initialize translator and TTS engine
translator = Translator()
tts_engine = pyttsx3.init()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"
        
        file = request.files["file"]
        
        if file.filename == "":
            return "No selected file"
        
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)  # Save uploaded file
            
            # Extract tables first
            tables = extract_tables_from_pdf(file_path)
            
            # If tables found, save them
            table_files = []
            if tables:
                for idx, table in enumerate(tables):
                    # Clean the table
                    table_cleaned = table.dropna(axis=0, how='all')
                    table_cleaned.columns = table_cleaned.columns.str.strip().str.lower()
                    
                    # Save table
                    table_filename = f"{os.path.splitext(file.filename)[0]}_table_{idx}.csv"
                    table_path = os.path.join(OUTPUT_FOLDER, table_filename)
                    table_cleaned.to_csv(table_path, index=False)
                    table_files.append(table_filename)
            
            # Extract text
            output_filename = f"{os.path.splitext(file.filename)[0]}.txt"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            extracted_text = extract_text_from_pdf(file_path)
            
            # Save extracted text
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            
            return render_template("results.html", 
                                 text_filename=output_filename,
                                 table_files=table_files,
                                 extracted_text=extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text)

    return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

@app.route("/translate", methods=["POST"])
def translate_text():
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('target_lang', 'en')
    
    try:
        translated = translator.translate(text, dest=target_lang)
        return jsonify({'translated_text': translated.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/text_to_speech", methods=["POST"])
def text_to_speech():
    data = request.get_json()
    text = data.get('text', '')
    
    try:
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # Save speech to temporary file
        tts_engine.save_to_file(text, temp_filename)
        tts_engine.runAndWait()
        
        return send_file(temp_filename, as_attachment=True, download_name='speech.wav')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/search", methods=["POST"])
def search_text():
    data = request.get_json()
    text = data.get('text', '')
    query = data.get('query', '')
    
    # Simple search implementation
    lines = text.split('\n')
    results = []
    
    for i, line in enumerate(lines):
        if query.lower() in line.lower():
            # Highlight the found text
            highlighted_line = line.replace(query, f"<mark>{query}</mark>")
            results.append({
                'line_number': i+1,
                'content': highlighted_line
            })
    
    return jsonify({'results': results})

if __name__ == "__main__":
    app.run(debug=True)