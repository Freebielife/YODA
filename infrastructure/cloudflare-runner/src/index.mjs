import { projects } from "./projects.mjs";

const GITHUB_API = "https://api.github.com";
const GITHUB_API_VERSION = "2026-03-10";
const TICK_MINUTES = 10;

export function validateProject(project) {
  if (!project || typeof project !== "object") throw new Error("Invalid project configuration");
  for (const field of ["id", "owner", "repo", "workflow", "ref"]) {
    if (typeof project[field] !== "string" || !/^[A-Za-z0-9._-]+$/.test(project[field])) {
      throw new Error("Invalid " + field + " in project configuration");
    }
  }
  if (typeof project.enabled !== "boolean") throw new Error("Project enabled flag must be boolean");
  const { everyMinutes, phaseMinutes } = project;
  if (!Number.isInteger(everyMinutes) || everyMinutes < TICK_MINUTES ||
      everyMinutes > 1440 || 1440 % everyMinutes !== 0 ||
      everyMinutes % TICK_MINUTES !== 0) {
    throw new Error("Invalid everyMinutes for " + project.id);
  }
  if (!Number.isInteger(phaseMinutes) || phaseMinutes < 0 ||
      phaseMinutes >= everyMinutes || phaseMinutes % TICK_MINUTES !== 0) {
    throw new Error("Invalid phaseMinutes for " + project.id);
  }
}

export function selectDueProjects(scheduledTime, registry = projects) {
  const at = new Date(scheduledTime);
  if (!Number.isFinite(at.getTime())) throw new Error("Invalid scheduled time");
  // Slots repeat every UTC day; everyMinutes must divide 1440.
  const minuteOfDay = at.getUTCHours() * 60 + at.getUTCMinutes();
  for (const project of registry) validateProject(project);
  const ids = registry.map(p => p.id);
  if (new Set(ids).size !== ids.length) throw new Error("Duplicate project ID");
  return registry.filter(p => p.enabled && minuteOfDay % p.everyMinutes === p.phaseMinutes);
}

export async function dispatchDue({ scheduledTime, token, registry = projects, fetcher = fetch }) {
  const due = selectDueProjects(scheduledTime, registry);
  if (!due.length) return [];
  if (typeof token !== "string" || !token.trim()) {
    throw new Error("GITHUB_ACTIONS_TOKEN secret is missing");
  }

  // Failures for one repository do not prevent other repositories dispatching.
  const outcomes = await Promise.allSettled(due.map(async project => {
    const endpoint = GITHUB_API + "/repos/" +
      encodeURIComponent(project.owner) + "/" +
      encodeURIComponent(project.repo) + "/actions/workflows/" +
      encodeURIComponent(project.workflow) + "/dispatches";
    const response = await fetcher(endpoint, {
      method: "POST",
      headers: {
        Accept: "application/vnd.github+json",
        // GitHub REST API rejects requests without a valid User-Agent (HTTP 403).
        "User-Agent": "Freebie-Observatory-Runner/1.0",
        Authorization: "Bearer " + token,
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ ref: project.ref })
    });
    if (!response.ok) {
      // Classify only known GitHub diagnostics; never print raw response bodies
      // or authentication credentials to Worker logs.
      let reason = "unknown";
      if (typeof response.json === "function") {
        try {
          const body = await response.json();
          const message = typeof body?.message === "string" ? body.message.toLowerCase() : "";
          if (message.includes("resource not accessible by personal access token") ||
              message.includes("resource not accessible by integration")) {
            reason = "token-repository-permissions";
          } else if (message.includes("secondary rate limit") || message.includes("abuse detection")) {
            reason = "secondary-rate-limit";
          } else if (message.includes("rate limit exceeded")) {
            reason = "rate-limit";
          } else if (message.includes("bad credentials")) {
            reason = "invalid-credentials";
          }
        } catch { /* GitHub may respond without a JSON body. */ }
      }
      const acceptedPermissions = response.headers?.get?.("x-accepted-github-permissions");
      const permissions = typeof acceptedPermissions === "string" &&
        acceptedPermissions.length <= 120 && /^[a-z_,;=\s]+$/.test(acceptedPermissions)
        ? acceptedPermissions.trim() : "not-provided";
      const remaining = response.headers?.get?.("x-ratelimit-remaining");
      const rate = typeof remaining === "string" && /^\d{1,8}$/.test(remaining)
        ? remaining : "unknown";
      throw new Error(project.id + ": GitHub dispatch HTTP " + response.status +
        " reason=" + reason + " required_permissions=" + permissions +
        " rate_remaining=" + rate);
    }
    return project.id;
  }));

  const failures = outcomes.flatMap((r, i) =>
    r.status === "rejected"
      ? [due[i].id + ": " + (r.reason instanceof Error ? r.reason.message : "dispatch failed")]
      : []);
  if (failures.length) {
    // Never log request headers, GitHub tokens or response bodies.
    throw new Error("Some observatories could not start: " + failures.join("; "));
  }
  return outcomes.map(r => r.value);
}

export default {
  // No public HTTP trigger. Only the authenticated Cloudflare cron scheduler
  // invokes scheduled(); this prevents strangers from starting Actions jobs.
  fetch() {
    return new Response("Not found", { status: 404 });
  },
  async scheduled(event, env) {
    try {
      const dispatched = await dispatchDue({
        scheduledTime: event.scheduledTime,
        token: env.GITHUB_ACTIONS_TOKEN
      });
      console.log(dispatched.length
        ? "Observatory dispatch accepted: " + dispatched.join(", ")
        : "No observatories due in this slot");
    } catch (error) {
      // Log only our curated exception message (project ID / HTTP status).
      // Do not output credentials, request headers, or GitHub response bodies.
      console.error("Observatory dispatch failed: " +
        (error instanceof Error ? error.message : "unknown error"));
      throw error;
    }
  }
};
