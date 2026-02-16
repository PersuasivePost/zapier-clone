import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Zap,
  LogOut,
  Plus,
  Edit,
  Power,
  PowerOff,
  Trash2,
  Clock,
  Loader2,
  CircleDot,
} from "lucide-react";

interface User {
  id: string;
  email: string;
  full_name: string;
}

interface Workflow {
  id: string;
  name: string;
  status: "draft" | "active" | "paused";
  created_at: string;
  updated_at: string;
  webhook_token: string | null;
  last_run_at: string | null;
  total_runs: number;
  successful_runs: number;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserInfo = async () => {
      const token = localStorage.getItem("token");

      console.log(
        "🔍 Dashboard - Checking token:",
        token ? `${token.substring(0, 20)}...` : null,
      );

      if (!token) {
        console.warn("⚠️ No token found, redirecting to login");
        navigate("/login");
        return;
      }

      try {
        console.log("📡 Fetching user info from /api/auth/me");
        const response = await fetch("http://localhost:8000/api/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        console.log("📡 Response status:", response.status);

        if (response.ok) {
          const userData = await response.json();
          console.log("✅ User data received:", userData);
          setUser(userData);

          // Fetch workflows
          await fetchWorkflows(token);
        } else {
          const errorText = await response.text();
          console.error(
            "❌ Token invalid or expired:",
            response.status,
            errorText,
          );
          // Token invalid or expired
          localStorage.removeItem("token");
          navigate("/login");
        }
      } catch (error) {
        console.error("❌ Failed to fetch user info:", error);
        localStorage.removeItem("token");
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, [navigate]);

  const fetchWorkflows = async (token: string) => {
    try {
      const response = await fetch("http://localhost:8000/api/workflows", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setWorkflows(data);
      }
    } catch (error) {
      console.error("Failed to fetch workflows:", error);
    }
  };

  const toggleWorkflowStatus = async (workflowId: string) => {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/workflows/${workflowId}/toggle`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (response.ok) {
        // Refresh workflows
        await fetchWorkflows(token);
      }
    } catch (error) {
      console.error("Failed to toggle workflow:", error);
      alert("Failed to toggle workflow status");
    }
  };

  const deleteWorkflow = async (workflowId: string, workflowName: string) => {
    if (
      !confirm(
        `Are you sure you want to delete "${workflowName}"? This cannot be undone.`,
      )
    ) {
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/workflows/${workflowId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (response.ok) {
        // Refresh workflows
        await fetchWorkflows(token);
      }
    } catch (error) {
      console.error("Failed to delete workflow:", error);
      alert("Failed to delete workflow");
    }
  };

  const createNewWorkflow = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const response = await fetch("http://localhost:8000/api/workflows", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: "Untitled Workflow" }),
      });

      if (response.ok) {
        const newWorkflow = await response.json();
        navigate(`/workflows/${newWorkflow.id}/edit`);
      }
    } catch (error) {
      console.error("Failed to create workflow:", error);
      alert("Failed to create workflow");
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}min ago`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
    return `${Math.floor(minutes / 1440)}d ago`;
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-indigo-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-indigo-600 rounded flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-gray-200">
                Zapier Clone
              </span>
            </div>

            {/* User Info & Logout */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-400">Welcome back,</p>
                <p className="font-semibold text-gray-200">{user?.full_name}</p>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/20 transition-colors font-medium"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header with Create Button */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-200 mb-1">
              Your Workflows
            </h1>
            <p className="text-gray-400">
              Automate tasks between your favorite apps
            </p>
          </div>
          <button
            onClick={createNewWorkflow}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium shadow-lg shadow-indigo-500/20"
          >
            <Plus className="w-5 h-5" />
            Create Workflow
          </button>
        </div>

        {/* Workflows Grid */}
        {workflows.length === 0 ? (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
            <div className="text-indigo-400 mb-4">
              <Zap className="w-16 h-16 mx-auto" />
            </div>
            <h2 className="text-xl font-semibold text-gray-200 mb-2">
              No workflows yet
            </h2>
            <p className="text-gray-400 mb-6">
              Create your first workflow to automate your tasks
            </p>
            <button
              onClick={createNewWorkflow}
              className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
            >
              <Plus className="w-5 h-5" />
              Create Your First Workflow
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {workflows.map((workflow) => (
              <div
                key={workflow.id}
                className="bg-gray-800 rounded-lg border border-gray-700 hover:border-indigo-500/50 transition-all overflow-hidden group"
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-4">
                    <span
                      className={`
                        flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium
                        ${workflow.status === "active" ? "bg-green-500/20 text-green-400" : ""}
                        ${workflow.status === "paused" ? "bg-yellow-500/20 text-yellow-400" : ""}
                        ${workflow.status === "draft" ? "bg-gray-700 text-gray-400" : ""}
                      `}
                    >
                      <CircleDot className="w-3 h-3" />
                      {workflow.status.charAt(0).toUpperCase() +
                        workflow.status.slice(1)}
                    </span>
                  </div>

                  {/* Workflow name */}
                  <h3 className="text-lg font-semibold text-gray-200 mb-4 truncate group-hover:text-indigo-400 transition-colors">
                    {workflow.name}
                  </h3>

                  {/* Stats */}
                  <div className="space-y-2 text-sm text-gray-400 mb-6">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>Last run: {formatDate(workflow.last_run_at)}</span>
                    </div>

                    {workflow.total_runs > 0 && (
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1 text-green-400">
                          <CircleDot className="w-3 h-3 fill-current" />
                          <span>{workflow.successful_runs} success</span>
                        </div>
                        <div className="flex items-center gap-1 text-red-400">
                          <CircleDot className="w-3 h-3 fill-current" />
                          <span>
                            {workflow.total_runs - workflow.successful_runs}{" "}
                            failed
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate(`/workflows/${workflow.id}/edit`)}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 rounded-lg hover:bg-indigo-500/20 transition-colors font-medium"
                    >
                      <Edit className="w-4 h-4" />
                      Edit
                    </button>

                    <button
                      onClick={() => toggleWorkflowStatus(workflow.id)}
                      className={`
                        px-4 py-2 rounded-lg transition-colors font-medium border
                        ${
                          workflow.status === "active"
                            ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/30 hover:bg-yellow-500/20"
                            : "bg-green-500/10 text-green-400 border-green-500/30 hover:bg-green-500/20"
                        }
                      `}
                      title={
                        workflow.status === "active" ? "Pause" : "Activate"
                      }
                    >
                      {workflow.status === "active" ? (
                        <PowerOff className="w-4 h-4" />
                      ) : (
                        <Power className="w-4 h-4" />
                      )}
                    </button>

                    <button
                      onClick={() => deleteWorkflow(workflow.id, workflow.name)}
                      className="px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/20 transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
