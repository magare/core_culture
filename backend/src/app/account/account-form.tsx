"use client";

import { useRef, useState, type FormEvent } from "react";
import { useSearchParams } from "next/navigation";

type Mode = "sign-in" | "sign-up" | "forgot" | "reset" | "verify";

export function AccountForm({ initiallySignedIn = false }: { initiallySignedIn?: boolean }) {
  const params = useSearchParams();
  const [token, setToken] = useState(params.get("token"));
  const [mode, setMode] = useState<Mode>(token ? "reset" : "sign-in");
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const [message, setMessage] = useState(params.get("verified") === "1" ? "Email verified. You can now sign in." : "");
  const [error, setError] = useState(params.has("error") ? "This email link is invalid or has expired. Request a new verification or recovery email below." : "");
  const [signedIn, setSignedIn] = useState(initiallySignedIn && !token);
  const titles = { "sign-in": "Welcome back.", "sign-up": "Make it yours.", forgot: "A fresh start.", reset: "Choose a new password.", verify: "Verify your email." };
  const labels = { "sign-in": "Sign in", "sign-up": "Create account", forgot: "Send recovery email", reset: "Update password", verify: "Resend verification email" };

  function clearAuthLink() {
    setToken(null);
    window.history.replaceState(null, "", window.location.pathname);
  }

  function switchMode(next: Mode) {
    clearAuthLink(); setMode(next); setMessage(""); setError("");
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending.current) return;
    pending.current = true;
    setBusy(true); setMessage(""); setError("");
    const element = event.currentTarget;
    const form = new FormData(element);
    const address = email.trim();
    const password = String(form.get("password") ?? "");
    const endpoint = mode === "forgot" ? "request-password-reset" : mode === "reset" ? "reset-password" : mode === "verify" ? "send-verification-email" : `${mode}/email`;
    const body = mode === "sign-up" ? { name: String(form.get("name") ?? "").trim(), email: address, password, callbackURL: "/account?verified=1" }
      : mode === "verify" ? { email: address, callbackURL: "/account?verified=1" }
      : mode === "forgot" ? { email: address, redirectTo: `${window.location.origin}/account` }
      : mode === "reset" ? { token, newPassword: password } : { email: address, password };
    try {
      const response = await fetch(`/api/auth/${endpoint}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const result = await response.json().catch(() => null);
      if (!response.ok) throw new Error(result?.error?.message ?? result?.message ?? (response.status === 429 ? "Too many attempts. Please wait a minute and try again." : "Unable to complete this request. Please try again."));
      element.reset();
      setEmail(address);
      setMessage(mode === "sign-up" ? "Check your email to verify your account, then sign in."
        : mode === "verify" ? "If this account needs verification, a new email is on its way."
        : mode === "forgot" ? "If an account exists, a recovery email is on its way."
        : mode === "reset" ? "Password updated. You can now sign in." : "You're signed in.");
      if (mode === "sign-in") setSignedIn(true);
      if (mode === "reset") { clearAuthLink(); setSignedIn(false); setMode("sign-in"); }
      if (mode === "sign-up") setMode("sign-in");
    } catch (cause) { setError(cause instanceof TypeError ? "Unable to connect. Check your connection and try again." : cause instanceof Error ? cause.message : "Unable to connect. Please try again."); }
    finally { pending.current = false; setBusy(false); }
  }

  async function signOut() {
    if (pending.current) return;
    pending.current = true;
    setBusy(true); setError(""); setMessage("");
    try {
      const response = await fetch("/api/auth/sign-out", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
      if (!response.ok) throw new Error("Unable to sign out. Please try again.");
      clearAuthLink(); setMode("sign-in"); setSignedIn(false); setMessage("You're signed out.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to connect."); }
    finally { pending.current = false; setBusy(false); }
  }

  return <div className="form-card" aria-busy={busy}><p className="eyebrow">MEMBER ACCOUNT</p><h2>{signedIn ? "You're connected." : titles[mode]}</h2>
    {signedIn ? <div className="signed-in"><p>Your session is managed with an HTTP-only cookie.</p><a href="/api/me">View my profile API ↗</a><a href="/api/bookings">View my bookings API ↗</a><button className="button" disabled={busy} onClick={signOut}>Sign out</button></div> : <form key={mode} onSubmit={submit}>
      {mode === "sign-up" && <label>Full name<input name="name" autoComplete="name" required minLength={2} maxLength={100} disabled={busy} /></label>}
      {mode !== "reset" && <label>Email address<input name="email" type="email" autoComplete="email" required maxLength={254} value={email} onChange={event => setEmail(event.target.value)} disabled={busy} /></label>}
      {mode !== "forgot" && mode !== "verify" && <label>{mode === "reset" ? "New password" : "Password"}<input name="password" type="password" autoComplete={mode === "sign-in" ? "current-password" : "new-password"} required minLength={12} maxLength={128} aria-describedby="password-hint" disabled={busy} /><span id="password-hint" className="hint">At least 12 characters.</span></label>}
      <button className="button" disabled={busy}>{busy ? "One moment…" : labels[mode]}<span aria-hidden="true">↗</span></button>
    </form>}
    <div role="status" aria-live="polite">{message && <p className="success">{message}</p>}</div>{error && <p className="error" role="alert">{error}</p>}
    {!signedIn && <div className="form-links">
      {mode !== "sign-in" && <button disabled={busy} onClick={() => switchMode("sign-in")}>Back to sign in</button>}
      {mode === "sign-in" && <><button disabled={busy} onClick={() => switchMode("sign-up")}>New here? Create an account</button><button disabled={busy} onClick={() => switchMode("forgot")}>Forgot your password?</button></>}
      {mode !== "verify" && <button disabled={busy} onClick={() => switchMode("verify")}>Resend verification email</button>}
    </div>}
  </div>;
}
