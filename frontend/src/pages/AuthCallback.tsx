import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

export default function AuthCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const token = searchParams.get("token");
    const error = searchParams.get("error");

    console.log("🔍 AuthCallback - URL Search Params:", {
      token: token ? `${token.substring(0, 20)}...` : null,
      error: error,
      fullURL: window.location.href,
    });

    if (token) {
      console.log("✅ Token found, storing in localStorage");
      // Store token in localStorage
      localStorage.setItem("token", token);
      // Redirect to dashboard
      console.log("✅ Redirecting to dashboard");
      navigate("/dashboard");
    } else if (error) {
      // Handle error
      console.error("❌ OAuth error:", error);
      navigate("/login?error=" + error);
    } else {
      console.warn("⚠️ No token or error found, redirecting to login");
      navigate("/login");
    }
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Completing sign in...</p>
      </div>
    </div>
  );
}
