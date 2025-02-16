import React, { useRef, useState } from "react";
import { FiTrash2 } from "react-icons/fi";
import { useNavigate } from "react-router-dom"; 

function App() {
  const [blocks, setBlocks] = useState([1, 2, 3]);
  const [selectedBlock, setSelectedBlock] = useState(null);
  const [block1Url, setBlock1Url] = useState("");
  const nodeRefs = useRef([]);
  const navigate = useNavigate(); 

  const handleBlockClick = (blockId) => {
    setSelectedBlock(blockId);
  };

  const deleteBlock = () => {
    if (selectedBlock !== null) {
      setBlocks((prevBlocks) => prevBlocks.filter((block) => block !== selectedBlock));
      setSelectedBlock(null);
    }
  };

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
      console.log("CSRF Test Results:", result.results);

   
      localStorage.setItem("csrfResult", JSON.stringify(result.results));

      navigate("/dashboard");
    } catch (error) {
      console.error('Error during CSRF test:', error);
    }
  };

  return (
    <div className="App">
      {blocks.map((blockId, index) => (
        <div
          key={blockId}
          ref={nodeRefs.current[index]}
          className={`block ${selectedBlock === blockId ? "highlight" : ""}`}
          onClick={() => handleBlockClick(blockId)}
        >
          <h2>Block {blockId}</h2>
          <p>You can drag this block</p>

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

          {blockId === 2 && (
            <div>
              <button onClick={testCSRF}>Test CSRF</button>
            </div>
          )}
        </div>
      ))}

      {/* Trash Icon */}
      <div className="trash-icon" onClick={deleteBlock}>
        <FiTrash2 size={32} color="red" />
      </div>
    </div>
  );
}

export default App;
