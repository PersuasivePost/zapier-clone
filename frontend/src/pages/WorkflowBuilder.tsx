import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ReactFlowProvider } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { ArrowLeft, Save, Play, Loader2, Power, PowerOff } from "lucide-react";

import { useWorkflowStore } from "../store/workflowStore";
import { WorkflowCanvas, ConfigPanel } from "../components/workflow";

export default function WorkflowBuilder() {
  return (
    <ReactFlowProvider>
      <WorkflowBuilderContent />
    </ReactFlowProvider>
  );
}

function WorkflowBuilderContent() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toggling, setToggling] = useState(false);

  const {
    workflow,
    hasUnsavedChanges,
    integrations,
    loadWorkflow: loadWorkflowFromStore,
    saveWorkflow,
    setWorkflowName,
  } = useWorkflowStore();

  // Load workflow data and integrations on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("token") || "";

        // Load integrations if not already loaded
        if (integrations.length === 0) {
          const response = await fetch(
            "http://localhost:8000/api/integrations",
            {
              headers: { Authorization: `Bearer ${token}` },
            },
          );
          if (response.ok) {
            const data = await response.json();
            useWorkflowStore.setState({ integrations: data });
          }
        }

        // Load workflow if editing existing
        if (id && id !== "new") {
          await loadWorkflowFromStore(id, token);
        }
      } catch (error) {
        console.error("Error loading data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [id, loadWorkflowFromStore]);

  const handleSave = async () => {
    try {
      setSaving(true);
      const token = localStorage.getItem("token") || "";
      await saveWorkflow(token);

      // Show success notification
      alert("Workflow saved successfully! ✅");
      useWorkflowStore.setState({ hasUnsavedChanges: false });

      // If creating new workflow, reload to get the ID
      if (!workflow.id && id === "new") {
        window.location.reload();
      }
    } catch (error) {
      console.error("Error saving workflow:", error);
      alert("Failed to save workflow. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleToggleStatus = async () => {
    if (!workflow.id) {
      alert("Please save the workflow first");
      return;
    }

    try {
      setToggling(true);
      const token = localStorage.getItem("token") || "";
      const response = await fetch(
        `http://localhost:8000/api/workflows/${workflow.id}/toggle`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      if (!response.ok) throw new Error("Failed to toggle workflow");

      const updated = await response.json();
      useWorkflowStore.setState({
        workflow: { ...workflow, status: updated.status },
      });

      alert(
        `Workflow ${updated.status === "active" ? "activated" : "paused"}!`,
      );
    } catch (error) {
      console.error("Error toggling workflow:", error);
      alert("Failed to toggle workflow status");
    } finally {
      setToggling(false);
    }
  };

  const handleBack = () => {
    if (hasUnsavedChanges) {
      if (confirm("You have unsaved changes. Leave anyway?")) {
        navigate("/dashboard");
      }
    } else {
      navigate("/dashboard");
    }
  };

  const handleTest = async () => {
    if (!workflow.webhook_token) {
      alert("Save the workflow first to get a webhook URL");
      return;
    }

    const webhookUrl = `http://localhost:8000/api/webhooks/${workflow.webhook_token}`;

    const testData = {
      message: "Test from builder",
      timestamp: new Date().toISOString(),
    };

    try {
      const response = await fetch(webhookUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(testData),
      });

      if (response.ok) {
        alert("Test workflow triggered! Check execution history.");
      } else {
        alert("Failed to trigger workflow");
      }
    } catch (error) {
      console.error("Error testing workflow:", error);
      alert("Failed to trigger workflow");
    }
  };

  // Show loading state
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-indigo-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading workflow...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Header */}
      <div className="h-16 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <button
            onClick={handleBack}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-200"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>

          <input
            type="text"
            value={workflow.name}
            onChange={(e) => {
              setWorkflowName(e.target.value);
              useWorkflowStore.setState({ hasUnsavedChanges: true });
            }}
            placeholder="Untitled Workflow"
            className="text-xl font-semibold bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded px-2 py-1 text-gray-200 placeholder-gray-500"
          />

          <span
            className={`
            px-2 py-1 rounded text-xs font-medium
            ${
              workflow.status === "active"
                ? "bg-green-500/20 text-green-400"
                : workflow.status === "paused"
                  ? "bg-yellow-500/20 text-yellow-400"
                  : "bg-gray-700 text-gray-400"
            }
          `}
          >
            {workflow.status}
          </span>

          {hasUnsavedChanges && (
            <span className="text-xs text-orange-400">• Unsaved changes</span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {workflow.id && (
            <button
              onClick={handleToggleStatus}
              disabled={toggling}
              className={`
                px-4 py-2 rounded-lg transition-colors font-medium flex items-center gap-2 border text-sm
                ${
                  workflow.status === "active"
                    ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/30 hover:bg-yellow-500/20"
                    : "bg-green-500/10 text-green-400 border-green-500/30 hover:bg-green-500/20"
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            >
              {toggling ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : workflow.status === "active" ? (
                <PowerOff className="w-4 h-4" />
              ) : (
                <Power className="w-4 h-4" />
              )}
              {workflow.status === "active" ? "Pause" : "Activate"}
            </button>
          )}

          <button
            onClick={handleTest}
            className="px-4 py-2 bg-indigo-500/10 text-indigo-400 rounded-lg hover:bg-indigo-500/20 transition-colors font-medium flex items-center gap-2 border border-indigo-500/30 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!workflow.id}
          >
            <Play className="w-4 h-4" />
            Test
          </button>

          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium flex items-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Canvas */}
        <WorkflowCanvas />

        {/* Right Panel */}
        <ConfigPanel />
      </div>
    </div>
  );
}
