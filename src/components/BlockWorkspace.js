import React, { useState } from "react";
import Blockly from "blockly";
import { BlocklyWorkspace } from "react-blockly";

const BlocklyComponent = () => {
  const [code, setCode] = useState("");

  const toolboxCategories = {
    kind: "categoryToolbox",
    contents: [
      { kind: "category", name: "Logic", contents: [{ kind: "block", type: "controls_if" }] },
      { kind: "category", name: "Loops", contents: [{ kind: "block", type: "controls_repeat_ext" }] },
      { kind: "category", name: "Math", contents: [{ kind: "block", type: "math_number" }] },
    ],
  };

  const handleWorkspaceChange = (workspace) => {
    const generatedCode = Blockly.JavaScript.workspaceToCode(workspace);
    setCode(generatedCode);
  };

  return (
    <div>
      <BlocklyWorkspace
        toolboxConfiguration={toolboxCategories}
        className="blockly-workspace"
        onWorkspaceChange={handleWorkspaceChange}
      />
      <h3>Generated Code:</h3>
      <pre>{code}</pre>
    </div>
  );
};

export default BlocklyComponent;
