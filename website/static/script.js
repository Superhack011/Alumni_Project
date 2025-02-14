function toggleStar(icon) {
    if (icon.classList.contains('text-warning')) {
      icon.classList.remove('text-warning'); // Removes gold color
      icon.classList.add('text-secondary'); // Adds white/grey color
    } else {
      icon.classList.remove('text-secondary'); // Removes white/grey color
      icon.classList.add('text-warning'); // Adds gold color
    }
  }
  


  let page = 1;
  document.addEventListener("DOMContentLoaded", function () {
      loadReviews(); // Load initial reviews
  
      document.getElementById("load-more-btn").addEventListener("click", function () {
          loadReviews();
      });
  });
  
  function loadReviews() {
      fetch(`/load_reviews?page=${page}`)
          .then(response => response.json())
          .then(data => {
              if (data.reviews.length > 0) {
                  const container = document.getElementById("reviews-container");
                  data.reviews.forEach(review => {
                      let starsHtml = "";
                      for (let i = 0; i < review.stars; i++) {
                          starsHtml += "⭐"; // Generate stars dynamically
                      }
  
                      let reviewCard = `
                          <div class="review-card">
                              <div class="review-header">
                                  <img src="/static/${review.member_image_path}" alt="Member Profile" class="profile-pic" />
                                  <div class="review-info">
                                      <p class="review-name">${review.name}</p>
                                      <p class="review-stars">${starsHtml}</p>
                                  </div>
                              </div>
                              <p class="review-text">${review.review_text}</p>
                              <p class="review-date">${review.created_at}</p>
                          </div>`;
                      
                      container.innerHTML += reviewCard;
                  });
                  page++; // Increase page count
              } else {
                  document.getElementById("load-more-btn").style.display = "none"; // Hide button when no more reviews
              }
          })
          .catch(error => console.error("Error loading reviews:", error));
  }
  