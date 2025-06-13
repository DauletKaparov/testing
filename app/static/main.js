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
        (item) => `
        <div style="border:1px solid #ccc; padding:1rem; margin-bottom:1rem;">
          <h3><a href="${item.url || '#'}" target="_blank">${item.title}</a></h3>
          <p><strong>Brief:</strong> ${item.brief}</p>
          <p><strong>Why it matters:</strong> ${item.why_matters}</p>
          <p><strong>Relevancy Score:</strong> ${item.score.toFixed(1)}/10</p>
          <p><strong>Tickers:</strong> ${item.tickers.join(', ') || 'None'}</p>
          <p><strong>Prediction:</strong> ${Object.entries(item.prediction)
            .map(([t, p]) => `${t}: ${p}`)
            .join(', ') || 'N/A'}</p>
        </div>`
      )
      .join("");
  } catch (err) {
    resultsDiv.textContent = err.message;
  }
});
