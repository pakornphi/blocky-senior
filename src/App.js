import React, { useRef, useState } from "react";
import Draggable from "react-draggable";
import { FiTrash2 } from "react-icons/fi";
import "./App.css";

function App() {
  // State variables to manage blocks, selected block, URL from Block 1, and CSRF result
  const [blocks, setBlocks] = useState([1, 2, 3]); // Store the list of blocks
  const [selectedBlock, setSelectedBlock] = useState(null); // Store selected block
  const [block1Url, setBlock1Url] = useState(""); // Store the URL from Block 1
  const [csrfResult, setCsrfResult] = useState(null); // Store the result of CSRF test
  const nodeRefs = useRef([]); // Store refs for each block

  // Function to handle block selection
  const handleBlockClick = (blockId) => {
    setSelectedBlock(blockId);
  };

  // Function to delete block
  const deleteBlock = () => {
    if (selectedBlock !== null) {
      setBlocks((prevBlocks) => prevBlocks.filter((block) => block !== selectedBlock));
      setSelectedBlock(null); // Clear the selection after deletion
    }
  };

  // Function to handle URL input change in Block 1
  const handleUrlChange = (event) => {
    setBlock1Url(event.target.value);
  };

  const testCSRF = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/test-csrf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: block1Url })
      });
  
      const result = await response.json();
      console.log("CSRF Test Results:", result.results);  // Log the results
  
      // Store and display the test results
      setCsrfResult(result.results);  // Assuming `setCsrfResult` updates the state with the results
    } catch (error) {
      console.error('Error during CSRF test:', error);
      setCsrfResult({ error: 'Failed to test CSRF' });
    }
  }; 

  return (
    <div className="App">
      {/* Render draggable blocks */}
      {blocks.map((blockId, index) => (
        <Draggable
          key={blockId}
          nodeRef={(nodeRefs.current[index] = React.createRef())} // Store ref for each block
        >
          <div
            ref={nodeRefs.current[index]}
            className={`block ${selectedBlock === blockId ? "highlight" : ""}`}
            onClick={() => handleBlockClick(blockId)} // Handle block selection on click
          >
            <h2>Block {blockId}</h2>
            <p>You can drag this block</p>

            {/* Block 1 - Input URL */}
            {blockId === 1 && (
              <div>
                <label htmlFor="urlInput">Enter URL:</label>
                <input
                  id="urlInput"
                  type="text"
                  value={block1Url}
                  onChange={handleUrlChange}
                  placeholder="Enter URL here"
                />
              </div>
            )}

            {/* Block 2 - Test CSRF Button */}
            {blockId === 2 && (
              <div>
                <button onClick={testCSRF}>Test CSRF</button>
              </div>
            )}
          </div>
        </Draggable>
      ))}

      {/* Trash icon to delete selected block */}
      <div className="trash-icon" onClick={deleteBlock}>
        <FiTrash2 size={32} color="red" />
      </div>

      {/* Display CSRF Test Result */}
      {csrfResult && (
        <div className="csrf-result">
          <h3>CSRF Test Result:</h3>
          {csrfResult.error ? (
            <p>{csrfResult.error}</p>
          ) : (
            <pre>{JSON.stringify(csrfResult, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
