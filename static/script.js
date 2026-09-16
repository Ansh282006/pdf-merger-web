document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const form = document.getElementById('uploadForm');
    const mergeBtn = document.getElementById('mergeBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = mergeBtn.querySelector('.btn-spinner');
    const toolSelect = document.getElementById('toolSelect');
    const dropzoneText = document.getElementById('dropzoneText');
    const dropzoneSubtext = document.getElementById('dropzoneSubtext');

    let selectedFiles = [];

    // --- Tool Switching Logic ---
    toolSelect.addEventListener('change', (e) => {
        const tool = e.target.value;
        selectedFiles = []; // Reset files when tool changes
        fileInput.value = ''; // Clear native input
        renderFileList();

        if (tool === 'merge') {
            form.action = '/merge';
            fileInput.accept = '.pdf';
            fileInput.multiple = true;
            dropzoneText.textContent = 'Drag & drop PDF files here';
            dropzoneSubtext.textContent = 'Supports multiple PDF files';
            btnText.textContent = 'Merge PDFs';
        } else if (tool === 'compress') {
            form.action = '/compress';
            fileInput.accept = '.pdf';
            fileInput.multiple = false;
            dropzoneText.textContent = 'Drag & drop a PDF file here';
            dropzoneSubtext.textContent = 'Supports single PDF file';
            btnText.textContent = 'Compress PDF';
        } else if (tool === 'pdf-to-image') {
            form.action = '/pdf-to-image';
            fileInput.accept = '.pdf';
            fileInput.multiple = false;
            dropzoneText.textContent = 'Drag & drop a PDF file here';
            dropzoneSubtext.textContent = 'Supports single PDF file';
            btnText.textContent = 'Convert to Images (ZIP)';
        } else if (tool === 'image-to-pdf') {
            form.action = '/image-to-pdf';
            fileInput.accept = 'image/*';
            fileInput.multiple = true;
            dropzoneText.textContent = 'Drag & drop image files here';
            dropzoneSubtext.textContent = 'Supports multiple images (PNG, JPG)';
            btnText.textContent = 'Convert to PDF';
        }
    });

    // --- Drag & Drop Events ---
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // --- File Handling ---
    function handleFiles(files) {
        const isImageMode = fileInput.accept.includes('image');
        const allowedType = isImageMode ? 'image/' : 'application/pdf';
        
        const validFiles = Array.from(files).filter(f => f.type.startsWith(allowedType));
        
        if (validFiles.length === 0) {
            alert(`Please select valid ${isImageMode ? 'image' : 'PDF'} files only.`);
            return;
        }

        // Append to selectedFiles, or overwrite if multiple isn't allowed
        if (fileInput.multiple) {
            selectedFiles = selectedFiles.concat(validFiles);
        } else {
            selectedFiles = [validFiles[0]];
        }

        updateFileInput(); // CRITICAL FIX: Sync JS array with HTML input
        renderFileList();
    }

    // CRITICAL FIX: Updates the native HTML file input with the JS file array
    function updateFileInput() {
        const dataTransfer = new DataTransfer();
        selectedFiles.forEach(file => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;
    }

    function renderFileList() {
        fileList.innerHTML = '';
        selectedFiles.forEach((file, index) => {
            const item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML = `
                <span>📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)</span>
                <button type="button" class="remove-file" data-index="${index}">&times;</button>
            `;
            fileList.appendChild(item);
        });

        // Remove file handler
        fileList.querySelectorAll('.remove-file').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = parseInt(e.target.dataset.index);
                selectedFiles.splice(idx, 1);
                updateFileInput(); // Sync again
                renderFileList();
            });
        });
    }

    // --- Form Submission (Loading State) ---
    form.addEventListener('submit', (e) => {
        if (selectedFiles.length === 0) {
            e.preventDefault();
            alert('Please add at least one file.');
            return;
        }

        // Show loading state
        btnText.classList.add('d-none');
        btnSpinner.classList.remove('d-none');
        mergeBtn.disabled = true;
    });
});