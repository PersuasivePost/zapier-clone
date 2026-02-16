import { useWorkflowStore } from "../../store/workflowStore";
import EmptyPanel from "./panels/EmptyPanel";
import IntegrationPicker from "./panels/IntegrationPicker";
import OperationPicker from "./panels/OperationPicker";
import StepConfigurator from "./panels/StepConfigurator";

/**
 * ConfigPanel - The right sidebar that shows different panels based on panelMode
 *
 * Modes:
 * - empty: Show empty state with instructions
 * - selectIntegration: Show integration picker grid
 * - selectOperation: Show operation (trigger/action) picker
 * - configure: Show step configuration form
 */
export default function ConfigPanel() {
  const { panelMode } = useWorkflowStore();

  return (
    <div className="w-96 bg-gray-800 border-l border-gray-700 flex flex-col overflow-hidden">
      {panelMode === "empty" && <EmptyPanel />}
      {panelMode === "selectIntegration" && <IntegrationPicker />}
      {panelMode === "selectOperation" && <OperationPicker />}
      {panelMode === "configure" && <StepConfigurator />}
    </div>
  );
}
