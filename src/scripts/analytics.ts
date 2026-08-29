import posthog from "posthog-js";

const posthogKey = import.meta.env.PUBLIC_POSTHOG_KEY;
const posthogHost = import.meta.env.PUBLIC_POSTHOG_HOST ?? "https://eu.i.posthog.com";

type AnalyticsLink = HTMLAnchorElement & {
  dataset: DOMStringMap & {
    analyticsEvent?: string;
    analyticsLabel?: string;
  };
};

if (posthogKey) {
  posthog.init(posthogKey, {
    api_host: posthogHost,
    defaults: "2026-05-30",
    person_profiles: "identified_only",
    autocapture: false,
    capture_pageview: false,
    capture_pageleave: false,
    session_recording: {
      maskAllInputs: true,
      maskAllElementAttributes: true
    },
    loaded: (client) => {
      client.capture("$pageview", {
        path: window.location.pathname,
        title: document.title
      });
    }
  });

  document.addEventListener("click", (event) => {
    const target = event.target instanceof Element
      ? event.target.closest<AnalyticsLink>("a[data-analytics-event]")
      : null;

    if (!target) {
      return;
    }

    posthog.capture(target.dataset.analyticsEvent ?? "link_clicked", {
      label: target.dataset.analyticsLabel ?? target.textContent?.trim(),
      href: target.href,
      path: window.location.pathname
    });
  });
}
