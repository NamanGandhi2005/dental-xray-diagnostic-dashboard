import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ImageUpload from './components/ImageUpload';
import ImageViewer from './components/ImageViewer';
import ReportDisplay from './components/ReportDisplay';
import DarkModeToggle from './components/DarkModeToggle'; 
import './App.css'; 


function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const savedMode = localStorage.getItem('darkMode');
    return savedMode ? JSON.parse(savedMode) : false; 
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode(prevMode => !prevMode);
  };
  

  const [fileQueue, setFileQueue] = useState([]);
  const [currentProcessingFile, setCurrentProcessingFile] = useState(null);
  const [results, setResults] = useState([]); 
  const [activeResultIndex, setActiveResultIndex] = useState(null); 
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(''); 

  const handleFilesSelect = (selectedFiles) => {
    setFileQueue(selectedFiles); 
    setResults([]);              
    setActiveResultIndex(null);  
    setCurrentProcessingFile(null); 
    setIsLoading(false);         
    setError('');                
  };

  const processFile = useCallback(async (fileToProcess) => {
    if (!fileToProcess) return;
    setIsLoading(true); 
    setCurrentProcessingFile(fileToProcess);
    setError(''); 
    
    const formData = new FormData();
    formData.append('file', fileToProcess);

    let fileSpecificResult = { 
        id: `${fileToProcess.name}-${Date.now()}-${Math.random()}`,
        fileName: fileToProcess.name, 
        imageSrc: '', 
        annotations: [], 
        report: '', 
        error: '' 
    };

    try {
      const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/diagnose`;
      const response = await axios.post(apiUrl, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const data = response.data;

      if (data.error && !data.converted_image_base64) { 
        fileSpecificResult.error = data.error;
        setError(`Error (file: ${fileToProcess.name}): ${data.error}`); 
      } else {
        if (data.converted_image_base64) {
          fileSpecificResult.imageSrc = `data:image/png;base64,${data.converted_image_base64}`;
        }
        fileSpecificResult.annotations = data.annotations || [];
        fileSpecificResult.report = data.diagnostic_report || 'No report generated.';
        if (data.error) { 
          fileSpecificResult.error = `Note: ${data.error}`;
        }
      }
    } catch (err) {
      let errorMessage = `Failed to process ${fileToProcess.name}.`;
      if (err.response?.data?.detail) {
        errorMessage = `${fileToProcess.name}: ${err.response.data.detail}`;
      } else if (err.message) {
        errorMessage = `${fileToProcess.name}: ${err.message}`;
      }
      fileSpecificResult.error = errorMessage;
      setError(errorMessage); 
    } finally {
      setResults(prevResults => {
        const updatedResults = [...prevResults, fileSpecificResult];
        if (activeResultIndex === null && updatedResults.length === 1) {
            setActiveResultIndex(0);
        }
        return updatedResults;
      });
      setCurrentProcessingFile(null); 
    }
  }, [activeResultIndex]); 
  
  useEffect(() => {
    if (currentProcessingFile === null && fileQueue.length > 0) {
      const nextFile = fileQueue[0];
      setFileQueue(prevQueue => prevQueue.slice(1)); 
      processFile(nextFile); 
    } else if (currentProcessingFile === null && fileQueue.length === 0) {
      setIsLoading(false); 
    }
  }, [currentProcessingFile, fileQueue, processFile]); 


  const activeFileResult = (activeResultIndex !== null && results[activeResultIndex]) 
                           ? results[activeResultIndex] 
                           : null;

  const displayImageSrc = activeFileResult?.imageSrc || '';
  const displayAnnotations = activeFileResult?.annotations || [];
  const displayReport = activeFileResult?.report || '';
  const displayErrorForActiveFile = activeFileResult?.error || '';

  const totalFilesInBatch = results.length + fileQueue.length + (currentProcessingFile ? 1 : 0);

  return (
    <div className="app-container"> 
      <header className="app-header">
        <h1>🦷 Dental X-ray Diagnostic Dashboard</h1>
        <DarkModeToggle isDarkMode={isDarkMode} toggleDarkMode={toggleDarkMode} /> 
      </header>
      
      <main className="dashboard-layout">
        <div className="left-panel">
          <ImageUpload 
            onFilesSelect={handleFilesSelect}
            isLoading={isLoading} 
            currentProcessingFile={currentProcessingFile?.name || ''} 
            totalFiles={totalFilesInBatch} 
            processedCount={results.length} 
          />
          {(error && !displayErrorForActiveFile) && <p className="error-message">{error}</p>}
          {displayErrorForActiveFile && <p className="error-message">Error for {activeFileResult?.fileName}: {displayErrorForActiveFile}</p>}
          
          {isLoading && currentProcessingFile && (
            <div className="loading-container">
              <div className="css-spinner"></div> 
              <p>Processing: {currentProcessingFile.name}, please wait...</p>
            </div>
          )}
          
          { displayImageSrc && (!isLoading || !currentProcessingFile || currentProcessingFile?.name !== activeFileResult?.fileName) && (
            <ImageViewer 
                imageSrc={displayImageSrc} 
                annotations={displayAnnotations} 
             />
          )}

          {!isLoading && !displayImageSrc && !currentProcessingFile && totalFilesInBatch === 0 && (
             <p className="placeholder-text">Upload DICOM image(s) to begin.</p>
          )}
        </div>
        <div className="right-panel">
          <ReportDisplay 
            report={displayReport} 
            isLoading={isLoading && currentProcessingFile?.name === activeFileResult?.fileName && !displayReport && !displayErrorForActiveFile} 
          />
          
          {results.length > 0 && (
            <div className="results-history">
              <h4>
                Processing History ({results.length} / {totalFilesInBatch})
                {fileQueue.length > 0 && ` - ${fileQueue.length} pending`}
              </h4>
              <ul>
                {results.map((res, index) => (
                  <li 
                    key={res.id} 
                    className={`${res.error ? 'result-error' : 'result-success'} ${index === activeResultIndex ? 'active-result' : ''}`}
                    onClick={() => setActiveResultIndex(index)}
                  >
                    <strong>{index + 1}. {res.fileName}</strong>: 
                    <span className="file-status-indicator">
                        {res.error ? ' (Error)' : ' (Processed)'}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </main>
      <footer className="app-footer">
        <p>© {new Date().getFullYear()} Dental Diagnostics Inc. For research purposes only.</p>
      </footer>
    </div>
  );
}

export default App;