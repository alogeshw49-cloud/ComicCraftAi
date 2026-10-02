/* ═══════════════════════════════════════
   ComicCraft AI — JavaScript
   Form handling, loading states, confetti
   ═══════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {

  // ─── Art Style Card Toggle ───────────────────────────────
  const styleCards = document.querySelectorAll(".style-card");
  styleCards.forEach(card => {
    card.addEventListener("click", () => {
      styleCards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");
    });
  });

  // ─── Character Counter for Textarea ──────────────────────
  const promptArea = document.getElementById("prompt");
  const counter    = document.getElementById("promptCount");
  if (promptArea && counter) {
    promptArea.addEventListener("input", () => {
      counter.textContent = promptArea.value.length;
      if (promptArea.value.length > 900) {
        counter.style.color = "#ef4444";
      } else {
        counter.style.color = "";
      }
    });
  }

  // ─── Form Submission + Loading State ─────────────────────
  const form           = document.getElementById("comicForm");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const generateBtn    = document.getElementById("generateBtn");

  if (form) {
    form.addEventListener("submit", (e) => {
      // Validate required fields
      const promptVal = document.getElementById("prompt")?.value.trim();
      const charVal   = document.getElementById("character")?.value.trim();

      if (!promptVal || promptVal.length < 5) {
        e.preventDefault();
        showToast("⚠️ Please enter a story prompt (min 5 characters)", "error");
        return;
      }

      if (!charVal) {
        e.preventDefault();
        showToast("⚠️ Please enter the main character name", "error");
        return;
      }

      // Show loading overlay
      if (loadingOverlay) {
        loadingOverlay.style.display = "flex";
        startLoadingSequence();
      }

      // Disable button
      if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<span class="btn-icon">⏳</span><span class="btn-text">Generating...</span>';
      }
    });
  }

  // ─── Animated Loading Step Sequence ──────────────────────
  function startLoadingSequence() {
    const steps = [
      { id: "step-outline", delay: 0 },
      { id: "step-story",   delay: 15000 },
      { id: "step-images",  delay: 30000 },
      { id: "step-pdf",     delay: 100000 },
    ];

    let prevStepEl = null;

    steps.forEach(({ id, delay }) => {
      setTimeout(() => {
        if (prevStepEl) {
          prevStepEl.classList.remove("active");
          prevStepEl.classList.add("done");
          // Update dot to checkmark
          const dot = prevStepEl.querySelector(".step-dot");
          if (dot) dot.textContent = "✓";
        }
        const stepEl = document.getElementById(id);
        if (stepEl) {
          stepEl.classList.add("active");
          prevStepEl = stepEl;
        }
      }, delay);
    });
  }

  // ─── Panel scroll-in animation ───────────────────────────
  const panels = document.querySelectorAll(".panel-card");
  if (panels.length > 0 && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    panels.forEach(panel => {
      panel.style.opacity = "0";
      panel.style.transform = "translateY(30px)";
      panel.style.transition = "opacity 0.6s ease, transform 0.6s ease";
      observer.observe(panel);
    });
  }

  // ─── Green Panel Download Success Modal ───────────────────
  setupDownloadSuccessModal();

  // ─── Smooth Scroll to form ────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", (e) => {
      const target = document.querySelector(anchor.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth" });
      }
    });
  });

});

// ═══════════════════════════════════════
// Green Panel Download Success Modal
// ═══════════════════════════════════════
function setupDownloadSuccessModal() {
  const modal = document.getElementById("downloadSuccessModal");
  const closeBtn = document.getElementById("closeModalBtn");
  const dismissBtn = document.getElementById("dismissModalBtn");

  // Hook all download buttons on the page
  const downloadLinks = document.querySelectorAll(
    'a[href*="download-pdf"], .btn-download, #downloadBtn'
  );

  downloadLinks.forEach(link => {
    link.addEventListener("click", (e) => {
      // Do not prevent default so browser initiates file download!
      const href = link.getAttribute("href") || "";
      let pdfPath = "";
      try {
        const url = new URL(href, window.location.origin);
        pdfPath = url.searchParams.get("pdf_path") || "";
      } catch (err) {
        pdfPath = "";
      }

      // Show toast + Green Panel modal after a quick delay so download starts first
      showToast("📥 Downloading comic PDF...", "success");

      setTimeout(() => {
        showDownloadSuccessModal(pdfPath);
      }, 400);
    });
  });

  // Close handlers
  if (closeBtn) closeBtn.addEventListener("click", hideDownloadSuccessModal);
  if (dismissBtn) dismissBtn.addEventListener("click", hideDownloadSuccessModal);

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        hideDownloadSuccessModal();
      }
    });
  }

  // Escape key closes modal
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal && modal.classList.contains("show")) {
      hideDownloadSuccessModal();
    }
  });
}

function showDownloadSuccessModal(pdfPath) {
  let modal = document.getElementById("downloadSuccessModal");
  if (!modal) return;

  // Extract clean filename
  let fileName = "comic_story.pdf";
  if (pdfPath) {
    const parts = pdfPath.split("/");
    fileName = parts[parts.length - 1];
  }

  const fileNameEl = document.getElementById("modalFileName");
  if (fileNameEl && fileName) {
    fileNameEl.textContent = fileName;
  }

  // Update "Open / View PDF" link to open in new tab
  const viewBtn = document.getElementById("modalViewPdfBtn");
  if (viewBtn && pdfPath) {
    viewBtn.href = "/" + pdfPath.replace(/^\//, "");
    viewBtn.setAttribute("target", "_blank");
  }

  // Update Download Again link
  const againBtn = document.getElementById("modalDownloadAgainBtn");
  if (againBtn && pdfPath) {
    againBtn.href = `/download-pdf?pdf_path=${encodeURIComponent(pdfPath)}`;
  }

  // Display modal
  modal.classList.add("show");

  // Re-trigger SVG checkmark animation
  const checkCircle = modal.querySelector(".modal-check-circle");
  const checkPath = modal.querySelector(".modal-check-path");
  if (checkCircle && checkPath) {
    checkCircle.style.animation = "none";
    checkPath.style.animation = "none";
    checkCircle.offsetHeight; // trigger reflow
    checkCircle.style.animation = "";
    checkPath.style.animation = "";
  }

  // Fire celebratory confetti!
  launchConfetti();
}

function hideDownloadSuccessModal() {
  const modal = document.getElementById("downloadSuccessModal");
  if (modal) {
    modal.classList.remove("show");
  }
}

// ═══════════════════════════════════════
// Toast Notification
// ═══════════════════════════════════════
function showToast(message, type = "info") {
  const existing = document.querySelector(".toast");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  toast.style.cssText = `
    position: fixed;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%) translateY(20px);
    background: ${type === "error" ? "#ef4444" : type === "success" ? "#10b981" : "#7c3aed"};
    color: #fff;
    padding: 0.75rem 1.5rem;
    border-radius: 100px;
    font-weight: 700;
    font-size: 0.9rem;
    z-index: 9999;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    max-width: 90vw;
    text-align: center;
  `;

  document.body.appendChild(toast);
  requestAnimationFrame(() => {
    toast.style.opacity = "1";
    toast.style.transform = "translateX(-50%) translateY(0)";
  });

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(-50%) translateY(10px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ═══════════════════════════════════════
// Confetti Animation (for success page)
// ═══════════════════════════════════════
function launchConfetti() {
  const container = document.getElementById("confetti");
  if (!container) return;

  const colors = ["#ffd700", "#7c3aed", "#ec4899", "#06b6d4", "#10b981", "#f97316"];
  const count  = 60;

  for (let i = 0; i < count; i++) {
    const piece = document.createElement("div");
    piece.className = "confetti-piece";

    const color    = colors[Math.floor(Math.random() * colors.length)];
    const left     = Math.random() * 100;
    const delay    = Math.random() * 2;
    const duration = 2 + Math.random() * 2;
    const size     = 6 + Math.random() * 8;

    piece.style.cssText = `
      left: ${left}%;
      top: -20px;
      width: ${size}px;
      height: ${size}px;
      background: ${color};
      animation-duration: ${duration}s;
      animation-delay: ${delay}s;
      border-radius: ${Math.random() > 0.5 ? "50%" : "2px"};
    `;

    container.appendChild(piece);
  }

  // Clean up after animation
  setTimeout(() => {
    container.innerHTML = "";
  }, 6000);
}
