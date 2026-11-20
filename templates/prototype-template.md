<!--
  Filled by __SPECKIT_COMMAND_SPECIFY__. This template is a construction
  contract: replace every bracketed placeholder, remove unused guidance, and
  keep the resolved file as standalone HTML. Do not wrap this document in a
  Markdown code fence.
-->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>[FEATURE NAME] - Prototype</title>
  <style>
    :root {
      color-scheme: light;
      --background: #f7f8fa;
      --surface: #ffffff;
      --text: #1f2328;
      --muted: #59636e;
      --border: #d0d7de;
      --primary: #0969da;
      --danger: #cf222e;
      --warning: #9a6700;
      --success: #1a7f37;
      --radius: 0.5rem;
      --space: 1rem;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      color: var(--text);
      background: var(--background);
      line-height: 1.5;
    }

    button,
    input,
    select,
    textarea {
      font: inherit;
    }

    button,
    [role="button"] {
      cursor: pointer;
    }

    :focus-visible {
      outline: 3px solid color-mix(in srgb, var(--primary) 30%, transparent);
      outline-offset: 2px;
    }

    .prototype-shell {
      min-height: 100vh;
    }

    .prototype-frame {
      width: min(100%, 80rem);
      margin: 0 auto;
      padding: clamp(1rem, 3vw, 3rem);
    }

    .prototype-surface {
      border: 1px solid var(--border);
      border-radius: var(--radius);
      background: var(--surface);
      box-shadow: 0 0.25rem 1.25rem rgb(31 35 40 / 8%);
    }

    .prototype-stack {
      display: grid;
      gap: var(--space);
    }

    .prototype-status[data-state="empty"],
    .prototype-status[data-state="loading"],
    .prototype-status[data-state="error"],
    .prototype-status[data-state="success"] {
      border-radius: var(--radius);
      padding: 0.75rem var(--space);
    }

    .prototype-status[data-state="empty"],
    .prototype-status[data-state="loading"] {
      color: var(--muted);
      background: #f6f8fa;
    }

    .prototype-status[data-state="error"] {
      color: var(--danger);
      background: #ffebe9;
    }

    .prototype-status[data-state="success"] {
      color: var(--success);
      background: #dafbe1;
    }

    [hidden] {
      display: none !important;
    }

    @media (max-width: 48rem) {
      .prototype-frame {
        padding: var(--space);
      }
    }
  </style>
</head>
<body>
  <!--
    Use stable, unique data-spec-ref values for every page, region, component,
    and meaningful state. References should combine a requirement identity and
    a semantic UI identity, for example:
      data-spec-ref="FR-001:project-list"
      data-spec-ref="US-002:task-form:validation-error"
  -->
  <div
    class="prototype-shell"
    data-spec-ref="[FEATURE-REF:root]"
    data-prototype-version="1"
  >
    <main class="prototype-frame prototype-stack">
      <header data-spec-ref="[FEATURE-REF:page-header]">
        <h1>[PAGE TITLE]</h1>
        <p>[PAGE PURPOSE]</p>
      </header>

      <section
        class="prototype-surface prototype-stack"
        data-spec-ref="[US-001:primary-flow]"
        data-prototype-state="default"
        style="padding: var(--space)"
      >
        <h2>[PRIMARY USER TASK]</h2>
        <p>[Replace this scaffold with the exact page structure, information hierarchy, controls, and interactions required by the specification.]</p>

        <!--
          Keep applicable states in the same document. Each state must be
          reachable through the prototype controls or documented state links.
        -->
        <div
          class="prototype-status"
          data-spec-ref="[FR-001:primary-state:empty]"
          data-state="empty"
          hidden
        >[EMPTY STATE]</div>
        <div
          class="prototype-status"
          data-spec-ref="[FR-001:primary-state:loading]"
          data-state="loading"
          hidden
        >[LOADING STATE]</div>
        <div
          class="prototype-status"
          data-spec-ref="[FR-001:primary-state:error]"
          data-state="error"
          hidden
        >[ERROR STATE]</div>
        <div
          class="prototype-status"
          data-spec-ref="[FR-001:primary-state:success]"
          data-state="success"
          hidden
        >[SUCCESS STATE]</div>
      </section>
    </main>
  </div>

  <script>
    (() => {
      "use strict";

      // Keep all prototype interactions local. Do not call network services,
      // load frameworks, or implement production business/data services here.
      const app = document.querySelector(".prototype-shell");
      if (!app) return;

      app.addEventListener("click", (event) => {
        const trigger = event.target.closest("[data-show-state]");
        if (!trigger) return;

        const regionRef = trigger.dataset.regionRef;
        const state = trigger.dataset.showState;
        const region = regionRef
          ? app.querySelector(`[data-spec-ref="${regionRef}"]`)
          : null;
        if (!region || !state) return;

        region.dataset.prototypeState = state;
        region.querySelectorAll("[data-state]").forEach((node) => {
          node.hidden = node.dataset.state !== state;
        });
      });
    })();
  </script>
</body>
</html>
