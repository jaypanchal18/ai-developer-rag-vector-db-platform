import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [file, setFile] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setError('');
      alert('File uploaded successfully!');
    } catch (err) {
      setError('Error uploading file. Please try again.');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery) {
      setError('Please enter a search query.');
      return;
    }

    try {
      const response = await axios.get(`/api/search?query=${encodeURIComponent(searchQuery)}`);
      setResults(response.data);
      setError('');
    } catch (err) {
      setError('Error fetching search results. Please try again.');
    }
  };

  return (
    <div>
      <h1>Document Upload and Search</h1>
      <div>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload Document</button>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search documents..."
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      <div>
        <h2>Search Results</h2>
        <ul>
          {results.map((result, index) => (
            <li key={index}>{result}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default App;