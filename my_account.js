document.addEventListener("DOMContentLoaded", async () => {
  const userGreeting = document.getElementById("user-greeting");
  const videoCount = document.getElementById("video-count");
  const videoList = document.getElementById("video-list");

  try {
    const res = await fetch("/api/user-info");
    const data = await res.json();

    userGreeting.textContent = `Welcome, ${data.username}!`;
    videoCount.textContent = `You have uploaded ${data.video_count} video(s).`;

    if (data.videos.length === 0) {
      videoList.innerHTML = "<p>No videos uploaded yet.</p>";
    } else {
      data.videos.forEach(video => {
        const card = document.createElement("div");
        card.className = "video-card";

        card.innerHTML = `
          <div class="video-preview">
            <h3>${video.filename}</h3>
            <video width="300" controls>
              <source src="/upload/${video.filename}" type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
          <div class="actions">
            <a href="/upload/encrypted_${video.filename}">Download Encrypted</a>
            <button data-video-id="${video.id}" class="decrypt-btn">Decrypt</button>
          </div>
        `;

        videoList.appendChild(card);
      });

      // Attach event listeners for all decrypt buttons
      document.querySelectorAll(".decrypt-btn").forEach(btn => {
        btn.addEventListener("click", async (e) => {
          const videoId = btn.getAttribute("data-video-id");

          const response = await fetch("/api/decrypt", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ video_id: videoId })
          });

          const result = await response.json();
          if (response.ok) {
            alert("Decryption successful!");
          } else {
            alert(result.error || "Decryption failed.");
          }
        });
      });
    }
  } catch (err) {
    console.error("Error loading dashboard:", err);
    videoList.innerHTML = "<p>Error loading videos. Please try again later.</p>";
  }

  // Logout Handler
  document.getElementById("logout-link").addEventListener("click", async (e) => {
    e.preventDefault();
    const res = await fetch("/logout", { method: "POST" });
    if (res.ok) {
      window.location.href = "/login";
    }
  });
});
