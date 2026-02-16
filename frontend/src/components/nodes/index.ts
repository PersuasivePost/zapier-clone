/**
 * Custom Node Components for React Flow Workflow Builder
 *
 * This file exports all custom node types and the nodeTypes object
 * that React Flow needs to render them.
 */

import { useMemo } from "react";
import TriggerNode from "./TriggerNode";
import ActionNode from "./ActionNode";
import AddStepNode from "./AddStepNode";

/**
 * Node Types Map for React Flow
 *
 * This object maps node type strings to their React components.
 * React Flow uses this to know which component to render for each node.
 *
 * IMPORTANT: This object should be created once and reused.
 * Don't recreate it on every render or React Flow will warn you.
 */
export const nodeTypes = {
  triggerNode: TriggerNode,
  actionNode: ActionNode,
  addStepNode: AddStepNode,
};

/**
 * Hook to get node types (memoized)
 * Use this in your React components to avoid recreating the object
 */
export function useNodeTypes() {
  return useMemo(() => nodeTypes, []);
}

// Export individual components for direct use if needed
export { TriggerNode, ActionNode, AddStepNode };
