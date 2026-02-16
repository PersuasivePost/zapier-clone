import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { useWorkflowStore, type NodeData } from "../../store/workflowStore";
import type { Node } from "@xyflow/react";

interface Integration {
  id: string;
  name: string;
  icon: string;
  triggers: Operation[];
  actions: Operation[];
}

interface Operation {
  id: string;
  name: string;
  description: string;
  type: "trigger" | "action";
  input_schema: {
    [key: string]: {
      type: string;
      required: boolean;
      description: string;
    };
  };
}

export default function RightPanel() {
  const {
    selectedNodeId,
    panelMode,
    selectedIntegration,
    nodes,
    integrations,
  } = useWorkflowStore();

  // Panel states
  const selectedNode = nodes.find((n) => n.id === selectedNodeId);
  const showIntegrationPicker = panelMode === "selectIntegration";
  const showOperationPicker = panelMode === "selectOperation";
  const showConfiguration = panelMode === "configure" && selectedNode;

  return (
    <div className="w-96 border-l border-gray-200 bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <h2 className="text-lg font-semibold text-gray-800">
          {showConfiguration && "Configure Step"}
          {showIntegrationPicker && "Choose Integration"}
          {showOperationPicker && "Choose Operation"}
          {panelMode === "empty" && "Workflow Builder"}
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {panelMode === "empty" && <EmptyState />}
        {showIntegrationPicker && (
          <IntegrationPicker integrations={integrations} />
        )}
        {showOperationPicker && (
          <OperationPicker integration={selectedIntegration!} />
        )}
        {showConfiguration && <StepConfiguration node={selectedNode!} />}
      </div>
    </div>
  );
}

// Empty state when nothing is selected
function EmptyState() {
  return (
    <div className="text-center py-12">
      <div className="text-gray-400 mb-2">
        <svg
          className="w-16 h-16 mx-auto"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"
          />
        </svg>
      </div>
      <p className="text-gray-600 font-medium">No step selected</p>
      <p className="text-sm text-gray-500 mt-1">
        Click a step to configure it
        <br />
        or click "+ Add Step" to continue
      </p>
    </div>
  );
}

// Integration picker grid
function IntegrationPicker({ integrations }: { integrations: Integration[] }) {
  const selectIntegration = useWorkflowStore(
    (state) => state.selectIntegration,
  );

  return (
    <div className="grid grid-cols-2 gap-3">
      {integrations.map((integration) => (
        <button
          key={integration.id}
          onClick={() => selectIntegration(integration)}
          className="
            p-4 rounded-lg border-2 border-gray-300 bg-white
            hover:border-blue-400 hover:shadow-md
            transition-all text-left
          "
        >
          <div className="text-3xl mb-2">{integration.icon}</div>
          <div className="font-semibold text-gray-800">{integration.name}</div>
          <div className="text-xs text-gray-500 mt-1">
            {integration.triggers.length} triggers, {integration.actions.length}{" "}
            actions
          </div>
        </button>
      ))}
      {integrations.length === 0 && (
        <div className="col-span-2 text-center py-8 text-gray-500">
          Loading integrations...
        </div>
      )}
    </div>
  );
}

// Operation picker (triggers/actions list)
function OperationPicker({ integration }: { integration: Integration }) {
  const { nodes, addNode, selectNode } = useWorkflowStore();
  const hasTrigger = nodes.some((n) => n.data.stepType === "trigger");

  // Show triggers if no trigger exists, otherwise show actions
  const operations = hasTrigger ? integration.actions : integration.triggers;
  const operationType = hasTrigger ? "action" : "trigger";

  const handleSelectOperation = (operation: Operation) => {
    addNode({
      stepOrder: nodes.length + 1,
      stepType: operationType,
      integrationId: integration.id,
      operationId: operation.id,
      connectionId: null,
      config: {},
      label: operation.name,
      icon: integration.icon,
      integrationName: integration.name,
    });
    selectNode(null); // Close panel after adding
  };

  return (
    <div>
      <button
        onClick={() => selectNode(null)}
        className="text-sm text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-1"
      >
        ← Back to integrations
      </button>

      <div className="space-y-2">
        {operations.map((operation) => (
          <button
            key={operation.id}
            onClick={() => handleSelectOperation(operation)}
            className="
              w-full p-4 rounded-lg border-2 border-gray-300 bg-white
              hover:border-purple-400 hover:shadow-md
              transition-all text-left
            "
          >
            <div className="font-semibold text-gray-800">{operation.name}</div>
            <div className="text-sm text-gray-600 mt-1">
              {operation.description}
            </div>
          </button>
        ))}
      </div>

      {operations.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No {operationType}s available for this integration
        </div>
      )}
    </div>
  );
}

