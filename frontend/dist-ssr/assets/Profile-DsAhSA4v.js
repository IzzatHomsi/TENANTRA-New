import { jsxs, jsx } from "react/jsx-runtime";
import { useState } from "react";
import { u as useAuth, g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const API_BASE = getApiBase();
function Profile() {
  const { token, user, role } = useAuth();
  const [email, setEmail] = useState(user?.email || "");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const isStrongPassword = (pw) => {
    if (!pw) return true;
    return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/.test(pw);
  };
  const readErr = async (res) => {
    try {
      const text = await res.text();
      try {
        const json = JSON.parse(text);
        return json?.detail || json?.message || text;
      } catch {
        return text;
      }
    } catch {
      return `HTTP ${res.status}`;
    }
  };
  const handleSave = async (event) => {
    event.preventDefault();
    setMessage("");
    setError("");
    if (!email.trim() || !/\S+@\S+\.\S+/.test(email)) {
      setError("Please provide a valid email address.");
      return;
    }
    if (!isStrongPassword(password)) {
      setError(
        "Password must be at least 8 chars and include upper, lower, digit, and special character."
      );
      return;
    }
    const body = { email };
    if (password) body.password = password;
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/users/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(body)
      });
      if (!res.ok) {
        const msg = await readErr(res);
        throw new Error(msg || `Update failed (HTTP ${res.status})`);
      }
      setMessage("Profile updated successfully.");
      setPassword("");
    } catch (err) {
      setError(err.message || "Failed to update profile.");
    } finally {
      setSubmitting(false);
    }
  };
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "My Profile" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Update your account details and rotate credentials." })
    ] }),
    /* @__PURE__ */ jsxs(Card, { className: "max-w-lg", children: [
      message && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-green-100 p-4 text-green-700", children: message }),
      error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
      /* @__PURE__ */ jsxs("form", { onSubmit: handleSave, className: "space-y-6", children: [
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Username" }),
          /* @__PURE__ */ jsx("input", { value: user?.username || "", disabled: true, className: "mt-1 block w-full rounded-md border-gray-300 bg-gray-100 shadow-sm sm:text-sm" })
        ] }),
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Email" }),
          /* @__PURE__ */ jsx(
            "input",
            {
              type: "email",
              value: email,
              placeholder: "you@example.com",
              onChange: (event) => setEmail(event.target.value),
              required: true,
              className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
            }
          )
        ] }),
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "New Password" }),
          /* @__PURE__ */ jsx(
            "input",
            {
              type: "password",
              value: password,
              placeholder: "Leave empty to keep current password",
              onChange: (event) => setPassword(event.target.value),
              className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
            }
          )
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
          /* @__PURE__ */ jsxs("span", { className: "text-sm text-gray-500", children: [
            "Role: ",
            /* @__PURE__ */ jsx("strong", { children: role || "standard_user" })
          ] }),
          /* @__PURE__ */ jsx(Button, { type: "submit", disabled: submitting, children: submitting ? "Saving..." : "Save" })
        ] })
      ] })
    ] })
  ] });
}
export {
  Profile as default
};
