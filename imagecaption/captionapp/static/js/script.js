document.addEventListener("DOMContentLoaded", () => {

  // ===== Navbar toggle =====
  const navToggle = document.querySelector(".nav-toggle");
  const navLinks = document.getElementById("navLinks");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => navLinks.classList.toggle("show"));
  }

  // ===== Dark/Light mode =====
  const modeToggle = document.getElementById("modeToggle");
  if (modeToggle) {
    modeToggle.addEventListener("change", () => document.body.classList.toggle("light-mode"));
  }

  // ===== Drop Area & File Input =====
  const dropArea = document.getElementById("dropArea");
  const fileInput = document.getElementById("fileInput");
  const previewImg = document.getElementById("previewImg");
  const form = document.getElementById("uploadForm");
  const spinner = document.getElementById("loadingSpinner");

  // Click to browse
  dropArea.addEventListener("click", () => fileInput.click());

  // Drag & Drop
  dropArea.addEventListener("dragover", e => {
    e.preventDefault();
    dropArea.classList.add("dragover");
  });
  dropArea.addEventListener("dragleave", () => dropArea.classList.remove("dragover"));
  dropArea.addEventListener("drop", e => {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    fileInput.dispatchEvent(new Event("change"));
  });

  // Preview before upload
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => {
        previewImg.src = e.target.result;
        previewImg.classList.remove("hidden");
      };
      reader.readAsDataURL(file);
    }
  });

  // ===== Spinner & Fake Progress =====
  form.addEventListener("submit", () => {
    spinner.style.display = "block";
  });

  // ===== Typing animation for caption =====
  const caption = document.getElementById("captionText");
  if (caption) {
    const text = caption.textContent.trim();
    caption.textContent = "";
    let i = 0;
    const typeWriter = () => {
      if (i < text.length) {
        caption.textContent += text.charAt(i);
        i++;
        setTimeout(typeWriter, 50);
      }
    };
    typeWriter();
  }

});
document.addEventListener("DOMContentLoaded", () => {
  // ===== Mobile Menu Toggle =====
  const menuToggle = document.getElementById("menuToggle");
  const navMenu = document.getElementById("navMenu");
  if (menuToggle && navMenu) {
    menuToggle.addEventListener("click", () => {
      navMenu.classList.toggle("active");
    });
  }

  // ===== Dark Mode Toggle =====
  const modeToggle = document.getElementById("modeToggle");
  if (modeToggle) {
    // Apply saved theme
    if (localStorage.getItem("theme") === "dark") {
      document.body.classList.add("dark-mode");
    }

    modeToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");

      if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
      } else {
        localStorage.setItem("theme", "light");
      }
    });
  }
});