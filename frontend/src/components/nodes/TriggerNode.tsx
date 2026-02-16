import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import type { NodeData } from "../../store/workflowStore";

interface TriggerNodeProps {
  data: NodeData;
  selected?: boolean;
}

function TriggerNode({ data, selected }: TriggerNodeProps) {
  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[200px]
        ${selected ? "border-blue-500 ring-2 ring-blue-200" : "border-gray-300"}
        hover:shadow-lg transition-shadow cursor-pointer
      `}
    >
      <div className="flex items-center gap-2">
        <span className="text-2xl">{data.icon}</span>
        <div className="flex-1">
          <div className="text-xs text-gray-500 font-medium uppercase">
            Trigger
          </div>
          <div className="font-semibold text-gray-800">
            {data.integrationName}
          </div>
          <div className="text-sm text-gray-600">{data.label}</div>
        </div>
      </div>

      {/* Output handle at bottom */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-blue-500 !w-3 !h-3 !border-2 !border-white"
      />
    </div>
  );
}

export default memo(TriggerNode);
