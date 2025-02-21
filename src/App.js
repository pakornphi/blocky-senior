import React, { useRef, useState } from "react";
import Draggable from "react-draggable";
import { FiTrash2 } from "react-icons/fi";
import "./App.css";

function App() {
  const [blocks, setBlocks] = useState([1, 2, 3]); // Store the list of blocks
  const [selectedBlock, setSelectedBlock] = useState(null); // Store selected block
  const [block1Url, setBlock1Url] = useState(""); // Store the URL from Block 1
  const [csrfResult, setCsrfResult] = useState(null); // Store the result of CSRF test
  const [keyInput, setKeyInput] = useState(""); // Store the key from Block 3
  const nodeRefs = useRef([]); // Store refs for each block

  // Handle block selection
  const handleBlockClick = (blockId) => {
    setSelectedBlock(blockId);
  };

  // Delete selected block
  const deleteBlock = () => {
    if (selectedBlock !== null) {
      setBlocks((prevBlocks) => prevBlocks.filter((block) => block !== selectedBlock));
      setSelectedBlock(null); // Clear the selection after deletion
    }
  };

  // Handle URL input change in Block 1
  const handleUrlChange = (event) => {
    setBlock1Url(event.target.value);
  };

  // Handle Key input change in Block 3
  const handleKeyChange = (event) => {
    setKeyInput(event.target.value);
  };

  // Function to test CSRF (same as before)
  const testCSRF = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/test-csrf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: block1Url }),
      });

      const result = await response.json();
      setCsrfResult(result.results); // Store and display the test results
    } catch (error) {
      console.error("Error during CSRF test:", error);
      setCsrfResult({ error: "Failed to test CSRF" });
    }
  };

  // Function to check for the key in Block 3
  const checkKeyInHead = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/check-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: block1Url, key: keyInput }),
      });

      const result = await response.json();
      setCsrfResult(result); // Assuming the backend returns a result (found or not)
    } catch (error) {
      console.error("Error checking key:", error);
      setCsrfResult({ error: "Failed to check key" });
    }
  };

  return (
    <div className="App">
      {/* Render draggable blocks */}
      {blocks.map((blockId, index) => (
        <Draggable
          key={blockId}
          nodeRef={(nodeRefs.current[index] = React.createRef())}
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

            {/* Block 3 - Input Key */}
            {blockId === 3 && (
              <div>
                <label htmlFor="keyInput">Enter Key:</label>
                <input
                  id="keyInput"
                  type="text"
                  value={keyInput}
                  onChange={handleKeyChange}
                  placeholder="Enter key to search in head"
                />
                <button onClick={checkKeyInHead}>Check Key in Head</button>
              </div>
            )}
          </div>
        </Draggable>
      ))}

      {/* Trash icon to delete selected block */}
      <div className="trash-icon" onClick={deleteBlock}>
        <FiTrash2 size={32} color="red" />
      </div>

      {/* Display CSRF or Key Check Result */}
      {csrfResult && (
        <div className="csrf-result">
          <h3>Test Result:</h3>
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
