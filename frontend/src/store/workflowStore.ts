import { create } from "zustand";
import {
  type Node,
  type Edge,
  applyNodeChanges,
  applyEdgeChanges,
  type NodeChange,
  type EdgeChange,
} from "@xyflow/react";

// ============= TYPES =============

export interface StepConfig {
  [key: string]: any;
}

export interface NodeData extends Record<string, unknown> {
  stepId?: string; // API step ID (when loaded from existing workflow)
  stepOrder: number;
  stepType: "trigger" | "action" | "filter";
  integrationId: string;
  operationId: string;
  connectionId: string | null;
  config: StepConfig;
  label: string;
  icon: string;
  integrationName: string;
}

export interface WorkflowInfo {
  id: string | null;
  name: string;
  status: "draft" | "active" | "paused";
  webhook_token: string | null;
}

export interface Integration {
  id: string;
  name: string;
  icon: string;
  triggers: Operation[];
  actions: Operation[];
}

export interface Operation {
  id: string;
  name: string;
  description: string;
  type: "trigger" | "action";
  input_schema: Record<string, any>;
}

type PanelMode =
  | "empty"
  | "selectIntegration"
  | "selectOperation"
  | "configure";

// ============= STORE INTERFACE =============

interface WorkflowState {
  // State
  workflow: WorkflowInfo;
  nodes: Node<NodeData>[];
  edges: Edge[];
  selectedNodeId: string | null;
  integrations: Integration[];
  selectedIntegration: Integration | null;
  panelMode: PanelMode;
  isSaving: boolean;
  isLoading: boolean;
  hasUnsavedChanges: boolean;

  // Workflow Actions
  loadWorkflow: (workflowId: string, token: string) => Promise<void>;
  createNewWorkflow: () => void;
  saveWorkflow: (token: string) => Promise<void>;
  setWorkflowName: (name: string) => void;

  // Node Actions
  addNode: (nodeData: NodeData) => void;
  removeNode: (nodeId: string) => void;
  selectNode: (nodeId: string | null) => void;
  deselectNode: () => void;
  updateNodeConfig: (nodeId: string, config: StepConfig) => void;

  // Panel Actions
  openIntegrationPicker: () => void;
  selectIntegration: (integration: Integration) => void;
  selectOperation: (operation: Operation) => void;

  // Integration Actions
  fetchIntegrations: () => Promise<void>;

  // React Flow handlers
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;

  // Legacy (keep for compatibility)
  setWorkflow: (workflow: WorkflowInfo) => void;
  setNodes: (nodes: Node<NodeData>[]) => void;
  setEdges: (edges: Edge[]) => void;
}

// ============= INITIAL STATE =============

const initialWorkflow: WorkflowInfo = {
  id: null,
  name: "New Workflow",
  status: "draft",
  webhook_token: null,
};

// ============= UTILITY FUNCTIONS =============

// Convert API steps to React Flow nodes
function stepsToNodes(
  steps: any[],
  integrations: Integration[],
): { nodes: Node<NodeData>[]; edges: Edge[] } {
  const nodes: Node<NodeData>[] = [];
  const edges: Edge[] = [];

  steps.forEach((step, index) => {
    // Find integration to get icon and name
    const integration = integrations.find((i) => i.id === step.integration_id);
    const operation = [
      ...(integration?.triggers || []),
      ...(integration?.actions || []),
    ].find((op) => op.id === step.operation_id);

    const nodeId = `node-${step.id || index}`;

    // Create node
    nodes.push({
      id: nodeId,
      type: step.step_type === "trigger" ? "triggerNode" : "actionNode",
      position: step.ui_metadata?.position || { x: 250, y: index * 150 + 50 },
      data: {
        stepId: step.id,
        stepOrder: step.order,
        stepType: step.step_type,
        integrationId: step.integration_id,
        operationId: step.operation_id,
        connectionId: step.connection_id,
        config: step.config || {},
        label: operation?.name || step.ui_metadata?.label || "Unknown",
        icon: integration?.icon || step.ui_metadata?.icon || "⚙️",
        integrationName:
          integration?.name || step.ui_metadata?.integrationName || "Unknown",
      },
    });

    // Create edge from previous node
    if (index > 0) {
      const prevNodeId = `node-${steps[index - 1].id || index - 1}`;
      edges.push({
        id: `edge-${prevNodeId}-${nodeId}`,
        source: prevNodeId,
        target: nodeId,
        animated: true,
      });
    }
  });

  return { nodes, edges };
}

