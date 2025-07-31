
document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.querySelector('input[type="file"]');
  fileInput.addEventListener("change", (event) => {
    const fileName = event.target.files[0]?.name || "No file selected";
    alert("Selected video: " + fileName);
  });

  const form = document.querySelector("form");
  form.addEventListener("submit", (e) => {
    const confirmed = confirm("Are you sure you want to upload this video?");
    if (!confirmed) {
      e.preventDefault();
    }
  });
});
