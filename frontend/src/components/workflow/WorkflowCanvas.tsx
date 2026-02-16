import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  type Connection,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { useWorkflowStore } from "../../store/workflowStore";
import { nodeTypes } from "../nodes";

export default function WorkflowCanvas() {
  const { nodes, edges, onNodesChange, onEdgesChange, selectNode } =
    useWorkflowStore();

  // Handle node click - select the node for configuration
  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: any) => {
      // Don't select the AddStepNode - it's just a button
      if (node.type !== "addStepNode") {
        selectNode(node.id);
      }
    },
    [selectNode],
  );

  // Handle canvas background click - deselect node
  const onPaneClick = useCallback(() => {
    selectNode(null);
  }, [selectNode]);

  // Handle connections - prevent manual connections for now
  const onConnect = useCallback((params: Connection) => {
    console.log("Connection attempt:", params);
    // For now, we don't allow manual connections
    // All connections are auto-generated based on step order
  }, []);

  return (
    <div className="h-full w-full bg-gray-900">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.5}
        maxZoom={1.5}
        defaultEdgeOptions={{
          animated: true,
          style: { stroke: "#6366f1", strokeWidth: 2 },
        }}
      >
        <Background
          color="#4b5563"
          variant={BackgroundVariant.Dots}
          gap={16}
          size={1}
        />
        <Controls className="bg-gray-800 border-gray-700" />
      </ReactFlow>
    </div>
  );
}
