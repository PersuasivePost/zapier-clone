import { Zap } from "lucide-react";

/**
 * EmptyPanel - Shown when no node is selected and no action is being taken
 */
export default function EmptyPanel() {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center">
      <div className="w-20 h-20 bg-indigo-500/20 rounded-full flex items-center justify-center mb-4">
        <Zap className="w-10 h-10 text-indigo-400" />
      </div>

      <h3 className="text-lg font-semibold text-gray-200 mb-2">
        Workflow Builder
      </h3>

      <p className="text-sm text-gray-400 max-w-xs">
        Click a step to configure it, or click{" "}
        <span className="text-indigo-400 font-medium">+ Add Step</span> to add a
        new step to your workflow.
      </p>

      <div className="mt-8 p-4 bg-gray-700/50 rounded-lg border border-gray-600 text-left">
        <p className="text-xs text-gray-300 font-medium mb-2">💡 Quick Tip</p>
        <p className="text-xs text-gray-400">
          Every workflow starts with a trigger. Add integrations to automate
          tasks between different services.
        </p>
      </div>
    </div>
  );
}
