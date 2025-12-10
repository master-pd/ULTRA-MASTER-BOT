/**
 * 🎨 IMAGE EDITOR - Create & Edit Images
 */

class ImageEditor {
    constructor() {
        this.images = [];
        this.currentImage = null;
        this.canvas = null;
        this.ctx = null;
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;
        
        this.init();
    }
    
    init() {
        this.loadImages();
        this.setupCanvas();
        this.setupEventListeners();
        this.setupDrawing();
    }
    
    loadImages() {
        // Load saved images from localStorage
        const savedImages = localStorage.getItem('master_images');
        if (savedImages) {
            this.images = JSON.parse(savedImages);
            this.renderImageGrid();
        }
        
        // Load from API
        this.fetchImages();
    }
    
    fetchImages() {
        fetch('/api/images')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.images) {
                    this.images = data.images;
                    this.renderImageGrid();
                    this.saveToLocalStorage();
                }
            })
            .catch(error => console.error('Error fetching images:', error));
    }
    
    renderImageGrid() {
        const grid = document.getElementById('images-grid');
        if (!grid) return;
        
        grid.innerHTML = '';
        
        this.images.forEach((image, index) => {
            const imageCard = this.createImageCard(image, index);
            grid.appendChild(imageCard);
        });
        
        if (this.images.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-image"></i>
                    <h3>No Images Yet</h3>
                    <p>Create your first image using the form above!</p>
                </div>
            `;
        }
    }
    
    createImageCard(image, index) {
        const card = document.createElement('div');
        card.className = 'image-card animate__animated animate__fadeIn';
        card.style.animationDelay = `${index * 0.1}s`;
        
        let previewHTML = '';
        
        if (image.image_base64) {
            previewHTML = `<img src="${image.image_base64}" alt="${image.title}" loading="lazy">`;
        } else if (image.image_url) {
            previewHTML = `<img src="${image.image_url}" alt="${image.title}" loading="lazy">`;
        } else {
            previewHTML = `<div class="image-placeholder">
                <i class="fas fa-image"></i>
                <span>${image.type.toUpperCase()}</span>
            </div>`;
        }
        
        card.innerHTML = `
            <div class="image-card-header">
                <h4>${image.title}</h4>
                <span class="image-badge image-${image.type}">${image.type}</span>
            </div>
            <div class="image-preview">
                ${previewHTML}
            </div>
            <div class="image-card-footer">
                <span class="image-date">
                    <i class="far fa-calendar"></i>
                    ${new Date(image.timestamp).toLocaleDateString()}
                </span>
                <div class="image-actions">
                    <button class="btn-view" data-index="${index}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-edit" data-index="${index}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-download" data-index="${index}">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn-delete" data-index="${index}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        // Add event listeners
        card.querySelector('.btn-view').addEventListener('click', () => this.viewImage(image));
        card.querySelector('.btn-edit').addEventListener('click', () => this.editImage(image));
        card.querySelector('.btn-download').addEventListener('click', () => this.downloadImage(image));
        card.querySelector('.btn-delete').addEventListener('click', () => this.deleteImage(index));
        
        return card;
    }
    
    setupCanvas() {
        this.canvas = document.getElementById('image-canvas');
        if (this.canvas) {
            this.ctx = this.canvas.getContext('2d');
            this.resizeCanvas();
        }
    }
    
    resizeCanvas() {
        if (this.canvas) {
            this.canvas.width = this.canvas.offsetWidth;
            this.canvas.height = this.canvas.offsetHeight;
        }
    }
    
    setupDrawing() {
        if (!this.canvas) return;
        
        // Mouse events
        this.canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.canvas.addEventListener('mousemove', (e) => this.draw(e));
        this.canvas.addEventListener('mouseup', () => this.stopDrawing());
        this.canvas.addEventListener('mouseout', () => this.stopDrawing());
        
        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => this.startDrawing(e.touches[0]));
        this.canvas.addEventListener('touchmove', (e) => this.draw(e.touches[0]));
        this.canvas.addEventListener('touchend', () => this.stopDrawing());
    }
    
    startDrawing(e) {
        this.isDrawing = true;
        const rect = this.canvas.getBoundingClientRect();
        this.lastX = e.clientX - rect.left;
        this.lastY = e.clientY - rect.top;
    }
    
    draw(e) {
        if (!this.isDrawing) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.lastX, this.lastY);
        this.ctx.lineTo(currentX, currentY);
        this.ctx.strokeStyle = document.getElementById('drawing-color').value;
        this.ctx.lineWidth = document.getElementById('brush-size').value;
        this.ctx.lineCap = 'round';
        this.ctx.stroke();
        
        this.lastX = currentX;
        this.lastY = currentY;
    }
    
    stopDrawing() {
        this.isDrawing = false;
    }
    
    clearCanvas() {
        if (this.ctx) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }
    
    viewImage(image) {
        this.currentImage = image;
        this.showImageModal(image);
    }
    
    showImageModal(image) {
        const modal = document.getElementById('image-modal');
        const content = document.getElementById('image-content');
        
        let modalContent = '';
        
        if (image.image_base64) {
            modalContent = `
                <div class="image-full-view">
                    <img src="${image.image_base64}" alt="${image.title}" class="image-full">
                </div>
            `;
        } else if (image.image_url) {
            modalContent = `
                <div class="image-full-view">
                    <img src="${image.image_url}" alt="${image.title}" class="image-full">
                </div>
            `;
        } else {
            modalContent = `
                <div class="image-text-view">
                    <h3>${image.title}</h3>
                    <pre>${JSON.stringify(image, null, 2)}</pre>
                </div>
            `;
        }
        
        modalContent += `
            <div class="image-info">
                <h3>${image.title}</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Type:</strong>
                        <span class="image-badge image-${image.type}">${image.type}</span>
                    </div>
                    <div class="info-item">
                        <strong>Created:</strong>
                        <span>${new Date(image.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="info-item">
                        <strong>Dimensions:</strong>
                        <span>${image.width || 'N/A'} x ${image.height || 'N/A'}</span>
                    </div>
                </div>
                
                ${image.description ? `
                <div class="image-description">
                    <strong>Description:</strong>
                    <p>${image.description}</p>
                </div>
                ` : ''}
                
                <div class="modal-actions">
                    <button class="btn btn-primary" onclick="imageEditor.downloadImage(imageEditor.currentImage)">
                        <i class="fas fa-download"></i> Download
                    </button>
                    <button class="btn btn-secondary modal-close">
                        <i class="fas fa-times"></i> Close
                    </button>
                </div>
            </div>
        `;
        
        content.innerHTML = modalContent;
        modal.style.display = 'block';
        
        // Add close button event
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
    
    editImage(image) {
        this.currentImage = image;
        this.showEditorModal(image);
    }
    
    showEditorModal(image) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'editor-modal';
        
        modal.innerHTML = `
            <div class="modal-content editor-modal">
                <div class="modal-header">
                    <h3>Edit Image: ${image.title}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="editor-container">
                        <div class="editor-tools">
                            <h4>Tools</h4>
                            <div class="tool-buttons">
                                <button id="tool-brush" class="tool-btn active">
                                    <i class="fas fa-paint-brush"></i> Brush
                                </button>
                                <button id="tool-text" class="tool-btn">
                                    <i class="fas fa-font"></i> Text
                                </button>
                                <button id="tool-shape" class="tool-btn">
                                    <i class="fas fa-shapes"></i> Shapes
                                </button>
                                <button id="tool-filter" class="tool-btn">
                                    <i class="fas fa-sliders-h"></i> Filters
                                </button>
                            </div>
                            
                            <div class="tool-options">
                                <div class="option-group">
                                    <label for="brush-size">Brush Size:</label>
                                    <input type="range" id="brush-size" min="1" max="50" value="5">
                                    <span id="brush-size-value">5</span>
                                </div>
                                
                                <div class="option-group">
                                    <label for="drawing-color">Color:</label>
                                    <input type="color" id="drawing-color" value="#3498db">
                                </div>
                                
                                <div class="option-group">
                                    <label for="opacity">Opacity:</label>
                                    <input type="range" id="opacity" min="0" max="1" step="0.1" value="1">
                                    <span id="opacity-value">1</span>
                                </div>
                            </div>
                            
                            <div class="action-buttons">
                                <button id="btn-clear" class="btn btn-warning">
                                    <i class="fas fa-eraser"></i> Clear
                                </button>
                                <button id="btn-undo" class="btn btn-secondary">
                                    <i class="fas fa-undo"></i> Undo
                                </button>
                                <button id="btn-redo" class="btn btn-secondary">
                                    <i class="fas fa-redo"></i> Redo
                                </button>
                            </div>
                        </div>
                        
                        <div class="editor-canvas-container">
                            <canvas id="image-canvas" width="800" height="600"></canvas>
                        </div>
                        
                        <div class="editor-preview">
                            <h4>Preview</h4>
                            <div class="preview-image" id="preview-image">
                                <img src="${image.image_base64 || image.image_url}" alt="Preview">
                            </div>
                        </div>
                    </div>
                    
                    <div class="editor-save">
                        <button id="btn-save-edited" class="btn btn-success">
                            <i class="fas fa-save"></i> Save Edited Image
                        </button>
                        <button id="btn-cancel-edit" class="btn btn-secondary">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'block';
        
        // Setup canvas for editing
        this.setupCanvas();
        this.loadImageToCanvas(image);
        
        // Setup event listeners
        this.setupEditorEvents(modal, image);
    }
    
    loadImageToCanvas(image) {
        if (!this.canvas || !this.ctx) return;
        
        const img = new Image();
        img.onload = () => {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
        };
        
        if (image.image_base64) {
            img.src = image.image_base64;
        } else if (image.image_url) {
            img.src = image.image_url;
        }
    }
    
    setupEditorEvents(modal, image) {
        // Close button
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.remove();
        });
        
        // Cancel button
        modal.querySelector('#btn-cancel-edit').addEventListener('click', () => {
            modal.remove();
        });
        
        // Clear button
        modal.querySelector('#btn-clear').addEventListener('click', () => {
            this.clearCanvas();
        });
        
        // Brush size slider
        const brushSize = modal.querySelector('#brush-size');
        const brushSizeValue = modal.querySelector('#brush-size-value');
        
        brushSize.addEventListener('input', () => {
            brushSizeValue.textContent = brushSize.value;
        });
        
        // Opacity slider
        const opacity = modal.querySelector('#opacity');
        const opacityValue = modal.querySelector('#opacity-value');
        
        opacity.addEventListener('input', () => {
            opacityValue.textContent = opacity.value;
            this.ctx.globalAlpha = parseFloat(opacity.value);
        });
        
        // Save edited image
        modal.querySelector('#btn-save-edited').addEventListener('click', () => {
            this.saveEditedImage(image);
            modal.remove();
        });
    }
    
    saveEditedImage(originalImage) {
        if (!this.canvas) return;
        
        // Get edited image as base64
        const editedImageData = this.canvas.toDataURL('image/png');
        
        // Create new image object
        const editedImage = {
            ...originalImage,
            image_base64: editedImageData,
            edited: true,
            edited_at: new Date().toISOString(),
            original_id: originalImage.id
        };
        
        // Add to images array
        this.images.unshift(editedImage);
        this.renderImageGrid();
        this.saveToLocalStorage();
        
        this.showNotification('Image edited and saved successfully!', 'success');
    }
    
    downloadImage(image) {
        if (image.image_base64) {
            // Download as image
            const link = document.createElement('a');
            link.href = image.image_base64;
            link.download = `${image.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else if (image.image_url) {
            // Download from URL
            fetch(image.image_url)
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `${image.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.png`;
                    document.body.appendChild(link);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(link);
                });
        }
        
        this.showNotification('Image downloaded successfully!', 'success');
    }
    
    deleteImage(index) {
        if (confirm('Are you sure you want to delete this image?')) {
            this.images.splice(index, 1);
            this.renderImageGrid();
            this.saveToLocalStorage();
            
            // Also delete from server
            this.deleteFromServer(index);
            
            this.showNotification('Image deleted successfully!', 'success');
        }
    }
    
    deleteFromServer(index) {
        const image = this.images[index];
        if (image && image.id) {
            fetch(`/api/images/${image.id}`, {
                method: 'DELETE'
            }).catch(error => console.error('Error deleting from server:', error));
        }
    }
    
    saveToLocalStorage() {
        localStorage.setItem('master_images', JSON.stringify(this.images));
    }
    
    setupEventListeners() {
        // Generate image button
        const generateBtn = document.getElementById('generate-image-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateImage());
        }
        
        // Create new image button
        const createBtn = document.getElementById('create-new-image');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.showImageCreator());
        }
        
        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            const modal = document.getElementById('image-modal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
            
            const editorModal = document.getElementById('editor-modal');
            if (editorModal && event.target === editorModal) {
                editorModal.remove();
            }
        });
    }
    
    generateImage() {
        const description = document.getElementById('image-description').value;
        const style = document.getElementById('image-style').value;
        
        if (!description.trim()) {
            this.showNotification('Please enter image description', 'warning');
            return;
        }
        
        // Show loading
        this.showLoading();
        
        // Send to server
        fetch('/api/images/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                description: description,
                style: style
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add to images array
                this.images.unshift(data.image);
                this.renderImageGrid();
                this.saveToLocalStorage();
                
                // Clear input
                document.getElementById('image-description').value = '';
                
                // Show success
                this.showNotification('Image created successfully!', 'success');
                
                // Show modal
                this.viewImage(data.image);
            } else {
                this.showNotification(data.error || 'Failed to create image', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Network error. Please try again.', 'error');
        })
        .finally(() => {
            this.hideLoading();
        });
    }
    
    showImageCreator() {
        // Show/hide image creator section
        const creator = document.querySelector('.image-creator');
        if (creator) {
            creator.style.display = creator.style.display === 'none' ? 'block' : 'none';
        }
    }
    
    showLoading() {
        const button = document.getElementById('generate-image-btn');
        if (button) {
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            button.disabled = true;
        }
    }
    
    hideLoading() {
        const button = document.getElementById('generate-image-btn');
        if (button) {
            button.innerHTML = '<i class="fas fa-paint-brush"></i> Generate Image';
            button.disabled = false;
        }
    }
    
    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">&times;</button>
        `;
        
        document.body.appendChild(notification);
        
        // Add close functionality
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
}

// Initialize image editor
window.imageEditor = new ImageEditor();