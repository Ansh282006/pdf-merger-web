import os
import zipfile
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from pypdf import PdfWriter
import pikepdf
import fitz  # PyMuPDF
from PIL import Image

# --- 1. Setup Absolute Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- 2. Initialize Flask App ---
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# --- 3. Helper Functions ---
def save_uploaded_files(files, allowed_extensions):
    """Saves uploaded files to the upload folder and returns their paths."""
    saved_paths = []
    for file in files:
        if file and file.filename.lower().endswith(allowed_extensions):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_paths.append(filepath)
    return saved_paths

def cleanup_files(paths):
    """Deletes files from the server after processing."""
    for path in paths:
        if os.path.exists(path):
            os.remove(path)

# --- 4. Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    uploaded_files = request.files.getlist('pdf_files')
    saved_paths = save_uploaded_files(uploaded_files, '.pdf')
    
    if not saved_paths:
        return "Error: No valid PDF files were uploaded.", 400
        
    try:
        merger = PdfWriter()
        for path in saved_paths:
            merger.append(path)
            
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'merged_document.pdf')
        with open(output_path, 'wb') as f:
            merger.write(f)
        merger.close()
        
        return send_file(output_path, as_attachment=True, download_name='merged_document.pdf')
    except Exception as e:
        print(f"MERGE ERROR: {e}")
        return f"Error merging PDFs: {str(e)}", 500
    finally:
        cleanup_files(saved_paths)

@app.route('/compress', methods=['POST'])
def compress():
    uploaded_files = request.files.getlist('pdf_files')
    saved_paths = save_uploaded_files(uploaded_files, '.pdf')
    
    if not saved_paths:
        return "Error: No valid PDF file uploaded.", 400
        
    try:
        input_path = saved_paths[0] # Compress only the first file
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'compressed_document.pdf')
        
        # Open and save with maximum compression settings
        with pikepdf.open(input_path) as pdf:
            pdf.save(
                output_path, 
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate
            )
            
        return send_file(output_path, as_attachment=True, download_name='compressed_document.pdf')
    except Exception as e:
        print(f"COMPRESSION ERROR: {e}") # This prints to your terminal
        return f"Error compressing PDF: {str(e)}", 500
    finally:
        cleanup_files(saved_paths)

@app.route('/pdf-to-image', methods=['POST'])
def pdf_to_image():
    uploaded_files = request.files.getlist('pdf_files')
    saved_paths = save_uploaded_files(uploaded_files, '.pdf')
    
    if not saved_paths:
        return "Error: No valid PDF file uploaded.", 400
        
    try:
        input_path = saved_paths[0]
        output_zip_path = os.path.join(app.config['OUTPUT_FOLDER'], 'converted_images.zip')
        
        doc = fitz.open(input_path)
        
        # Save the ZIP file directly to the outputs folder instead of memory
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=150) # Higher DPI = better quality
                img_data = pix.tobytes("png")
                zip_file.writestr(f"page_{page_num + 1}.png", img_data)
        
        doc.close()
        
        # Send the saved ZIP file
        return send_file(output_zip_path, mimetype='application/zip', as_attachment=True, download_name='converted_images.zip')
    except Exception as e:
        print(f"PDF TO IMAGE ERROR: {e}") # This prints to your terminal
        return f"Error converting PDF to Image: {str(e)}", 500
    finally:
        cleanup_files(saved_paths)

@app.route('/image-to-pdf', methods=['POST'])
def image_to_pdf():
    uploaded_files = request.files.getlist('pdf_files')
    # Allow common image formats
    saved_paths = save_uploaded_files(uploaded_files, ('.png', '.jpg', '.jpeg', '.webp'))
    
    if not saved_paths:
        return "Error: No valid image files uploaded.", 400
        
    try:
        images = []
        for path in saved_paths:
            img = Image.open(path).convert('RGB')
            images.append(img)
            
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'converted_images.pdf')
        # Save the first image, appending the rest
        images[0].save(output_path, save_all=True, append_images=images[1:])
        
        return send_file(output_path, as_attachment=True, download_name='converted_images.pdf')
    except Exception as e:
        print(f"IMAGE TO PDF ERROR: {e}")
        return f"Error converting Image to PDF: {str(e)}", 500
    finally:
        cleanup_files(saved_paths)

# --- 5. Run the App ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)