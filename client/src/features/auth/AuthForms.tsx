import { FormEvent, useState } from "react";

import { useAuth } from "./AuthContext";

const AuthForms = () => {
  const { state, loginUser, registerUser, logout, loading, error } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (mode === "login") {
      await loginUser(email, password);
    } else {
      await registerUser(email, password, fullName);
    }
  };

  if (state.accessToken) {
    return (
      <section className="auth-card" id="auth">
        <header>
          <span className="badge">Access</span>
          <h3>Signed in</h3>
        </header>
        <p>You are logged in as {state.userEmail ?? "current user"}.</p>
        <button type="button" className="btn btn--ghost" onClick={logout}>
          Logout
        </button>
      </section>
    );
  }

  return (
    <section className="auth-card" id="auth">
      <header>
        <span className="badge">Access</span>
        <h3>{mode === "login" ? "Login to Autorisen" : "Create an account"}</h3>
      </header>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          Email
          <input
            required
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
          />
        </label>
        {mode === "register" && (
          <label>
            Full name (optional)
            <input
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              placeholder="Ada Lovelace"
            />
          </label>
        )}
        <label>
          Password
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="••••••••"
          />
        </label>
        {error && <p className="auth-error">{error}</p>}
        <button className="btn btn--primary" type="submit" disabled={loading}>
          {loading ? "Submitting…" : mode === "login" ? "Login" : "Register"}
        </button>
      </form>
      <footer>
        <button type="button" className="btn btn--link" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Need an account? Register" : "Have an account? Login"}
        </button>
      </footer>
    </section>
  );
};

export default AuthForms;
