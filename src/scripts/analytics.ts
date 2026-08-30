import posthog from "posthog-js";

const posthogKey = import.meta.env.PUBLIC_POSTHOG_KEY;
const posthogHost = import.meta.env.PUBLIC_POSTHOG_HOST ?? "https://eu.i.posthog.com";

type AnalyticsLink = HTMLAnchorElement & {
  dataset: DOMStringMap & {
    analyticsEvent?: string;
    analyticsLabel?: string;
  };
};

const scrollDepthThresholds = [25, 50, 75, 100] as const;

if (posthogKey) {
  const currentPath = window.location.pathname;
  const capturedSessionEvents = new Set<string>();
  const captureOncePerSession = (
    key: string,
    eventName: string,
    properties: Record<string, string | number>
  ) => {
    const storageKey = `erme2:analytics:${currentPath}:${key}`;

    if (capturedSessionEvents.has(storageKey)) {
      return;
    }

    try {
      if (window.sessionStorage.getItem(storageKey)) {
        capturedSessionEvents.add(storageKey);
        return;
      }

      window.sessionStorage.setItem(storageKey, "1");
    } catch {
      // Session storage can be unavailable in restrictive browser modes.
    }

    capturedSessionEvents.add(storageKey);
    posthog.capture(eventName, properties);
  };

  const trackSectionViews = () => {
    if (!("IntersectionObserver" in window)) {
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || !(entry.target instanceof HTMLElement)) {
          return;
        }

        const section = entry.target.dataset.analyticsSection;

        if (!section) {
          return;
        }

        captureOncePerSession(`section:${section}`, "site_section_viewed", {
          section,
          path: currentPath
        });
        observer.unobserve(entry.target);
      });
    }, {
      rootMargin: "0px 0px -35% 0px",
      threshold: 0.25
    });

    document.querySelectorAll<HTMLElement>("[data-analytics-section]").forEach((section) => {
      observer.observe(section);
    });
  };

  const trackScrollDepth = () => {
    const scrollHeight = Math.max(
      document.body.scrollHeight,
      document.documentElement.scrollHeight
    );
    const viewportBottom = window.scrollY + window.innerHeight;
    const depth = Math.min(100, Math.floor((viewportBottom / scrollHeight) * 100));

    scrollDepthThresholds
      .filter((threshold) => depth >= threshold)
      .forEach((threshold) => {
        captureOncePerSession(`scroll:${threshold}`, "site_scroll_depth_reached", {
          depth: threshold,
          path: currentPath
        });
      });
  };

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
        path: currentPath,
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
      path: currentPath
    });
  });

  trackSectionViews();
  trackScrollDepth();
  window.addEventListener("scroll", trackScrollDepth, { passive: true });
}
