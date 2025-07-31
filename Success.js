document.addEventListener("DOMContentLoaded", () => {
  const successMessage = document.getElementById("success-message");
  const decryptBtn = document.getElementById("decrypt-btn");
  const uploadBtn = document.getElementById("upload-btn");


  successMessage.style.display = "block";


  decryptBtn.addEventListener("click", () => {
    
    fetch("/success", {
      method: "POST"
    })
    .then(response => {
      if (response.ok) {
        alert("Decryption request sent.");
      } else {
        alert("Decryption failed.");
      }
    })
    .catch(() => alert("Something went wrong."));
  });


  uploadBtn.addEventListener("click", () => {
    window.location.href = "/upload";
  });
});
