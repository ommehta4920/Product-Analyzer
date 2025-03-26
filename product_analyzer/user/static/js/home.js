// JavaScript for interactivity (if needed)
document.getElementById('searchForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const searchQuery = document.getElementById('searchInput').value;
    if (searchQuery) {
      alert(`You searched for: ${searchQuery}`);
      // You can add functionality to handle the search query here
    } else {
      alert('Please enter a search term.');
    }
  });