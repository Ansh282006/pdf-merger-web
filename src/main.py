import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from pypdf import PdfWriter

# Tell Flask where templates and static folders are
app = Flask(__name__, template_folder='../templates', static_folder='../static')

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/')
def index():
    """Home page with the upload form."""
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    """Handles the PDF upload and merging."""
    uploaded_files = request.files.getlist('pdf_files')
    
    if not uploaded_files or uploaded_files[0].filename == '':
        return redirect(url_for('index'))
    
    # Save the uploaded files
    saved_paths = []
    for file in uploaded_files:
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_paths.append(filepath)
            
    # Merge the PDFs
    merger = PdfWriter()
    for path in saved_paths:
        merger.append(path)
        
    output_filename = 'merged_document.pdf'
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    with open(output_path, 'wb') as f:
        merger.write(f)
    merger.close()
    
    # Clean up uploaded files (optional, but good practice)
    for path in saved_paths:
        os.remove(path)
        
    # Send the merged file to the user
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)