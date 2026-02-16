import { useState, useEffect } from "react";
import { ArrowLeft } from "lucide-react";
import { useWorkflowStore } from "../../../store/workflowStore";

interface Operation {
  id: string;
  name: string;
  description: string;
  type: "trigger" | "action";
  input_schema?: any[];
}

interface IntegrationDetail {
  id: string;
  name: string;
  icon: string;
  triggers: Operation[];
  actions: Operation[];
}

/**
 * OperationPicker - Shows available operations (triggers/actions) for selected integration
 */
export default function OperationPicker() {
  const { selectedIntegration, nodes, addNode, selectNode } =
    useWorkflowStore();
  const [integrationDetail, setIntegrationDetail] =
    useState<IntegrationDetail | null>(null);
  const [loading, setLoading] = useState(true);

  // Determine if we need triggers or actions
  const hasTrigger = nodes.some((n) => n.data.stepType === "trigger");
  const needsType = hasTrigger ? "action" : "trigger";

  useEffect(() => {
    if (!selectedIntegration) return;

    const fetchIntegrationDetail = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/integrations/${selectedIntegration.id}`,
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
  }, [selectedIntegration]);

  const handleBack = () => {
    selectNode(null); // Goes back to integration picker
  };

  const handleSelectOperation = (operation: Operation) => {
    if (!selectedIntegration) return;

    // Add the node with this operation
    addNode({
      stepOrder: nodes.filter((n) => n.type !== "addStepNode").length + 1,
      stepType: needsType,
      integrationId: selectedIntegration.id,
      operationId: operation.id,
      connectionId: null,
      config: {},
      label: operation.name,
      icon: selectedIntegration.icon,
      integrationName: selectedIntegration.name,
    });

    // Close panel after adding (goes to empty state)
    selectNode(null);
  };

  if (!selectedIntegration) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <p className="text-gray-400 text-sm">No integration selected</p>
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

  const operations = integrationDetail
    ? needsType === "trigger"
      ? integrationDetail.triggers
      : integrationDetail.actions
    : [];

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={handleBack}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-200 transition-colors mb-3"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to integrations
        </button>

        <div className="flex items-center gap-3">
          <div className="text-3xl">{selectedIntegration.icon}</div>
          <div>
            <h3 className="text-lg font-semibold text-gray-200">
              {selectedIntegration.name}
            </h3>
            <p className="text-xs text-gray-400">Choose a {needsType}</p>
          </div>
        </div>
      </div>

      {/* Operations List */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-2">
          {operations.map((operation) => (
            <button
              key={operation.id}
              onClick={() => handleSelectOperation(operation)}
              className="
                w-full p-4 rounded-lg border-2 border-gray-700 bg-gray-750
                hover:border-indigo-500 hover:bg-gray-700
                transition-all text-left group
              "
            >
              <div className="font-semibold text-gray-200 text-sm group-hover:text-indigo-400 transition-colors">
                {operation.name}
              </div>
              {operation.description && (
                <div className="text-xs text-gray-500 mt-1">
                  {operation.description}
                </div>
              )}
            </button>
          ))}
        </div>

        {operations.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-sm">
              No {needsType}s available for this integration
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
