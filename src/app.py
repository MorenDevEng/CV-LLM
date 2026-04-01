import os
import sys
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import rag_pipeline

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'pdfs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No se encontró archivo'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            rag_pipeline.process_pdf(filepath)
            return jsonify({
                'success': True,
                'filename': filename
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'})

@app.route('/upload-batch', methods=['POST'])
def upload_batch():
    files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return jsonify({'success': False, 'error': 'No se encontraron archivos'})
    
    if len(files) > 5:
        return jsonify({'success': False, 'error': 'Máximo 5 archivos permitidos'})
    
    valid_files = []
    for file in files:
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            valid_files.append(filepath)
    
    if len(valid_files) == 0:
        return jsonify({'success': False, 'error': 'No se encontraron archivos válidos'})
    
    try:
        rag_pipeline.process_multiple_pdfs(valid_files)
        return jsonify({
            'success': True,
            'files': len(valid_files)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'success': False, 'error': 'Mensaje vacío'})
    
    try:
        response = rag_pipeline.chat(message)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/match', methods=['POST'])
def match_keywords():
    data = request.get_json()
    keywords = data.get('keywords', '')
    
    if not keywords:
        return jsonify({'success': False, 'error': 'No hay palabras clave'})
    
    try:
        result = rag_pipeline.match_keywords(keywords)
        return jsonify({
            'success': True,
            'percentage': result['percentage'],
            'matched': result['matched']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)