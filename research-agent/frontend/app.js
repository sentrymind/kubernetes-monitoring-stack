// Research Agent Frontend JavaScript

const API_BASE = window.location.origin;

let currentPapers = [];
let currentSearchTime = 0;

// Search form submission
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await performSearch();
});

async function performSearch() {
    const query = document.getElementById('query').value;
    const semanticSearch = document.getElementById('semanticSearch').checked;
    const startYear = document.getElementById('startYear').value || null;
    const endYear = document.getElementById('endYear').value || null;
    const maxResults = parseInt(document.getElementById('maxResults').value) || 50;

    // Get selected sources
    const sourceCheckboxes = document.querySelectorAll('input[name="sources"]:checked');
    const sources = Array.from(sourceCheckboxes).map(cb => cb.value);

    if (sources.length === 0) {
        alert('Please select at least one source');
        return;
    }

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('analysis-section').style.display = 'none';

    // Build request
    const request = {
        query: query,
        sources: sources,
        max_results: maxResults,
        semantic_search: semanticSearch
    };

    if (startYear) request.start_year = parseInt(startYear);
    if (endYear) request.end_year = parseInt(endYear);

    try {
        const response = await fetch(`${API_BASE}/api/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        currentPapers = data.papers;
        currentSearchTime = data.search_time;

        displayResults(data);

    } catch (error) {
        console.error('Search error:', error);
        alert('Search failed: ' + error.message);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function displayResults(data) {
    // Show results section
    document.getElementById('results-section').style.display = 'block';

    // Display statistics
    displayStats(data);

    // Display papers
    displayPapers(data.papers);
}

function displayStats(data) {
    const statsHtml = `
        <div class="stat-card">
            <span class="stat-value">${data.total_results}</span>
            <span class="stat-label">Papers Found</span>
        </div>
        <div class="stat-card">
            <span class="stat-value">${data.search_time.toFixed(2)}s</span>
            <span class="stat-label">Search Time</span>
        </div>
        <div class="stat-card">
            <span class="stat-value">${data.query.length > 30 ? data.query.substring(0, 30) + '...' : data.query}</span>
            <span class="stat-label">Query</span>
        </div>
    `;

    document.getElementById('stats').innerHTML = statsHtml;
}

function displayPapers(papers) {
    const papersList = document.getElementById('papers-list');
    document.getElementById('paper-count').textContent = `(${papers.length})`;

    if (papers.length === 0) {
        papersList.innerHTML = '<p>No papers found. Try a different query.</p>';
        return;
    }

    const papersHtml = papers.map(paper => {
        const sourceBadge = paper.source === 'pubmed'
            ? '<span class="badge badge-pubmed">PubMed</span>'
            : '<span class="badge badge-arxiv">arXiv</span>';

        const similarityBadge = paper.similarity_score
            ? `<span class="badge similarity-score">Similarity: ${(paper.similarity_score * 100).toFixed(1)}%</span>`
            : '';

        const authors = paper.authors.slice(0, 3).join(', ') +
                       (paper.authors.length > 3 ? ' et al.' : '');

        const year = paper.year || 'N/A';
        const journal = paper.journal || 'N/A';

        const abstract = paper.abstract.length > 500
            ? paper.abstract.substring(0, 500) + '...'
            : paper.abstract;

        return `
            <div class="paper-card">
                <div class="paper-title">
                    <a href="${paper.url}" target="_blank">${paper.title}</a>
                </div>
                <div class="paper-authors">${authors}</div>
                <div class="paper-meta">
                    ${sourceBadge}
                    ${similarityBadge}
                    <span>Year: ${year}</span>
                    <span>Journal: ${journal}</span>
                </div>
                <div class="paper-abstract">${abstract}</div>
            </div>
        `;
    }).join('');

    papersList.innerHTML = papersHtml;
}

async function createVisualization(type) {
    if (currentPapers.length === 0) {
        alert('Please search for papers first');
        return;
    }

    const vizContainer = document.getElementById('visualization-container');
    vizContainer.innerHTML = '<div class="loading"><div class="spinner"></div><p>Creating visualization...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/api/visualize/${type}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentPapers)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success && data.file) {
            const filename = data.file.split('/').pop();
            const fileUrl = `${API_BASE}/visualizations/${filename}`;

            if (data.file.endsWith('.html')) {
                vizContainer.innerHTML = `<iframe src="${fileUrl}" width="100%" height="600" frameborder="0"></iframe>`;
            } else {
                vizContainer.innerHTML = `<img src="${fileUrl}" alt="${type} visualization" style="max-width: 100%; height: auto;">`;
            }
        } else {
            throw new Error('Visualization failed');
        }

    } catch (error) {
        console.error('Visualization error:', error);
        vizContainer.innerHTML = `<p style="color: red;">Visualization failed: ${error.message}</p>`;
    }
}

async function analyzeResults() {
    if (currentPapers.length === 0) {
        alert('Please search for papers first');
        return;
    }

    const analysisSection = document.getElementById('analysis-section');
    const analysisContent = document.getElementById('analysis-content');

    analysisSection.style.display = 'block';
    analysisContent.innerHTML = '<div class="loading"><div class="spinner"></div><p>Analyzing papers...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentPapers)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        displayAnalysis(data);

    } catch (error) {
        console.error('Analysis error:', error);
        analysisContent.innerHTML = `<p style="color: red;">Analysis failed: ${error.message}</p>`;
    }
}

function displayAnalysis(data) {
    const analysisContent = document.getElementById('analysis-content');

    // Summary statistics
    let summaryHtml = '<h3>Summary Statistics</h3><ul class="analysis-list">';
    summaryHtml += `<li>Total Papers: ${data.summary.total_papers}</li>`;
    summaryHtml += `<li>Total Authors: ${data.summary.total_authors}</li>`;
    summaryHtml += `<li>Date Range: ${data.summary.date_range.start} - ${data.summary.date_range.end}</li>`;
    summaryHtml += `<li>Avg Authors per Paper: ${data.summary.avg_authors_per_paper.toFixed(2)}</li>`;
    summaryHtml += '</ul>';

    // Top keywords
    let keywordsHtml = '<h3>Top Keywords</h3><ul class="analysis-list">';
    for (const [keyword, count] of Object.entries(data.top_keywords).slice(0, 15)) {
        keywordsHtml += `<li>${keyword}: ${count}</li>`;
    }
    keywordsHtml += '</ul>';

    // Top authors
    let authorsHtml = '<h3>Top Authors</h3><ul class="analysis-list">';
    for (const author of data.top_authors.slice(0, 10)) {
        authorsHtml += `<li>${author.author} (${author.paper_count} papers)</li>`;
    }
    authorsHtml += '</ul>';

    // Top journals
    let journalsHtml = '<h3>Top Journals</h3><ul class="analysis-list">';
    for (const journal of data.top_journals.slice(0, 10)) {
        journalsHtml += `<li>${journal.journal} (${journal.paper_count} papers)</li>`;
    }
    journalsHtml += '</ul>';

    const html = `
        <div class="analysis-grid">
            <div class="analysis-card">${summaryHtml}</div>
            <div class="analysis-card">${keywordsHtml}</div>
            <div class="analysis-card">${authorsHtml}</div>
            <div class="analysis-card">${journalsHtml}</div>
        </div>
    `;

    analysisContent.innerHTML = html;
}

// Health check on page load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();
        console.log('API Health:', data);
    } catch (error) {
        console.error('API health check failed:', error);
    }
});
