const categoryFilter = document.getElementById("filter-category"); // Fixed capital 'F' to small 'f'
const stageFilter = document.getElementById("filter-stage");
const searchFilter = document.getElementById("filter-search");
const ideaCards = document.querySelectorAll(".idea-card");

function applyFilters() {
    const category = categoryFilter.value;
    const stage = stageFilter.value;
    const search = searchFilter.value.toLowerCase(); // Fixed typo: 'toLowecase' to 'toLowerCase'

    ideaCards.forEach((card) => {
        const matchesCategory = !category || card.dataset.category === category;
        const matchesStage = !stage || card.dataset.stage === stage;
        const matchesSearch = !search || card.querySelector("h3").textContent.toLowerCase().includes(search); // Fixed typo: 'matchsSearch' to 'matchesSearch'

        if (matchesCategory && matchesStage && matchesSearch) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    });
}

if (categoryFilter) {
    categoryFilter.addEventListener("change", applyFilters); // Fixed typo: 'addEvebtListener' to 'addEventListener'
    stageFilter.addEventListener("change", applyFilters);
    searchFilter.addEventListener("input", applyFilters);
}
