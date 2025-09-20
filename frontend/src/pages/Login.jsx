
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Eye, EyeOff } from "lucide-react";

export default function Login() {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    const success = login({ email, password });
    if (success) {
      navigate("/dashboard");
    } else {
      setError("Invalid credentials! Use demo2@example.com / demopass123");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-100 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300">
      <form onSubmit={handleLogin} className="card w-full max-w-md p-8 shadow-xl border border-gray-100 dark:border-gray-700">
        <div className="flex flex-col items-center mb-6">
          <img src="/logo192.png" alt="Dristhi Logo" className="w-14 h-14 mb-2" />
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white mb-1">Welcome to Dristhi</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm">AI-Powered Career & Life Platform</p>
        </div>
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 text-center">
            {error}
          </div>
        )}
        <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-200">Email</label>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="input-field mb-4"
          disabled={loading}
          required
        />
        <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-200">Password</label>
        <div className="relative mb-4">
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input-field pr-10"
            disabled={loading}
            required
          />
          <button
            type="button"
            tabIndex={-1}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
            onClick={() => setShowPassword((v) => !v)}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
          </button>
        </div>
        <button
          type="submit"
          className="btn-primary w-full text-lg font-semibold py-2 mt-2"
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
        <div className="mt-6 mb-2">
          <div className="bg-blue-50 dark:bg-gray-900 border border-blue-200 dark:border-gray-700 rounded-lg px-4 py-3 text-center text-sm text-blue-800 dark:text-blue-200">
            <div className="font-semibold mb-1">Demo Credentials</div>
            <div className="flex flex-col gap-1">
              <span><b>Email:</b> demo2@example.com</span>
              <span><b>Password:</b> demopass123</span>
            </div>
          </div>
        </div>
        <div className="text-center text-xs text-gray-400 mt-2">
          &copy; {new Date().getFullYear()} Dristhi. All rights reserved.
        </div>
      </form>
    </div>
  );
}
