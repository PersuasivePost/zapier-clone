import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { Plus } from "lucide-react";
import { useWorkflowStore } from "../../store/workflowStore";

function AddStepNode() {
  const openIntegrationPicker = useWorkflowStore(
    (state) => state.openIntegrationPicker,
  );

  return (
    <div className="relative">
      {/* Input handle at top */}
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-gray-400 !w-3 !h-3 !border-2 !border-white"
      />

      <button
        onClick={() => openIntegrationPicker()}
        className="
          px-6 py-3 rounded-lg border-2 border-dashed border-gray-400
          bg-white hover:bg-gray-50 hover:border-gray-600
          transition-all min-w-[200px] group
        "
      >
        <div className="flex items-center justify-center gap-2 text-gray-600 group-hover:text-gray-800">
          <Plus className="w-5 h-5" />
          <span className="font-medium">Add Step</span>
        </div>
      </button>
    </div>
  );
}

export default memo(AddStepNode);
