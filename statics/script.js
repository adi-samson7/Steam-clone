document.addEventListener("DOMContentLoaded", function () {
    showSection("home");
    updateCartCount();
    loadStore();
    loadCart();
    updateCategoryButtons();
    updateCartCount();
    fetchGames(); // Fetch games from backend
    loadCart();
    updateCategoryButtons();
});


// SECTION DISPLAY FUNCTION
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });

    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.style.display = 'flex';
        selectedSection.style.flexDirection = 'column';
        selectedSection.style.alignItems = 'center';
        selectedSection.style.justifyContent = 'center';
        selectedSection.style.width = '100%';
    }

    if (sectionId === 'store') loadStore();
    if (sectionId === 'cart') loadCart();
    if (sectionId === 'library') fetchLibrary(); // NEW: fetch library when library section is shown
}

// CATEGORY SLIDER FUNCTIONALITY
const categorySlider = document.querySelector('.category-slider');
const prevCategoryBtn = document.querySelector('.left-btn');  // left arrow
const nextCategoryBtn = document.querySelector('.right-btn'); // right arrow

function updateCategoryButtons() {
    if (!categorySlider) return;
    prevCategoryBtn.style.display = categorySlider.scrollLeft > 0 ? 'block' : 'none';
    nextCategoryBtn.style.display =
        categorySlider.scrollLeft + categorySlider.clientWidth < categorySlider.scrollWidth ? 'block' : 'none';
}

function scrollCategories(direction) {
    const cardWidth = document.querySelector('.category-card').offsetWidth + 10;
    const visibleCards = 6; 
    categorySlider.scrollBy({ left: direction * cardWidth * visibleCards, behavior: 'smooth' });
    setTimeout(updateCategoryButtons, 500);
}

if (categorySlider) {
    categorySlider.addEventListener('scroll', updateCategoryButtons);
}

// GAME RECOMMENDATION SLIDER
const slides = document.querySelectorAll('.slide');
let currentSlide = 0;

function changeSlide(direction) {
    slides[currentSlide].style.display = "none"; 
    currentSlide = (currentSlide + direction + slides.length) % slides.length;
    slides[currentSlide].style.display = "flex";
    slides[currentSlide].style.alignItems = "center";
    slides[currentSlide].style.justifyContent = "center";
}

// Auto-slide every 3 seconds
setInterval(() => {
    changeSlide(1);
}, 5000);

document.addEventListener("DOMContentLoaded", () => {
    slides.forEach((slide, index) => {
        slide.style.display = index === 0 ? "flex" : "none";
        slide.style.alignItems = "center";
        slide.style.justifyContent = "center";
    });
});

// all working till here.........................................................................................

// ✅ Fetch Games from Backend
async function fetchGames() {
    try {
        const response = await fetch("http://127.0.0.1:8000/games"); // Ensure correct API path
        if (!response.ok) throw new Error("Failed to fetch games.");
        const data = await response.json();
        
        localStorage.setItem("games", JSON.stringify(data.games)); // Store in local storage
        loadStore();
    } catch (error) {
        console.error("Error fetching games:", error);
    }
}

// ✅ Load Store Games
function loadStore() {
    const storeContainer = document.getElementById("store-items");
    if (!storeContainer) return;
    storeContainer.innerHTML = "";
    storeContainer.style.display = "flex";
    storeContainer.style.flexWrap = "wrap";
    storeContainer.style.justifyContent = "center";

    let games = JSON.parse(localStorage.getItem("games")) || [];
    let filteredGames = currentCategory === "all" ? games : games.filter(game => game.category.includes(currentCategory));

    filteredGames.forEach(game => {
        let gameCard = document.createElement("div");
        gameCard.classList.add("game-card");
        gameCard.innerHTML = `
            <h3>${game.name}</h3>
            <p><strong>Category:</strong> ${game.category}</p>
            <p><strong>Year:</strong> ${game.year}</p>
            <p><strong>Price:</strong> ₹${game.price.toFixed(2)}</p>
            <button onclick="addToCart(${game.id})">${isInCart(game.id) ? "In Cart" : "Add to Cart"}</button>
        `;
        storeContainer.appendChild(gameCard);
    });
}

// ✅ Show Games by Category
function showCategory(categoryName) {
    currentCategory = categoryName;
    showSection("store");
}

// ✅ Fetch and Display Games by Category
function showCategoryPage(category) {
    fetch(`http://127.0.0.1:8000/games/${encodeURIComponent(category)}`)
        .then(response => response.json())
        .then(data => {
            let categoryGamesContainer = document.getElementById("category-games");
            categoryGamesContainer.innerHTML = "";

            if (data.message) {
                categoryGamesContainer.innerHTML = `<p>${data.message}</p>`;
                return;
            }

            data.games.forEach(game => {
                let gameCard = document.createElement("div");
                gameCard.classList.add("game-card");
                gameCard.innerHTML = `
                    <h3>${game.name}</h3>
                    <p>Price: ₹${game.price.toFixed(2)}</p>
                    <button class="add-to-cart" data-id="${game.id}" onclick="addToCart(${game.id})">
                         ${isInCart(game.id) ? "In Cart" : "Add to Cart"}
                    </button>
                `;
                categoryGamesContainer.appendChild(gameCard);
            });

            document.querySelectorAll(".section").forEach(section => section.style.display = "none");
            document.getElementById("category-page").style.display = "block";
            document.getElementById("category-title").innerText = category;
        })
        .catch(error => console.error("Error fetching category games:", error));
}
// all working till here.........................................................................................

// SCROLL BUTTONS FOR CATEGORY SLIDER
function scrollLeft(id) {
    document.getElementById(id).scrollBy({ left: -220, behavior: 'smooth' });
}

function scrollRight(id) {
    document.getElementById(id).scrollBy({ left: 220, behavior: 'smooth' });
}

// NEW: Fetch and Display User Library (Purchased Games)
function fetchLibrary() {
    // Retrieve current user details from sessionStorage
    const currentUser = {
        username: sessionStorage.getItem("user_name"),
        email: sessionStorage.getItem("user_email")
    };
    if (!currentUser.email) {
        alert("Please login to view your library.");
        return;
    }
    // Fetch purchased games for the current user
    fetch(`http://127.0.0.1:8000/api/user-library?email=${encodeURIComponent(currentUser.email)}`)
        .then(response => response.json())
        .then(data => {
            const libraryList = document.getElementById("libraryList");
            libraryList.innerHTML = ""; // Clear previous entries

            if (data.library && data.library.length > 0) {
                data.library.forEach(item => {
                    const li = document.createElement("li");
                    li.textContent = item.game_name; // Display only game name
                    libraryList.appendChild(li);
                });
            } else {
                libraryList.innerHTML = "<p>You haven't purchased any games yet.</p>";
            }
        })
        .catch(error => console.error("Error fetching library:", error));
}
