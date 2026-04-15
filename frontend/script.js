// ============================================================
// GameIQ - Dashboard Logic
// ============================================================

const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" 
    ? "http://localhost:3000/api" 
    : "/api";

document.addEventListener("DOMContentLoaded", () => {
    checkApi();
    initCharts();
    setupToggles();
});

// ── API Status ──
async function checkApi() {
    const badge = document.getElementById("apiBadge");
    const dot = badge.querySelector(".api-dot");
    try {
        const r = await fetch(API_BASE + "/health");
        if (r.ok) {
            dot.classList.add("online");
            badge.lastChild.textContent = " Connected";
        }
    } catch {
        dot.classList.add("offline");
        badge.lastChild.textContent = " Offline";
    }
}

// ── Toggle Buttons ──
function setupToggles() {
    // Retention
    document.getElementById("retYes").addEventListener("click", () => {
        toggle("retYes", "retNo", "inputRetention", "1");
    });
    document.getElementById("retNo").addEventListener("click", () => {
        toggle("retNo", "retYes", "inputRetention", "0");
    });

    // Version
    document.getElementById("ver30").addEventListener("click", () => {
        toggle("ver30", "ver40", "inputVersion", "gate_30");
    });
    document.getElementById("ver40").addEventListener("click", () => {
        toggle("ver40", "ver30", "inputVersion", "gate_40");
    });
}

function toggle(onId, offId, hiddenId, value) {
    document.getElementById(onId).classList.add("selected");
    document.getElementById(offId).classList.remove("selected");
    // set hidden input if it exists, else store on button
    var hidden = document.getElementById(hiddenId);
    if (hidden) hidden.value = value;
}

// ── Prediction ──
async function predictChurn() {
    var btn = document.getElementById("predictBtn");
    var rounds = Number(document.getElementById("inputRounds").value);

    // read from toggle state
    var retention_1 = document.getElementById("retYes").classList.contains("selected") ? 1 : 0;
    var version = document.getElementById("ver30").classList.contains("selected") ? "gate_30" : "gate_40";

    if (isNaN(rounds) || rounds < 0) {
        alert("Enter a valid number of rounds.");
        return;
    }

    btn.classList.add("loading");
    btn.textContent = "Predicting...";

    try {
        var res = await fetch(API_BASE + "/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rounds: rounds, retention_1: retention_1, version: version })
        });
        var data = await res.json();

        if (data.success) {
            showResult(data.data);
        } else {
            alert("Error: " + (data.error || "Unknown"));
        }
    } catch (err) {
        alert("Cannot connect to API. Are both servers running?");
    } finally {
        btn.classList.remove("loading");
        btn.textContent = "Run Prediction";
    }
}

function showResult(d) {
    document.getElementById("resultPlaceholder").style.display = "none";
    var content = document.getElementById("resultContent");
    content.classList.remove("hidden");

    var isChurn = d.prediction === 1 || d.churn === 1;
    var retPct = d.details ? d.details.retain_probability : (d.probabilities ? d.probabilities.retain : 0);
    var churnPct = d.details ? d.details.churn_probability : (d.probabilities ? d.probabilities.churn : 0);
    var conf = d.probability || d.confidence || Math.max(retPct, churnPct);

    // Verdict badge
    var badge = document.getElementById("resultBadge");
    badge.className = "result-verdict " + (isChurn ? "churned" : "retained");
    document.getElementById("resultLabel").textContent = isChurn ? "Likely to Churn" : "Likely to Stay";

    // Ring
    var circumference = 2 * Math.PI * 42;
    var offset = circumference - (conf / 100) * circumference;
    var ring = document.getElementById("ringFill");
    ring.style.strokeDashoffset = offset;
    ring.className = "ring-progress " + (isChurn ? "churned" : "retained");
    document.getElementById("ringValue").textContent = conf.toFixed(1) + "%";

    // Bars
    setTimeout(function () {
        document.getElementById("retainBar").style.width = retPct + "%";
        document.getElementById("churnBar").style.width = churnPct + "%";
    }, 150);
    document.getElementById("retainProb").textContent = retPct.toFixed(1) + "%";
    document.getElementById("churnProb").textContent = churnPct.toFixed(1) + "%";

    // Note
    var input = d.input_received || d.input || {};
    document.getElementById("resultDetails").innerHTML =
        "<strong>Input:</strong> " + (input.rounds || "N/A") + " rounds, " +
        "Day 1: " + (input.retention_1 == 1 ? "Yes" : "No") + ", " +
        (input.version || "N/A") + "<br>" +
        (isChurn
            ? "This player profile shows disengagement signals. Consider re-engagement notifications or difficulty adjustment."
            : "This player appears engaged and likely to continue. Consider offering premium content to deepen retention.");
}

// ── Charts ──
function initCharts() {
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = "#6b7280";

    // Churn doughnut
    new Chart(document.getElementById("churnPieChart"), {
        type: "doughnut",
        data: {
            labels: ["Churned (81.4%)", "Retained (18.6%)"],
            datasets: [{
                data: [81.4, 18.6],
                backgroundColor: ["#fca5a5", "#6ee7b7"],
                borderColor: ["#fee2e2", "#d1fae5"],
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "60%",
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { padding: 16, usePointStyle: true, pointStyleWidth: 10, font: { size: 12 } }
                }
            }
        }
    });

    // Retention bar
    new Chart(document.getElementById("retentionBarChart"), {
        type: "bar",
        data: {
            labels: ["Day 1 Retention", "Day 7 Retention"],
            datasets: [
                {
                    label: "gate_30",
                    data: [44.82, 19.02],
                    backgroundColor: "#818cf8",
                    borderRadius: 4,
                    barPercentage: 0.6
                },
                {
                    label: "gate_40",
                    data: [44.23, 18.20],
                    backgroundColor: "#c4b5fd",
                    borderRadius: 4,
                    barPercentage: 0.6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 55,
                    ticks: { callback: function (v) { return v + "%"; } },
                    grid: { color: "#f3f4f6" }
                },
                x: { grid: { display: false } }
            },
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { padding: 16, usePointStyle: true, font: { size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: function (ctx) { return ctx.dataset.label + ": " + ctx.parsed.y + "%"; }
                    }
                }
            }
        }
    });

    // Engagement bar
    new Chart(document.getElementById("engagementChart"), {
        type: "bar",
        data: {
            labels: ["0", "1-10", "11-50", "51-100", "101-250", "251-500", "500+"],
            datasets: [{
                label: "Churn Rate",
                data: [100, 95.2, 85.3, 72.1, 55.4, 40.2, 28.6],
                backgroundColor: "#fca5a5",
                borderRadius: 4,
                barPercentage: 0.65
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 110,
                    ticks: { callback: function (v) { return v + "%"; } },
                    grid: { color: "#f3f4f6" }
                },
                x: {
                    grid: { display: false },
                    title: { display: true, text: "Game Rounds Played", color: "#9ca3af" }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) { return "Churn: " + ctx.parsed.y + "%"; }
                    }
                }
            }
        }
    });
}

// ── Nav active state ──
document.querySelectorAll(".nav-tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
        document.querySelectorAll(".nav-tab").forEach(function (t) { t.classList.remove("active"); });
        tab.classList.add("active");
    });
});
