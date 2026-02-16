/**
 * Example: How to Use Custom Nodes in React Flow Workflow Builder
 *
 * This file demonstrates the correct way to set up React Flow with custom nodes.
 * Use this as a reference when building your WorkflowBuilder component.
 */

import { useCallback, useEffect } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  ReactFlowProvider,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { useWorkflowStore } from "../../store/workflowStore";
import { nodeTypes } from "../nodes";

/**
 * STEP 1: Wrap your app (or builder page) in ReactFlowProvider
 * This provides React Flow context to all child components
 */
export function WorkflowBuilderWrapper() {
  return (
    <ReactFlowProvider>
      <WorkflowBuilderInner />
    </ReactFlowProvider>
  );
}

/**
 * STEP 2: The actual builder component
 * This is where you use ReactFlow with your custom nodes
 */
function WorkflowBuilderInner() {
  // Get state and actions from Zustand store
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    selectNode,
    fetchIntegrations,
    loadWorkflow,
  } = useWorkflowStore();

  // Load integrations on mount
  useEffect(() => {
    fetchIntegrations();
  }, [fetchIntegrations]);

  // Load workflow if editing existing one
  useEffect(() => {
    const workflowId: string | null = "some-id"; // Get from URL params
    const token = localStorage.getItem("token");
    if (workflowId && workflowId !== "new" && token) {
      loadWorkflow(workflowId, token);
    }
  }, [loadWorkflow]);

  // Handle node click - select the node for configuration
  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: any) => {
      if (node.type !== "addStepNode") {
        selectNode(node.id);
      }
    },
    [selectNode],
  );

  // Handle connection (when user drags from one handle to another)
  // For now, we prevent manual connections since steps are added via "+ Add Step"
  const onConnect = useCallback(() => {
    // Do nothing - connections are auto-created when adding steps
  }, []);

  return (
    <div style={{ width: "100%", height: "100vh" }}>
      <ReactFlow
        // Pass nodes and edges from store
        nodes={nodes}
        edges={edges}
        // Pass change handlers from store (for dragging, selecting, etc.)
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        // Pass event handlers
        onNodeClick={onNodeClick}
        onConnect={onConnect}
        // CRITICAL: Pass the nodeTypes object
        // This tells React Flow which component to use for each node type
        nodeTypes={nodeTypes}
        // Optional: Visual settings
        fitView
        minZoom={0.5}
        maxZoom={1.5}
      >
        {/* Background grid */}
        <Background color="#e5e7eb" gap={16} />

        {/* Zoom/pan controls */}
        <Controls />

        {/* Mini map */}
        <MiniMap
          nodeColor={(node) => {
            if (node.type === "triggerNode") return "#3b82f6"; // Blue
            if (node.type === "actionNode") return "#a855f7"; // Purple
            return "#9ca3af"; // Gray
          }}
        />
      </ReactFlow>
    </div>
  );
}

/**
 * IMPORTANT NOTES:
 *
 * 1. nodeTypes object:
 *    - Created ONCE in nodes/index.ts
 *    - Don't recreate it on every render
 *    - Maps 'triggerNode' -> TriggerNodeComponent, etc.
 *
 * 2. Node data structure:
 *    When you create a node in the store, it looks like:
 *    {
 *      id: 'node-123',
 *      type: 'triggerNode',  // <-- This matches a key in nodeTypes
 *      position: { x: 250, y: 50 },
 *      data: {
 *        stepOrder: 1,
 *        stepType: 'trigger',
 *        integrationId: 'webhook',
 *        operationId: 'incoming_webhook',
 *        label: 'Incoming Webhook',
 *        icon: '🔗',
 *        integrationName: 'Webhook',
 *        config: {},
 *        ... // all fields from NodeData interface
 *      }
 *    }
 *
 * 3. React Flow automatically:
 *    - Looks at node.type ('triggerNode')
 *    - Finds the component in nodeTypes object
 *    - Renders <TriggerNode data={node.data} selected={node.selected} />
 *
 * 4. The "Add Step" node:
 *    - Is a regular node with type='addStepNode'
 *    - The store should always keep one at the bottom
 *    - When clicked, it calls openIntegrationPicker()
 *
 * 5. Handles (connection points):
 *    - Trigger nodes: Have source handle at bottom (edges go OUT)
 *    - Action nodes: Have target at top (edges come IN) and source at bottom (edges go OUT)
 *    - Add Step node: Has target at top (receives edge from last real step)
 */

export default WorkflowBuilderWrapper;
