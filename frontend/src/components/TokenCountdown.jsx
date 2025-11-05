import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import { jwtDecode } from "jwt-decode";

/**
 * TokenCountdown displays the remaining time until the current JWT expires.
 * It reads the token from the AuthContext, decodes the expiry timestamp and
 * continually updates the countdown every second. When the token has
 * expired it shows a notice. If there is no token available nothing is
 * rendered.
 */
function TokenCountdown() {
  const { token } = useAuth();
  const [timeLeft, setTimeLeft] = useState(null);

  useEffect(() => {
    // Only start countdown when a token is present
    if (!token) {
      setTimeLeft(null);
      return;
    }

    let decoded;
    try {
      decoded = jwtDecode(token);
    } catch (err) {
      setTimeLeft(null);
      return;
    }
    const expiryMs = decoded.exp * 1000;

    // Helper to update the remaining time
    const updateTime = () => {
      const now = Date.now();
      setTimeLeft(expiryMs - now);
    };

    // Initialise immediately and set interval
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, [token]);

  // Do not render anything if there is no token or time left is undefined
  if (timeLeft === null) return null;

  if (timeLeft <= 0) {
    return <p className="text-xs text-red-400">Session expired</p>;
  }

  // Convert milliseconds to minutes and seconds
  const totalSeconds = Math.floor(timeLeft / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  const formatted = `${minutes}:${seconds.toString().padStart(2, "0")}`;

  return (
    <p className="mt-1 text-xs text-slate-400">⏳ Session expires in {formatted}</p>
  );
}

export default TokenCountdown;
