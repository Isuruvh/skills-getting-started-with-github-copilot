document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const submitButton = signupForm.querySelector('button[type="submit"]');
  let isSubmitting = false;

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participants = details.participants || [];

        const participantsSection = participants.length
          ? `
            <ul class="participants-list">
              ${participants.map((participant) => `
                <li>
                  <span>${participant}</span>
                  <button class="remove-btn" data-activity="${name}" data-email="${participant}" title="Unregister">🗑️</button>
                </li>`).join("")}
            </ul>
          `
          : '<p class="participants-empty">No participants yet. Be the first to sign up!</p>';

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <p class="participants-title">Participants (${participants.length})</p>
            ${participantsSection}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Wire up unregister buttons
        activityCard.querySelectorAll(".remove-btn").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const activity = btn.dataset.activity;
            const email = btn.dataset.email;
            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
                { method: "DELETE" }
              );
              if (response.ok) {
                fetchActivities();
              } else {
                const result = await response.json();
                console.error("Unregister failed:", result.detail);
              }
            } catch (error) {
              console.error("Error unregistering:", error);
            }
          });
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (isSubmitting) {
      return;
    }

    const emailInput = document.getElementById("email");
    const email = emailInput.value.trim().toLowerCase();
    const activity = document.getElementById("activity").value;

    if (!email) {
      messageDiv.textContent = "Please enter a valid email.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      return;
    }

    isSubmitting = true;
    submitButton.disabled = true;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        await fetchActivities();
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    } finally {
      isSubmitting = false;
      submitButton.disabled = false;
    }
  });

  // Initialize app
  fetchActivities();
});
