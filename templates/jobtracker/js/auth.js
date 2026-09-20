(function () {
  "use strict";

  const ACCESS_KEY = "jt_access";
  const REFRESH_KEY = "jt_refresh";

  const AuthStore = {
    getAccess: () => localStorage.getItem(ACCESS_KEY),
    getRefresh: () => localStorage.getItem(REFRESH_KEY),
    setTokens: (access, refresh) => {
      if (access) localStorage.setItem(ACCESS_KEY, access);
      if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
    },
    clear: () => {
      localStorage.removeItem(ACCESS_KEY);
      localStorage.removeItem(REFRESH_KEY);
    },
    isLoggedIn: () => !!localStorage.getItem(ACCESS_KEY),
  };

  async function refreshAccessToken() {
    const refresh = AuthStore.getRefresh();
    if (!refresh) return false;
    try {
      const res = await fetch("/v1/auth/refresh/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      AuthStore.setTokens(data.access, refresh);
      return true;
    } catch (e) {
      return false;
    }
  }

  // Wraps fetch(): attaches the access token, and on a 401 tries exactly one
  // silent refresh + retry before giving up and sending the user to /login/.
  async function authFetch(url, options) {
    options = options || {};
    options.headers = Object.assign({ "Content-Type": "application/json" }, options.headers || {});
    const access = AuthStore.getAccess();
    if (access) options.headers["Authorization"] = `Bearer ${access}`;

    let res = await fetch(url, options);
    if (res.status === 401) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        options.headers["Authorization"] = `Bearer ${AuthStore.getAccess()}`;
        res = await fetch(url, options);
      } else {
        AuthStore.clear();
        window.location.href = "/login/";
        throw new Error("Session expired");
      }
    }
    return res;
  }

  // Convenience wrapper: throws a readable Error on non-2xx, otherwise
  // returns parsed JSON (or null for 204s).
  async function apiRequest(url, options) {
    const res = await authFetch(url, options);
    if (!res.ok) {
      let message = `Request failed (${res.status})`;
      try {
        const data = await res.json();
        message = formatApiError(data);
      } catch (e) {
        /* non-JSON error body, keep the generic message */
      }
      throw new Error(message);
    }
    if (res.status === 204) return null;
    return res.json();
  }

  // Our custom_exception_handler wraps errors as
  // {success:false, code:..., detail: "..."} or {..., detail: {field: "msg"}}.
  // DRF's default (e.g. simplejwt's own 401s) sometimes just sends {detail:"..."}.
  function formatApiError(data) {
    const detail = data && data.detail !== undefined ? data.detail : data;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object") {
      return Object.entries(detail)
        .map(([field, msg]) => (Array.isArray(msg) ? msg.join(" ") : msg))
        .join(" ");
    }
    return "Something went wrong.";
  }

  function requireAuth() {
    if (!AuthStore.isLoggedIn()) {
      window.location.href = "/login/";
    }
  }

  function logout() {
    const refresh = AuthStore.getRefresh();
    fetch("/v1/auth/logout/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    }).finally(() => {
      AuthStore.clear();
      window.location.href = "/login/";
    });
  }

  window.Auth = { AuthStore, authFetch, apiRequest, formatApiError, requireAuth, logout };
})();