import { useState, useEffect } from "react";
import { X, Trash2 } from "lucide-react";
import { useWorkflowStore } from "../../../store/workflowStore";
import DynamicForm from "./DynamicForm";

interface FieldSchema {
  key: string;
  label: string;
  type: "string" | "text" | "number" | "boolean" | "select";
  description?: string;
  required?: boolean;
  placeholder?: string;
  options?: { label: string; value: string }[];
}

interface Operation {
  id: string;
  name: string;
  description: string;
  type: "trigger" | "action";
  input_schema: FieldSchema[];
}

interface IntegrationDetail {
  id: string;
  name: string;
  icon: string;
  triggers: Operation[];
  actions: Operation[];
}

/**
 * StepConfigurator - Dynamic form for configuring a step's inputs
 */
export default function StepConfigurator() {
  const { selectedNodeId, nodes, updateNodeConfig, removeNode, selectNode } =
    useWorkflowStore();
  const [integrationDetail, setIntegrationDetail] =
    useState<IntegrationDetail | null>(null);
  const [loading, setLoading] = useState(true);

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);

  useEffect(() => {
    if (!selectedNode) return;

    const fetchIntegrationDetail = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/integrations/${selectedNode.data.integrationId}`,
        );
        if (!response.ok)
          throw new Error("Failed to fetch integration details");
        const data = await response.json();
        setIntegrationDetail(data);
      } catch (error) {
        console.error("Error fetching integration detail:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchIntegrationDetail();
  }, [selectedNode]);

  const handleClose = () => {
    selectNode(null);
  };

  const handleDelete = () => {
    if (!selectedNode) return;
    if (confirm(`Delete this ${selectedNode.data.stepType} step?`)) {
      removeNode(selectedNode.id);
    }
  };

  const handleConfigChange = (newConfig: Record<string, any>) => {
    if (!selectedNode) return;
    updateNodeConfig(selectedNode.id, newConfig);
  };

  if (!selectedNode) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <p className="text-gray-400 text-sm">No step selected</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  // Find the operation to get its input schema
  const operation = integrationDetail
    ? [...integrationDetail.triggers, ...integrationDetail.actions].find(
        (op) => op.id === selectedNode.data.operationId,
      )
    : null;

  const inputSchema = operation?.input_schema || [];

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={handleClose}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-200 transition-colors mb-3"
        >
          <X className="w-4 h-4" />
          Close
        </button>

        <div className="flex items-center gap-3">
          <div className="text-3xl">{selectedNode.data.icon}</div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold text-gray-200">
                {selectedNode.data.integrationName}
              </h3>
              <span
                className={`
                  px-2 py-0.5 rounded text-xs font-medium
                  ${
                    selectedNode.data.stepType === "trigger"
                      ? "bg-blue-500/20 text-blue-400"
                      : "bg-purple-500/20 text-purple-400"
                  }
                `}
              >
                {selectedNode.data.stepType}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              {selectedNode.data.label}
            </p>
          </div>
        </div>
      </div>

      {/* Configuration Form */}
      <div className="flex-1 overflow-y-auto p-4">
        {inputSchema.length > 0 ? (
          <>
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-gray-300 mb-1">
                Configuration
              </h4>
              <p className="text-xs text-gray-500">
                Configure the inputs for this step. You can use template
                variables like{" "}
                <code className="text-indigo-400">{"{{trigger.field}}"}</code>{" "}
                to reference data from previous steps.
              </p>
            </div>

            <DynamicForm
              schema={inputSchema}
              values={selectedNode.data.config || {}}
              onChange={handleConfigChange}
            />
          </>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p className="text-sm">No configuration required</p>
            <p className="text-xs mt-1">This step has no input fields</p>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="p-4 border-t border-gray-700">
        <button
          onClick={handleDelete}
          className="
            w-full px-4 py-2 rounded-lg
            bg-red-500/10 text-red-400 border-2 border-red-500/30
            hover:bg-red-500/20 hover:border-red-500/50
            transition-all font-medium text-sm
            flex items-center justify-center gap-2
          "
        >
          <Trash2 className="w-4 h-4" />
          Delete Step
        </button>
      </div>
    </div>
  );
}
