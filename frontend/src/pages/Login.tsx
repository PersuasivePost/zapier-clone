import { useState } from "react";
import { Zap } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <div className="min-h-screen bg-white flex">
      {/* Left Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="flex items-center gap-2 mb-8">
            <div className="w-10 h-10 bg-orange-500 rounded flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold">Zapier</span>
          </div>

          <h1 className="text-3xl font-bold mb-2">Log in to your account</h1>
          <p className="text-gray-600 mb-8">
            Don't have an account?{" "}
            <a
              href="/signup"
              className="text-orange-500 hover:text-orange-600 font-semibold"
            >
              Sign up
            </a>
          </p>

          {/* Social Login Buttons */}
          <div className="space-y-3 mb-6">
            <button
              onClick={() =>
                (window.location.href =
                  "http://localhost:8000/api/auth/google/login")
              }
              className="w-full py-3 px-4 border-2 border-gray-300 rounded hover:bg-gray-50 transition flex items-center justify-center gap-3 font-semibold"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google
            </button>

            {/*
            <button className="w-full py-3 px-4 border-2 border-gray-300 rounded hover:bg-gray-50 transition flex items-center justify-center gap-3 font-semibold">
              <svg className="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
              Continue with Facebook
            </button>

            <button className="w-full py-3 px-4 border-2 border-gray-300 rounded hover:bg-gray-50 transition flex items-center justify-center gap-3 font-semibold">
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
              </svg>
              Continue with LinkedIn
            </button>
            */}
          </div>

          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 border-t border-gray-300"></div>
            <span className="text-sm text-gray-500">OR</span>
            <div className="flex-1 border-t border-gray-300"></div>
          </div>

          {/* Email/Password Form */}
          <form className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-semibold mb-2"
              >
                Email
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded focus:border-orange-500 focus:outline-none"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-semibold mb-2"
              >
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded focus:border-orange-500 focus:outline-none"
                placeholder="Enter your password"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="w-4 h-4 text-orange-500 border-gray-300 rounded focus:ring-orange-500"
                />
                <span className="ml-2 text-sm text-gray-700">Remember me</span>
              </label>
              <a
                href="#"
                className="text-sm text-orange-500 hover:text-orange-600 font-semibold"
              >
                Forgot password?
              </a>
            </div>

            <button
              type="submit"
              className="w-full py-3 bg-orange-500 text-white rounded font-semibold hover:bg-orange-600 transition"
            >
              Log in
            </button>
          </form>

          <p className="text-xs text-gray-500 mt-6 text-center">
            By continuing, you agree to Zapier's{" "}
            <a href="#" className="text-orange-500 hover:underline">
              Terms of Service
            </a>{" "}
            and{" "}
            <a href="#" className="text-orange-500 hover:underline">
              Privacy Policy
            </a>
          </p>
        </div>
      </div>

      {/* Right Side - Illustration/Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-orange-400 to-pink-500 items-center justify-center p-12">
        <div className="text-white text-center max-w-md">
          <h2 className="text-4xl font-bold mb-4">Welcome back!</h2>
          <p className="text-lg opacity-90">
            Access your automation workflows and connect your favorite apps in
            seconds.
          </p>
          <div className="mt-12 grid grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="w-16 h-16 bg-white/20 backdrop-blur rounded-lg"
              ></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
