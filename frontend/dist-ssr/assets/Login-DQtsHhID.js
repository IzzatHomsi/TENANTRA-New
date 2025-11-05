import { jsxs, jsx } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { u as useAuth } from "../entry-server.js";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
function ErrorBanner({ message, onClose }) {
  if (!message) return null;
  return /* @__PURE__ */ jsxs("div", { className: "mb-3 flex items-start justify-between rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800", role: "alert", children: [
    /* @__PURE__ */ jsx("div", { className: "pr-3", children: message }),
    /* @__PURE__ */ jsx(
      "button",
      {
        type: "button",
        "aria-label": "Dismiss error",
        className: "ml-2 inline-flex h-6 w-6 items-center justify-center rounded hover:bg-red-100",
        onClick: onClose,
        children: "×"
      }
    )
  ] });
}
function Login() {
  const { signIn, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location?.state && location.state.from && location.state.from.pathname || "/app/dashboard";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, from, navigate]);
  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await signIn({ username, password });
      navigate(from, { replace: true });
    } catch (err) {
      setError(err?.message || "Login failed");
    } finally {
      setSubmitting(false);
    }
  };
  return /* @__PURE__ */ jsx("div", { className: "bg-facebook-gray flex min-h-screen flex-col items-center justify-center", children: /* @__PURE__ */ jsxs("div", { className: "w-full max-w-md", children: [
    /* @__PURE__ */ jsxs("div", { className: "text-center mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-5xl font-bold text-facebook-blue", children: "tenantra" }),
      /* @__PURE__ */ jsx("p", { className: "text-xl", children: "Connect with friends and the world around you on Tenantra." })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "bg-facebook-white p-8 rounded-lg shadow-lg", children: [
      /* @__PURE__ */ jsxs("form", { onSubmit: handleLogin, children: [
        /* @__PURE__ */ jsx(ErrorBanner, { message: error, onClose: () => setError("") }),
        /* @__PURE__ */ jsx("div", { className: "mb-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            className: "w-full rounded-md border border-gray-300 px-4 py-3 text-lg focus:border-facebook-blue focus:outline-none",
            type: "text",
            autoComplete: "username",
            value: username,
            onChange: (event) => setUsername(event.target.value),
            placeholder: "Email or Phone Number",
            required: true
          }
        ) }),
        /* @__PURE__ */ jsx("div", { className: "mb-4", children: /* @__PURE__ */ jsx(
          "input",
          {
            className: "w-full rounded-md border border-gray-300 px-4 py-3 text-lg focus:border-facebook-blue focus:outline-none",
            type: "password",
            autoComplete: "current-password",
            value: password,
            onChange: (event) => setPassword(event.target.value),
            placeholder: "Password",
            required: true
          }
        ) }),
        /* @__PURE__ */ jsx(
          "button",
          {
            type: "submit",
            className: "w-full rounded-md bg-facebook-blue px-4 py-3 text-lg font-bold text-white hover:bg-blue-600 disabled:opacity-60",
            disabled: submitting,
            children: submitting ? "Logging In..." : "Log In"
          }
        )
      ] }),
      /* @__PURE__ */ jsx("div", { className: "text-center mt-4", children: /* @__PURE__ */ jsx("a", { href: "#", className: "text-facebook-blue hover:underline", children: "Forgot password?" }) }),
      /* @__PURE__ */ jsx("hr", { className: "my-6" }),
      /* @__PURE__ */ jsx("div", { className: "text-center", children: /* @__PURE__ */ jsx("button", { className: "rounded-md bg-green-500 px-6 py-3 text-lg font-bold text-white hover:bg-green-600", children: "Create New Account" }) })
    ] })
  ] }) });
}
export {
  Login as default
};
