document.addEventListener("DOMContentLoaded", function () {
  const chatForm = document.getElementById("chat-form");
  const chatBox = document.getElementById("chat-box");

  chatForm.addEventListener("submit", function (event) {
    event.preventDefault();
    let message = document.getElementById("message").value.trim();
    if (message) {
      fetch(window.location.pathname, {
        method: "POST",
        body: new URLSearchParams({ message: message }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      })
        .then((response) => response.json())
        .then(() => {
          location.reload(); // Refresh to show new messages
        });
    }
  });

  chatBox.scrollTop = chatBox.scrollHeight;
});
