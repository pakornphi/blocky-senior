import React, { useRef, useState } from "react";
import Draggable from "react-draggable";
import { FiTrash2 } from "react-icons/fi";
import "./App.css";

function App() {
  const [blocks, setBlocks] = useState([1, 2, 3]); // เก็บรายการของบล็อก
  const [selectedBlock, setSelectedBlock] = useState(null); // เก็บบล็อกที่ถูกเลือก
  const [block1Url, setBlock1Url] = useState(""); // เก็บ URL ของ Block 1
  const nodeRefs = useRef([]); // เก็บ ref สำหรับแต่ละบล็อก

  // ฟังก์ชันสำหรับเลือกบล็อกเมื่อคลิก
  const handleBlockClick = (blockId) => {
    setSelectedBlock(blockId);
  };

  // ฟังก์ชันลบบล็อก
  const deleteBlock = () => {
    if (selectedBlock !== null) {
      setBlocks((prevBlocks) => prevBlocks.filter((block) => block !== selectedBlock));
      setSelectedBlock(null); // ล้างการเลือกหลังจากลบ
    }
  };

  // ฟังก์ชันสำหรับจัดการ URL ของ Block 1
  const handleUrlChange = (event) => {
    setBlock1Url(event.target.value);
  };

  return (
    <div className="App">
      {/* แสดงบล็อก */}
      {blocks.map((blockId, index) => (
        <Draggable
          key={blockId}
          nodeRef={(nodeRefs.current[index] = React.createRef())} // เก็บ ref สำหรับแต่ละบล็อก
        >
          <div
            ref={nodeRefs.current[index]}
            className={`block ${selectedBlock === blockId ? "highlight" : ""}`}
            onClick={() => handleBlockClick(blockId)} // ตั้งค่าบล็อกที่ถูกเลือกเมื่อคลิก
          >
            <h2>Block {blockId}</h2>
            <p>คุณสามารถลากบล็อกนี้ได้</p>

            {/* แสดง input URL เฉพาะ Block 1 */}
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
          </div>
        </Draggable>
      ))}

      {/* ไอคอนถังขยะ */}
      <div className="trash-icon" onClick={deleteBlock}>
        <FiTrash2 size={32} color="red" />
      </div>
    </div>
  );
}

export default App;
