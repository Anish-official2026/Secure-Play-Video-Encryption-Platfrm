document.addEventListener("DOMContentLoaded", () => {
  const signupForm = document.getElementById("signup-form");

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault(); 

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
      alert("Please fill in all fields.");
      return;
    }

    try {
      const response = await fetch("/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
      });

      const result = await response.json();

      if (response.ok) {
        alert(result.message || "Signup successful!");
        window.location.href = "/login"; 
      } else {
        alert(result.error || "Signup failed.");
      }
    } catch (error) {
      alert("Something went wrong. Please try again.");
      console.error(error);
    }
  });
});
