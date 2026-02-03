let currentPage = 1;
const itemsPerPage = 6;
let pageWindow = 5; // عدد الأرقام الظاهرة في pagination
let originalNews = [...newsData];

/* Render News */
function renderNews() {
    const grid = document.getElementById("newsGrid");
    grid.innerHTML = "";

    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageItems = newsData.slice(start, end); // الأخبار الخاصة بالصفحة فقط

    pageItems.forEach((item, index) => {
        const globalIndex = start + index; // رقم عالمي لكل عنصر
        grid.innerHTML += `
            <div class="news-card">
                <h2>${item.title}</h2>
                <span class="date">${item.publishDate}</span>
                <p class="short-text">${item.content.substring(0,140)}...</p>
                <p class="full-text" id="full-${globalIndex}">${item.content}</p>
                <button class="more-btn" onclick="toggleMore(${globalIndex}, this)">Read More</button>
            </div>
        `;
    });

    renderPagination();
}

/* Toggle Read More / Less */
function toggleMore(index, btn) {
    const text = document.getElementById(`full-${index}`);
    if (text.style.display === "block") {
        text.style.display = "none";
        btn.innerText = "Read More";
    } else {
        text.style.display = "block";
        btn.innerText = "Read Less";
    }
}

/* Apply Filter */
function applyFilter() {
    const filterValue = document.getElementById("dateFilter").value;

    if(filterValue === "all") newsData = [...originalNews];
    else if(filterValue === "new") newsData = [...originalNews].sort((a,b) => new Date(b.publishDate)-new Date(a.publishDate));
    else if(filterValue === "old") newsData = [...originalNews].sort((a,b) => new Date(a.publishDate)-new Date(b.publishDate));

    currentPage = 1;
    renderNews();
}

/* Pagination */
function renderPagination() {
    const totalPages = Math.ceil(newsData.length / itemsPerPage);
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    let startPage = Math.floor((currentPage-1)/pageWindow)*pageWindow + 1;
    let endPage = Math.min(startPage + pageWindow -1, totalPages);

    for(let i=startPage; i<=endPage; i++) {
        pagination.innerHTML += `
            <button class="${i===currentPage?'active':''}" onclick="changePage(${i})">${i}</button>
        `;
    }

    document.getElementById("morePagesBtn").style.display = (endPage < totalPages) ? "inline-block" : "none";
}

/* Change Page */
function changePage(page) {
    currentPage = page;
    renderNews();
}

/* More Pages Button */
function loadMorePages() {
    const totalPages = Math.ceil(newsData.length / itemsPerPage);
    let startPage = Math.floor((currentPage-1)/pageWindow)*pageWindow + 1;
    let endPage = Math.min(startPage + pageWindow -1, totalPages);

    if(endPage < totalPages) {
        currentPage = endPage + 1; // تحديث الصفحة الحالية
        renderNews();             // إعادة عرض الأخبار الجديدة فقط
    }
}

/* Init */
renderNews();