// Step configuration form
function StepConfiguration({ node }: { node: Node<NodeData> }) {
  const [integrationData, setIntegrationData] = useState<Integration | null>(
    null,
  );
  const [config, setConfig] = useState<Record<string, string>>(
    node.data.config || {},
  );
  const { updateNodeConfig, removeNode, selectNode } = useWorkflowStore();

  useEffect(() => {
    // Fetch integration details to get input schema
    fetch(`http://localhost:8000/api/integrations/${node.data.integrationId}`)
      .then((res) => res.json())
      .then((data) => setIntegrationData(data))
      .catch((err) => console.error("Failed to load integration:", err));
  }, [node.data.integrationId]);

  const handleSave = () => {
    updateNodeConfig(node.id, config);
  };

  const handleDelete = () => {
    if (confirm("Delete this step?")) {
      removeNode(node.id);
    }
  };

  const handleClose = () => {
    selectNode(null);
  };

  if (!integrationData) {
    return <div className="text-center py-8 text-gray-500">Loading...</div>;
  }

  // Find the operation to get input schema
  const operation = [
    ...integrationData.triggers,
    ...integrationData.actions,
  ].find((op) => op.id === node.data.operationId);

  if (!operation) {
    return (
      <div className="text-center py-8 text-red-500">Operation not found</div>
    );
  }

  const inputSchema = operation.input_schema || {};

  return (
    <div className="space-y-4">
      <button
        onClick={handleClose}
        className="text-sm text-gray-600 hover:text-gray-700 flex items-center gap-1"
      >
        <X className="w-4 h-4" /> Close
      </button>

      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl">{node.data.icon}</span>
          <div>
            <div className="font-semibold text-gray-800">
              {node.data.integrationName}
            </div>
            <div className="text-sm text-gray-600">{node.data.label}</div>
          </div>
        </div>
      </div>

      {/* Dynamic form based on input schema */}
      <div className="space-y-4">
        {Object.entries(inputSchema).map(
          ([fieldName, fieldConfig]: [string, any]) => (
            <div key={fieldName}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {fieldConfig.description || fieldName}
                {fieldConfig.required && (
                  <span className="text-red-500 ml-1">*</span>
                )}
              </label>

              {fieldConfig.type === "textarea" ? (
                <textarea
                  value={config[fieldName] || ""}
                  onChange={(e) =>
                    setConfig({ ...config, [fieldName]: e.target.value })
                  }
                  onBlur={handleSave}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={4}
                  placeholder={fieldConfig.description}
                />
              ) : (
                <input
                  type="text"
                  value={config[fieldName] || ""}
                  onChange={(e) =>
                    setConfig({ ...config, [fieldName]: e.target.value })
                  }
                  onBlur={handleSave}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder={fieldConfig.description}
                />
              )}

              <p className="text-xs text-gray-500 mt-1">
                Use {"{{trigger.field}}"} to insert dynamic data
              </p>
            </div>
          ),
        )}

        {Object.keys(inputSchema).length === 0 && (
          <div className="text-sm text-gray-500 bg-gray-100 p-3 rounded">
            No configuration needed for this step.
          </div>
        )}
      </div>

      {/* Delete button */}
      {node.data.stepType !== "trigger" && (
        <button
          onClick={handleDelete}
          className="w-full px-4 py-2 bg-red-50 text-red-600 rounded-md hover:bg-red-100 transition-colors font-medium"
        >
          Delete Step
        </button>
      )}
    </div>
  );
}
