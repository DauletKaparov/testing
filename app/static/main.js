const scanBtn = document.getElementById("scan-btn");
const periodSelect = document.getElementById("period");
const industrySelect = document.getElementById("industry");
const resultsDiv = document.getElementById("results");

scanBtn.addEventListener("click", async () => {
  const period = periodSelect.value;
  const industry = industrySelect.value;
  resultsDiv.textContent = "Scanning...";

  try {
    const res = await fetch(`/scan?period=${period}&industry=${industry}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.length === 0) {
      resultsDiv.textContent = "No articles found in this timeframe.";
      return;
    }
    resultsDiv.innerHTML = data
      .map(
        (item, idx) => `
        <div class="news-card" style="border:1px solid #ccc; padding:1rem; margin-bottom:1rem;">
          <h3 style="margin:0 0 0.5rem 0;"><a href="${item.url || '#'}" target="_blank">${item.title}</a></h3>
          <p style="margin:0 0 0.5rem 0;"><strong>Score:</strong> ${item.score.toFixed(1)}/10</p>
          <button class="toggle-btn" data-idx="${idx}">More</button>
          <div class="details" id="details-${idx}" style="display:none; margin-top:0.5rem;">
            <p><strong>Brief:</strong> ${item.brief}</p>
            <p><strong>Why it matters:</strong> ${item.why_matters}</p>
            <p><strong>Tickers:</strong> ${item.tickers.length ? item.tickers.join(', ') : '<em>None</em>'}</p>
            <p><strong>Prediction:</strong> ${Object.keys(item.prediction).length ? Object.entries(item.prediction).map(([t, p]) => `${t}: ${p}`).join(', ') : '<em>N/A</em>'}</p>
          </div>
        </div>`
      )
      .join("");

    // attach toggle listeners
    document.querySelectorAll('.toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = btn.dataset.idx;
        const detailDiv = document.getElementById(`details-${idx}`);
        if (detailDiv.style.display === 'none') {
          detailDiv.style.display = 'block';
          btn.textContent = 'Less';
        } else {
          detailDiv.style.display = 'none';
          btn.textContent = 'More';
        }
      });
    });
  } catch (err) {
    resultsDiv.textContent = err.message;
  }
});
