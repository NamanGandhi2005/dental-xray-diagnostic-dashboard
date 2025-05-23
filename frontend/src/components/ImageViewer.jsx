import React, { useEffect, useRef, useState } from 'react';
import './ImageViewer.css';

function ImageViewer({ imageSrc, annotations }) {
  const canvasRef = useRef(null);
  const imageRef = useRef(null);
  const containerRef = useRef(null); 
  const [imageDimensions, setImageDimensions] = useState({ naturalWidth: 0, naturalHeight: 0, displayWidth: 0, displayHeight: 0 });

  useEffect(() => {
    const image = imageRef.current;
    const canvas = canvasRef.current;
    const container = containerRef.current;

    if (!image || !canvas || !imageSrc || !container) return;

    const drawAnnotations = () => {
      if (!image.complete || image.naturalWidth === 0) return; 

      const displayWidth = image.clientWidth;
      const displayHeight = image.clientHeight;
      
      if (imageDimensions.naturalWidth !== image.naturalWidth || 
          imageDimensions.naturalHeight !== image.naturalHeight ||
          imageDimensions.displayWidth !== displayWidth ||
          imageDimensions.displayHeight !== displayHeight) {
        setImageDimensions({
          naturalWidth: image.naturalWidth,
          naturalHeight: image.naturalHeight,
          displayWidth: displayWidth,
          displayHeight: displayHeight,
        });
      }

      canvas.width = displayWidth;
      canvas.height = displayHeight;
      
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height); 

      if (annotations && annotations.length > 0) {
        const scaleX = displayWidth / image.naturalWidth;
        const scaleY = displayHeight / image.naturalHeight;

        annotations.forEach((ann) => { 
          const boxX = (ann.x - ann.width / 2) * scaleX;
          const boxY = (ann.y - ann.height / 2) * scaleY;
          const boxWidth = ann.width * scaleX;
          const boxHeight = ann.height * scaleY;

          ctx.strokeStyle = '#FF0000'; 
          ctx.lineWidth = 2;
          ctx.strokeRect(boxX, boxY, boxWidth, boxHeight);

          
          const text = `${ann.class} (${(ann.confidence * 100).toFixed(0)}%)`;
          ctx.font = 'bold 14px Arial';
          const textMetrics = ctx.measureText(text);
          const textWidth = textMetrics.width;
          const textHeight = 14;

          let rectX = boxX;
          let rectY = boxY - textHeight - 4;
          let textX = boxX + 2;
          let textY = boxY - 4; 

         
          if (rectY < 0) {
            rectY = boxY + 2; 
            textY = boxY + textHeight; 
          }

          
          
          
          
          if (rectX + textWidth + 4 > canvas.width) {
            rectX = canvas.width - textWidth - 4;
            textX = rectX + 2;
          }
          
          if (rectX < 0) {
            rectX = 0;
            textX = rectX + 2;
          }
          
          ctx.fillStyle = '#FF0000'; 
          ctx.fillRect(rectX, rectY, textWidth + 4, textHeight + 4);
          
          ctx.fillStyle = 'white'; 
          ctx.fillText(text, textX, textY);
          
        });
      }
    };
    
    const handleLoad = () => {
        drawAnnotations();
    };

    if (image.complete && image.naturalWidth > 0) {
      handleLoad(); 
    } else {
      image.addEventListener('load', handleLoad);
    }

    const resizeObserver = new ResizeObserver(drawAnnotations);
    if (container) {
      resizeObserver.observe(container);
    }
    
    return () => {
      if (image) {
        image.removeEventListener('load', handleLoad);
      }
      if (container) {
        resizeObserver.unobserve(container);
      }
      resizeObserver.disconnect();
    };
  }, [imageSrc, annotations, imageDimensions]); 

  if (!imageSrc) {
    return null; 
  }

  return (
    <div ref={containerRef} className="image-viewer-container">
      <img 
        ref={imageRef} 
        src={imageSrc} 
        alt="Dental X-ray" 
        className="xray-image"
      />
      <canvas 
        ref={canvasRef} 
        className="annotation-canvas"
      />
    </div>
  );
}

export default ImageViewer;