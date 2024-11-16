import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadedImage, setUploadedImage] = useState(null);
    const [resultImage, setResultImage] = useState(null);
    const [vehicleCount, setVehicleCount] = useState(null);
    const [adjustedGreenTime, setAdjustedGreenTime] = useState(null);

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
        setUploadedImage(URL.createObjectURL(event.target.files[0])); 
    };

    const handleUpload = () => {
        if (!selectedFile) return; 

        const formData = new FormData();  
        formData.append('image', selectedFile);

        axios.post('http://localhost:5000/detect_vehicles', formData)
            .then(response => {
                setVehicleCount(response.data.vehicle_count);
                setAdjustedGreenTime(response.data.adjusted_green_time);
                setResultImage(URL.createObjectURL(response.data.result_image));
            })
            .catch(error => {
                console.error('Error uploading file: ', error);  
            });
    };

    const handleGetResultImage = () => {
        axios.get('http://localhost:5000/get_result_image', {
            params: {
                result_image_path: resultImage 
            },
            responseType: 'arraybuffer'
        })
        .then(response => {
            const imageData = Buffer.from(response.data, 'binary').toString('base64');
            setResultImage(`data:image/jpeg;base64,${imageData}`);
        })
        .catch(error => {
            console.error('Error getting result image: ', error);
        });
    };

    return (
        <div className="app-container">
            <h1>Traffic Congestion Management System</h1>

            <div className="upload-section">
                <h2>Upload Image</h2>
                <input type="file" id="fileInput" onChange={handleFileChange} />
                <label htmlFor="fileInput">Choose File</label>
                <div>{selectedFile && <span>{selectedFile.name}</span>}</div>
                <div className="upload-button">
                    <button onClick={handleUpload}>Upload</button>
                </div>
            </div>

            {uploadedImage && <img src={uploadedImage} alt="Uploaded" className="uploaded-image" />}

            {vehicleCount !== null && (
                <div className="result-section">
                    <p>Vehicle Count: {vehicleCount}</p>
                </div>
            )}

            {adjustedGreenTime !== null && (
                <div className="result-section">
                    <p>Adjusted Green Signal Time: {adjustedGreenTime} seconds</p>
                </div>
            )}

            {resultImage && (
                <div className="result-section">
                    <p>Result Image:</p>
                    <img src={resultImage} alt="Result" className="result-image" />
                </div>
            )}

            {resultImage && (
                <div className="result-section">
                    <button onClick={handleGetResultImage}>Get Result Image</button>
                </div>
            )}
        </div>
    );
};

export default App;