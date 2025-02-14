function toggleStar(icon) {
    if (icon.classList.contains('text-warning')) {
      icon.classList.remove('text-warning'); // Removes gold color
      icon.classList.add('text-secondary'); // Adds white/grey color
    } else {
      icon.classList.remove('text-secondary'); // Removes white/grey color
      icon.classList.add('text-warning'); // Adds gold color
    }
  }
  