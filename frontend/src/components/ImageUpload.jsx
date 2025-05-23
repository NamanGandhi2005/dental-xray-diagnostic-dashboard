import React from 'react';
import './ImageUpload.css';


function ImageUpload({ onFilesSelect, isLoading, currentProcessingFile, totalFiles, processedCount }) {

  const handleFileChange = (event) => {
    const files = event.target.files; 
    if (files && files.length > 0) {
      const validFiles = Array.from(files).filter(file => 
        file.name.toLowerCase().endsWith('.dcm') || file.name.toLowerCase().endsWith('.rvg')
      );
      if (validFiles.length > 0) {
        
        onFilesSelect(validFiles); 
        
      } else if (files.length > 0) {
        alert('No valid .dcm or .rvg files selected.');
      }
    }
    event.target.value = null; 
  };

  

  const displayTotalFiles = totalFiles; 

  return (
    <div className="image-upload-container">
      <input 
        type="file" 
        accept=".dcm,.rvg" 
        onChange={handleFileChange} 
        id="file-upload-input" 
        className="file-upload-input"
        multiple 
        disabled={isLoading && !!currentProcessingFile} 
      />
      <label htmlFor="file-upload-input" className={`file-upload-label ${isLoading && !!currentProcessingFile ? 'disabled' : ''}`}>
        {isLoading && currentProcessingFile 
          ? `Processing: ${currentProcessingFile}` 
          : (displayTotalFiles > 0 && processedCount < displayTotalFiles) 
            ? `Selected ${displayTotalFiles - processedCount} file(s) to analyze` 
            : 'Choose DICOM/RVG File(s)'}
      </label>
      
      {displayTotalFiles > 0 && (
        <div className="upload-status">
          <p>Queue: {displayTotalFiles - processedCount - (isLoading && currentProcessingFile ? 1 : 0) } pending. Processed: {processedCount} / {displayTotalFiles}.</p>
          {isLoading && currentProcessingFile && <p>Analyzing: {currentProcessingFile}</p>}
        </div>
      )}

      {}
      {displayTotalFiles > 0 && processedCount === displayTotalFiles && !isLoading && (
        <p className="success-message">All files processed!</p>
      )}
    </div>
  );
}

export default ImageUpload;