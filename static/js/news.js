// ===== Configuration =====
let currentPage = 1;
const itemsPerPage = 10; // must match Flask limit
const pageWindow = 3;    // 3 pages before & after

// Fetch news from server dynamically
async function fetchNews(page = 1, sortType = "new", query = "") {
    const response = await fetch(`/news-data?page=${page}&sort=${sortType}&q=${encodeURIComponent(query)}`);
    const data = await response.json();
    return data; // { news: [...], total: x, current: y }
}

// ===== Render News Cards =====
function renderNewsCards(newsItems) {
    const grid = document.querySelector(".news-grid");
    grid.innerHTML = "";

    if (newsItems.length === 0) {
        grid.innerHTML = `<div class="no-results"><p>No news found</p></div>`;
        return;
    }

    newsItems.forEach((n, index) => {
        const card = document.createElement("div");
        card.classList.add("news-card");

        card.innerHTML = `
            <span class="category-tag">${n.category}</span>
            <h3>${n.title}</h3>
            <p class="summary">${n.summary}</p>
            <p class="full-text">${n.content}</p>
            <button class="more-btn">Read More</button>
            <div class="news-footer">
                <span class="author">By: ${n.author}</span>
                <span class="date">${n.publishDate}</span>
            </div>
        `;
        grid.appendChild(card);
    });

    // Attach Read More toggle
    const buttons = document.querySelectorAll(".more-btn");
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            const card = btn.closest(".news-card");
            const fullText = card.querySelector(".full-text");
            const summary = card.querySelector(".summary");

            if (fullText.style.display === "block") {
                fullText.style.display = "none";
                summary.style.display = "block";
                btn.innerText = "Read More";
            } else {
                fullText.style.display = "block";
                summary.style.display = "none";
                btn.innerText = "Read Less";
            }
        });
    });
}

// ===== Render Pagination =====
function renderPagination(totalPages) {
    const pagination = document.querySelector(".pagination");
    pagination.innerHTML = "";

    // Previous Button
    if (currentPage > 1) {
        const prev = document.createElement("a");
        prev.innerText = "Previous";
        prev.href = "#";
        prev.addEventListener("click", e => {
            e.preventDefault();
            changePage(currentPage - 1);
        });
        pagination.appendChild(prev);
    }

    // Page numbers (dynamic window)
    const startPage = Math.max(currentPage - pageWindow, 1);
    const endPage = Math.min(currentPage + pageWindow, totalPages);

    for (let i = startPage; i <= endPage; i++) {
        if (i === currentPage) {
            const btn = document.createElement("button");
            btn.classList.add("active");
            btn.innerText = i;
            pagination.appendChild(btn);
        } else {
            const link = document.createElement("a");
            link.innerText = i;
            link.href = "#";
            link.addEventListener("click", e => {
                e.preventDefault();
                changePage(i);
            });
            pagination.appendChild(link);
        }
    }

    // Next Button
    if (currentPage < totalPages) {
        const next = document.createElement("a");
        next.innerText = "Next";
        next.href = "#";
        next.addEventListener("click", e => {
            e.preventDefault();
            changePage(currentPage + 1);
        });
        pagination.appendChild(next);
    }
}

// ===== Change Page =====
async function changePage(page) {
    const query = document.querySelector("input[name='q']").value || "";
    const sortType = document.querySelector("select[name='sort']").value || "new";

    currentPage = page;

    const data = await fetchNews(currentPage, sortType, query);
    renderNewsCards(data.news);

    const totalPages = Math.ceil(data.total / itemsPerPage);
    renderPagination(totalPages);

    // Scroll to top of news
    window.scrollTo({ top: 160, behavior: "smooth" });
}

// ===== Apply Filter / Search =====
document.querySelector(".search-form").addEventListener("submit", async e => {
    e.preventDefault();
    currentPage = 1;

    const query = document.querySelector("input[name='q']").value || "";
    const sortType = document.querySelector("select[name='sort']").value || "new";

    const data = await fetchNews(currentPage, sortType, query);
    renderNewsCards(data.news);

    const totalPages = Math.ceil(data.total / itemsPerPage);
    renderPagination(totalPages);
});

// ===== Initial Load =====
window.addEventListener("DOMContentLoaded", async () => {
    const data = await fetchNews(currentPage);
    renderNewsCards(data.news);
    const totalPages = Math.ceil(data.total / itemsPerPage);
    renderPagination(totalPages);
});
