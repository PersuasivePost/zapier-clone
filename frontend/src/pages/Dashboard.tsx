import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Zap, LogOut } from "lucide-react";

interface User {
  id: string;
  email: string;
  full_name: string;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserInfo = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        navigate("/login");
        return;
      }

      try {
        const response = await fetch("http://localhost:8000/api/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          // Token invalid or expired
          localStorage.removeItem("token");
          navigate("/login");
        }
      } catch (error) {
        console.error("Failed to fetch user info:", error);
        localStorage.removeItem("token");
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-orange-500 rounded flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold">Zapier</span>
            </div>

            {/* User Info & Logout */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-500">Welcome back,</p>
                <p className="font-semibold text-gray-900">{user?.full_name}</p>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition"
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
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
          <div className="space-y-4">
            <div className="border-l-4 border-orange-500 bg-orange-50 p-4">
              <h2 className="font-semibold text-gray-900 mb-2">
                🎉 Welcome to Your Workspace!
              </h2>
              <p className="text-gray-700">
                You're successfully logged in as <strong>{user?.email}</strong>
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-orange-500 transition">
                <div className="text-4xl mb-2">⚡</div>
                <h3 className="font-semibold text-gray-900 mb-2">Workflows</h3>
                <p className="text-gray-600 text-sm">
                  Create automated workflows to connect your apps
                </p>
              </div>

              <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-orange-500 transition">
                <div className="text-4xl mb-2">🔗</div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  Connections
                </h3>
                <p className="text-gray-600 text-sm">
                  Manage your app integrations and connections
                </p>
              </div>

              <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-orange-500 transition">
                <div className="text-4xl mb-2">📊</div>
                <h3 className="font-semibold text-gray-900 mb-2">Analytics</h3>
                <p className="text-gray-600 text-sm">
                  View your workflow performance and statistics
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
