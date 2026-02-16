import { ArrowLeft } from "lucide-react";
import { useWorkflowStore } from "../../../store/workflowStore";

/**
 * IntegrationPicker - Shows grid of available integrations
 * Filters based on whether user needs a trigger or action
 */
export default function IntegrationPicker() {
  const { integrations, nodes, selectIntegration, selectNode } =
    useWorkflowStore();

  // Determine if we need a trigger or action
  const hasTrigger = nodes.some((n) => n.data.stepType === "trigger");
  const needsType = hasTrigger ? "action" : "trigger";

  // Filter integrations based on what we need
  const availableIntegrations = integrations.filter((integration) => {
    if (needsType === "trigger") {
      return integration.triggers && integration.triggers.length > 0;
    } else {
      return integration.actions && integration.actions.length > 0;
    }
  });

  const handleBack = () => {
    selectNode(null); // This sets panelMode to "empty"
  };

  const handleSelectIntegration = (integration: any) => {
    selectIntegration(integration);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={handleBack}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-200 transition-colors mb-3"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
        <h3 className="text-lg font-semibold text-gray-200">
          Choose {needsType === "trigger" ? "Trigger" : "Action"}
        </h3>
        <p className="text-xs text-gray-400 mt-1">
          {needsType === "trigger"
            ? "Select an event that starts your workflow"
            : "Select an action to perform"}
        </p>
      </div>

      {/* Integrations Grid */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="grid grid-cols-2 gap-3">
          {availableIntegrations.map((integration) => {
            const count =
              needsType === "trigger"
                ? integration.triggers?.length || 0
                : integration.actions?.length || 0;

            return (
              <button
                key={integration.id}
                onClick={() => handleSelectIntegration(integration)}
                className="
                  p-4 rounded-lg border-2 border-gray-700 bg-gray-750
                  hover:border-indigo-500 hover:bg-gray-700
                  transition-all text-left group
                "
              >
                <div className="text-3xl mb-2">{integration.icon}</div>
                <div className="font-semibold text-gray-200 text-sm group-hover:text-indigo-400 transition-colors">
                  {integration.name}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {count} {needsType}
                  {count !== 1 ? "s" : ""}
                </div>
              </button>
            );
          })}
        </div>

        {availableIntegrations.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-sm">No integrations available</p>
            <p className="text-xs mt-1">
              Try adding integrations to your account
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