// Convert React Flow nodes to API steps
function nodesToSteps(nodes: Node<NodeData>[]): any[] {
  return nodes
    .sort((a, b) => a.position.y - b.position.y) // Sort by vertical position
    .map((node, index) => ({
      id: node.data.stepId,
      order: index + 1,
      step_type: node.data.stepType,
      integration_id: node.data.integrationId,
      operation_id: node.data.operationId,
      connection_id: node.data.connectionId,
      config: node.data.config,
      ui_metadata: {
        position: node.position,
        label: node.data.label,
        icon: node.data.icon,
        integrationName: node.data.integrationName,
      },
    }));
}

// ============= STORE IMPLEMENTATION =============

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  // Initial State
  workflow: initialWorkflow,
  nodes: [],
  edges: [],
  selectedNodeId: null,
  integrations: [],
  selectedIntegration: null,
  panelMode: "empty",
  isSaving: false,
  isLoading: false,
  hasUnsavedChanges: false,

  // ========== WORKFLOW ACTIONS ==========

  loadWorkflow: async (workflowId: string, token: string) => {
    set({ isLoading: true });
    try {
      const response = await fetch(
        `http://localhost:8000/api/workflows/${workflowId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      if (!response.ok) throw new Error("Failed to load workflow");

      const data = await response.json();
      const { integrations } = get();

      // Convert steps to nodes
      const { nodes, edges } = stepsToNodes(data.steps || [], integrations);

      set({
        workflow: {
          id: data.id,
          name: data.name,
          status: data.status,
          webhook_token: data.webhook_token,
        },
        nodes,
        edges,
        hasUnsavedChanges: false,
        isLoading: false,
      });
    } catch (error) {
      console.error("Error loading workflow:", error);
      set({ isLoading: false });
      throw error;
    }
  },

  createNewWorkflow: () => {
    set({
      workflow: initialWorkflow,
      nodes: [],
      edges: [],
      selectedNodeId: null,
      panelMode: "empty",
      hasUnsavedChanges: false,
    });
  },

  saveWorkflow: async (token: string) => {
    const { workflow, nodes } = get();
    set({ isSaving: true });

    try {
      const steps = nodesToSteps(nodes);
      const payload = {
        name: workflow.name,
        status: workflow.status,
        steps,
      };

      const url = workflow.id
        ? `http://localhost:8000/api/workflows/${workflow.id}`
        : "http://localhost:8000/api/workflows";

      const method = workflow.id ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error("Failed to save workflow");

      const saved = await response.json();

      set({
        workflow: {
          id: saved.id,
          name: saved.name,
          status: saved.status,
          webhook_token: saved.webhook_token,
        },
        hasUnsavedChanges: false,
        isSaving: false,
      });

      return saved;
    } catch (error) {
      console.error("Error saving workflow:", error);
      set({ isSaving: false });
      throw error;
    }
  },

  setWorkflowName: (name: string) => {
    set((state) => ({
      workflow: { ...state.workflow, name },
      hasUnsavedChanges: true,
    }));
  },

  // ========== NODE ACTIONS ==========

  addNode: (nodeData: NodeData) => {
    const { nodes, edges } = get();
    const nodeId = `node-${Date.now()}`;
    const lastNode = nodes[nodes.length - 1];

    // Calculate position
    const yPosition = lastNode ? lastNode.position.y + 150 : 50;

    const newNode: Node<NodeData> = {
      id: nodeId,
      type: nodeData.stepType === "trigger" ? "triggerNode" : "actionNode",
      position: { x: 250, y: yPosition },
      data: {
        ...nodeData,
        stepOrder: nodes.length + 1,
      },
    };

    // Create edge from last node
    const newEdge: Edge | null = lastNode
      ? {
          id: `edge-${lastNode.id}-${nodeId}`,
          source: lastNode.id,
          target: nodeId,
          animated: true,
        }
      : null;

    set({
      nodes: [...nodes, newNode],
      edges: newEdge ? [...edges, newEdge] : edges,
      selectedNodeId: nodeId,
      panelMode: "configure",
      selectedIntegration: null,
      hasUnsavedChanges: true,
    });
  },

  removeNode: (nodeId: string) => {
    const { nodes, edges } = get();

    // Don't allow deleting the trigger
    const nodeToDelete = nodes.find((n) => n.id === nodeId);
    if (nodeToDelete?.data.stepType === "trigger") {
      alert("Cannot delete the trigger step");
      return;
    }

    // Remove node and recalculate step orders
    const remainingNodes = nodes
      .filter((node) => node.id !== nodeId)
      .map((node, index) => ({
        ...node,
        data: { ...node.data, stepOrder: index + 1 },
      }));

    set({
      nodes: remainingNodes,
      edges: edges.filter(
        (edge) => edge.source !== nodeId && edge.target !== nodeId,
      ),
      selectedNodeId: null,
      panelMode: "empty",
      hasUnsavedChanges: true,
    });
  },

  selectNode: (nodeId: string | null) => {
    set({
      selectedNodeId: nodeId,
      panelMode: nodeId ? "configure" : "empty",
    });
  },

  deselectNode: () => {
    set({
      selectedNodeId: null,
      panelMode: "empty",
    });
  },

  updateNodeConfig: (nodeId: string, config: StepConfig) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, config } } : node,
      ),
      hasUnsavedChanges: true,
    });
  },

  // ========== PANEL ACTIONS ==========

  openIntegrationPicker: () => {
    set({
      panelMode: "selectIntegration",
      selectedNodeId: null,
      selectedIntegration: null,
    });
  },

  selectIntegration: (integration: Integration) => {
    set({
      selectedIntegration: integration,
      panelMode: "selectOperation",
    });
  },

  selectOperation: (operation: Operation) => {
    const { selectedIntegration, nodes } = get();
    if (!selectedIntegration) return;

    // Determine if this is a trigger or action
    const hasTrigger = nodes.some((n) => n.data.stepType === "trigger");
    const stepType = hasTrigger ? "action" : "trigger";

    // Create the node
    get().addNode({
      stepOrder: nodes.length + 1,
      stepType,
      integrationId: selectedIntegration.id,
      operationId: operation.id,
      connectionId: null,
      config: {},
      label: operation.name,
      icon: selectedIntegration.icon,
      integrationName: selectedIntegration.name,
    });
  },

  // ========== INTEGRATION ACTIONS ==========

  fetchIntegrations: async () => {
    try {
      const response = await fetch("http://localhost:8000/api/integrations");
      if (!response.ok) throw new Error("Failed to fetch integrations");

      const data = await response.json();
      set({ integrations: data });
    } catch (error) {
      console.error("Error fetching integrations:", error);
    }
  },

  // ========== REACT FLOW HANDLERS ==========

  onNodesChange: (changes: NodeChange[]) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes) as Node<NodeData>[],
      hasUnsavedChanges: true,
    });
  },

  onEdgesChange: (changes: EdgeChange[]) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },

  // ========== LEGACY COMPATIBILITY ==========

  setWorkflow: (workflow: WorkflowInfo) => set({ workflow }),
  setNodes: (nodes: Node<NodeData>[]) => set({ nodes }),
  setEdges: (edges: Edge[]) => set({ edges }),
}));
