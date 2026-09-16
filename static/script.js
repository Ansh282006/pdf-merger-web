document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const form = document.getElementById('uploadForm');
    const mergeBtn = document.getElementById('mergeBtn');
    const btnText = mergeBtn.querySelector('.btn-text');
    const btnSpinner = mergeBtn.querySelector('.btn-spinner');

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
    let selectedFiles = [];

    function handleFiles(files) {
        const pdfFiles = Array.from(files).filter(f => f.type === 'application/pdf');
        if (pdfFiles.length === 0) {
            alert('Please select PDF files only.');
            return;
        }
        selectedFiles = pdfFiles;
        renderFileList();
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
                renderFileList();
            });
        });
    }

    // --- Form Submission (Loading State) ---
    form.addEventListener('submit', (e) => {
        if (selectedFiles.length === 0) {
            e.preventDefault();
            alert('Please add at least one PDF file.');
            return;
        }

        // Show loading state
        btnText.classList.add('d-none');
        btnSpinner.classList.remove('d-none');
        mergeBtn.disabled = true;
    });
});