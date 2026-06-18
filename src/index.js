document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const dropzonePrompt = document.getElementById('dropzone-prompt');
    const filePreviewCard = document.getElementById('file-preview-card');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const btnRemoveFile = document.getElementById('btn-remove-file');
    
    const btnCompress = document.getElementById('btn-compress');
    const btnDecompress = document.getElementById('btn-decompress');
    const modeIndicator = document.getElementById('mode-indicator');
    
    const btnProcess = document.getElementById('btn-process');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    
    const resultsPanel = document.getElementById('results-panel');
    const resultsTitle = document.getElementById('results-title');
    const labelSizeOrig = document.getElementById('label-size-orig');
    const labelSizeProc = document.getElementById('label-size-proc');
    const valSizeOrig = document.getElementById('val-size-orig');
    const valSizeProc = document.getElementById('val-size-proc');
    const valSavings = document.getElementById('val-savings');
    const valRatio = document.getElementById('val-ratio');
    const labelSavings = document.getElementById('label-savings');
    const labelRatio = document.getElementById('label-ratio');
    
    const frequencySection = document.getElementById('frequency-section');
    const frequencyList = document.getElementById('frequency-list');
    
    const btnDownload = document.getElementById('btn-download');
    
    // Application State
    let currentFile = null;
    let currentMode = 'compress'; // 'compress' or 'decompress'
    let processedResult = null; // Stores { filename, contentBlob }

    // Toggle Modes
    function setMode(mode) {
        currentMode = mode;
        if (mode === 'compress') {
            btnCompress.classList.add('active');
            btnDecompress.classList.remove('active');
            modeIndicator.style.transform = 'translateX(0)';
            document.getElementById('formats-hint').textContent = 'Supports .txt, .docx files';
        } else {
            btnCompress.classList.remove('active');
            btnDecompress.classList.add('active');
            modeIndicator.style.transform = 'translateX(100%)';
            document.getElementById('formats-hint').textContent = 'Supports .huf files';
        }
        updateActionButtonState();
    }

    btnCompress.addEventListener('click', () => setMode('compress'));
    btnDecompress.addEventListener('click', () => setMode('decompress'));

    // Handle File Selection
    function selectFile(file) {
        if (!file) return;
        currentFile = file;
        
        // Autodetect mode based on file extension
        const ext = file.name.split('.').pop().toLowerCase();
        if (ext === 'huf') {
            setMode('decompress');
        } else {
            setMode('compress');
        }

        // Show Preview Card
        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);
        
        dropzonePrompt.style.display = 'none';
        filePreviewCard.style.display = 'flex';
        
        updateActionButtonState();
        hideResults();
    }

    function removeFile() {
        currentFile = null;
        fileInput.value = '';
        
        dropzonePrompt.style.display = 'block';
        filePreviewCard.style.display = 'none';
        
        updateActionButtonState();
        hideResults();
    }

    btnRemoveFile.addEventListener('click', (e) => {
        e.stopPropagation();
        removeFile();
    });

    // Drag and Drop Listeners
    dropzone.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            selectFile(e.target.files[0]);
        }
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-over');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-over');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            selectFile(e.dataTransfer.files[0]);
        }
    });

    // Update Action Button Text & Enablement
    function updateActionButtonState() {
        if (!currentFile) {
            btnProcess.disabled = true;
            btnText.textContent = 'Select a file';
            return;
        }
        btnProcess.disabled = false;
        btnText.textContent = currentMode === 'compress' ? 'Compress File' : 'Decompress File';
    }

    // Hide results panel
    function hideResults() {
        resultsPanel.style.display = 'none';
        processedResult = null;
    }

    // Process File (Upload and Run algorithm)
    btnProcess.addEventListener('click', async () => {
        if (!currentFile) return;

        // Set Loading State
        btnProcess.disabled = true;
        btnSpinner.style.display = 'inline-block';
        btnText.textContent = currentMode === 'compress' ? 'Compressing...' : 'Decompression...';

        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('mode', currentMode);

        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(errText || 'Failed to process file');
            }

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || 'Server processing error');
            }

            // Parse response
            const byteCharacters = atob(data.content_base64);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const contentBlob = new Blob([byteArray], { type: 'application/octet-stream' });
            
            processedResult = {
                filename: data.filename,
                contentBlob: contentBlob
            };

            // Display Results
            displayResults(data.stats);

        } catch (error) {
            console.error(error);
            alert(`Error processing file: ${error.message}`);
        } finally {
            // Restore Button State
            btnSpinner.style.display = 'none';
            updateActionButtonState();
        }
    });

    // Download Handler
    btnDownload.addEventListener('click', () => {
        if (!processedResult) return;
        
        const url = URL.createObjectURL(processedResult.contentBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = processedResult.filename;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // Display statistics and frequencies in UI
    function displayResults(stats) {
        resultsPanel.style.display = 'flex';
        
        if (currentMode === 'compress') {
            resultsTitle.textContent = 'File Compressed';
            labelSizeOrig.textContent = 'Original Size';
            labelSizeProc.textContent = 'Compressed Size';
            labelSavings.textContent = 'Space Saved';
            labelRatio.textContent = 'Compression Ratio';
            
            valSizeOrig.textContent = formatBytes(stats.orig_size);
            valSizeProc.textContent = formatBytes(stats.proc_size);
            
            valSavings.textContent = `${stats.savings.toFixed(2)}%`;
            valRatio.textContent = `${stats.ratio.toFixed(2)}x`;
            
            // Show character frequencies
            frequencySection.style.display = 'flex';
            renderFrequencies(stats.frequencies);
        } else {
            resultsTitle.textContent = 'File Decompressed';
            labelSizeOrig.textContent = 'Compressed Size';
            labelSizeProc.textContent = 'Decompressed Size';
            labelSavings.textContent = 'Expansion Factor';
            labelRatio.textContent = 'Verification Status';
            
            valSizeOrig.textContent = formatBytes(stats.comp_size);
            valSizeProc.textContent = formatBytes(stats.decomp_size);
            valSavings.textContent = `${stats.factor.toFixed(2)}x`;
            valRatio.textContent = 'PASSED';
            
            // Hide character frequencies for decompress
            frequencySection.style.display = 'none';
        }
        
        // Scroll into view
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Render Character Frequencies
    function renderFrequencies(frequencies) {
        frequencyList.innerHTML = '';
        if (!frequencies || frequencies.length === 0) {
            frequencyList.innerHTML = '<div class="subtext" style="text-align:center;">No character frequencies available.</div>';
            return;
        }

        // Get max frequency for progress bar scaling
        const maxFreq = Math.max(...frequencies.map(f => f[1]));

        frequencies.forEach(([char, count]) => {
            const percentage = maxFreq > 0 ? (count / maxFreq) * 100 : 0;
            
            // Display character nicely
            let displayChar = char;
            if (char === ' ') displayChar = 'Space';
            else if (char === '\n') displayChar = '\\n';
            else if (char === '\r') displayChar = '\\r';
            else if (char === '\t') displayChar = '\\t';
            
            const item = document.createElement('div');
            item.className = 'freq-item';
            item.innerHTML = `
                <span class="freq-char-badge" title="Character">${escapeHtml(displayChar)}</span>
                <div class="freq-bar-container">
                    <div class="freq-bar-fill" style="width: 0%"></div>
                </div>
                <span class="freq-count">${count}</span>
            `;
            
            frequencyList.appendChild(item);
            
            // Trigger animation in next frame
            requestAnimationFrame(() => {
                item.querySelector('.freq-bar-fill').style.width = `${percentage}%`;
            });
        });
    }

    // Helper: Escape HTML string to avoid injection issues
    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Helper: Format Bytes nicely
    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
});
