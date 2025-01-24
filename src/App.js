import React from 'react';
import Draggable from 'react-draggable';  // import react-draggable

function App() {
  return (
    <div className="App">
      <Draggable>
        <div className="block" style={blockStyle}>
          <h2>Block 1</h2>
          <p>คุณสามารถลากบล็อกนี้ได้</p>
        </div>
      </Draggable>

      <Draggable>
        <div className="block" style={blockStyle}>
          <h2>Block 2</h2>
          <p>คุณสามารถลากบล็อกนี้ได้</p>
        </div>
      </Draggable>

      <Draggable>
        <div className="block" style={blockStyle}>
          <h2>Block 3</h2>
          <p>คุณสามารถลากบล็อกนี้ได้</p>
        </div>
      </Draggable>
    </div>
  );
}

const blockStyle = {
  border: '1px solid black',
  padding: '20px',
  marginBottom: '20px',
  cursor: 'move',
  width: '200px',
};

export default App;
