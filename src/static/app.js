document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";
        activityCard.dataset.activityName = name;

        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants list HTML
        let participantsHTML = '';
        if (details.participants.length > 0) {
          participantsHTML = `
            <div class="participants-section">
              <strong>Participants:</strong>
              <ul class="participants-list">
                ${details.participants.map(email => `
                  <li class="participant-item">
                    <span>${email}</span>
                    <button class="delete-btn" data-activity="${name}" data-email="${email}" title="Unregister">✕</button>
                  </li>
                `).join('')}
              </ul>
            </div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners for delete buttons
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Function to handle unregistering a participant
  async function handleUnregister(event) {
    const button = event.target;
    const activityName = button.dataset.activity;
    const email = button.dataset.email;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        // Refresh activities to show updated list
        await fetchActivities();
        
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");

        // Hide message after 5 seconds
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      } else {
        messageDiv.textContent = result.detail || "Failed to unregister";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        // Refresh activities to show updated list
        await fetchActivities();
        
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
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
    }
  });

  // Initialize app
  fetchActivities();
});
