// Global Variables
let localScores = {};
let globalScores = {};
const dimWeights = { prestige: 0.5, vibes: 0.2, location: 0.3 };
const defaultScore = { prestige: 1000, vibes: 1000, location: 1000 };

// Fetch global scores and populate the dropdown
fetch("global_scores.txt")
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json(); // Parse as JSON
    })
    .then(data => {
        globalScores = data;
        populateProgramOptions(); // Populate the datalist with program names
        updateRankings(); // Update rankings table if needed
    })
    .catch(error => console.error("Failed to load global scores:", error));

// Populate the datalist for the searchable dropdown
function populateProgramOptions() {
    const datalist = document.getElementById("program-options");
    datalist.innerHTML = ""; // Clear existing options

    // Add an <option> for each program
    for (const program in globalScores) {
        const option = document.createElement("option");
        option.value = program; // Use program name as the value
        datalist.appendChild(option);
    }
}

// Add New Residency Program
function addNewProgram() {
    const programName = document.getElementById("program-name").value.trim();
    if (!programName) {
        alert("Program name cannot be empty.");
        return;
    }

    if (!localScores[programName]) {
        localScores[programName] = { ...defaultScore };
        if (!globalScores[programName]) {
            globalScores[programName] = { ...defaultScore };
        }

        updateProgramOptions();
        alert(`${programName} added successfully!`);

        // Automatically compare with existing programs
        for (const dimension of Object.keys(dimWeights)) {
            for (const existingProgram in localScores) {
                if (existingProgram !== programName) {
                    showComparisonModal(dimension, programName, existingProgram);
                    // const winner = prompt(`Which program is better for ${dimension}? Enter '${programName}' or '${existingProgram}':`);
                    // if (winner === programName || winner === existingProgram) {
                    //     updateScoresByDimension(programName, existingProgram, localScores, winner, dimension);
                    //     updateScoresByDimension(programName, existingProgram, globalScores, winner, dimension);
                    // }
                }
            }
        }
        updateRankings();
    } else {
        alert(`${programName} already exists.`);
    }

    document.getElementById("program-name").value = "";
}

let currentComparison = {}; // To store details of the current comparison

function showComparisonModal(dimension, program1, program2) {
    currentComparison = { dimension, program1, program2 }; // Store details

    // Update modal content
    document.getElementById("compare-question").textContent = 
        `Which program is better for ${dimension}?`;
    document.getElementById("option1-button").textContent = program1;
    document.getElementById("option2-button").textContent = program2;

    // Show the modal
    document.getElementById("compare-modal").style.display = "block";
}

function selectWinner(option) {
    const { dimension, program1, program2 } = currentComparison;

    const winner = option === "option1" ? program1 : program2;

    // Update scores
    updateScoresByDimension(program1, program2, localScores, winner, dimension);
    updateScoresByDimension(program1, program2, globalScores, winner, dimension);

    // Hide the modal
    document.getElementById("compare-modal").style.display = "none";

    // Continue with the next steps, e.g., update rankings
    updateRankings();
}

// Update program options in the comparison dropdowns
function updateProgramOptions() {
    const program1Select = document.getElementById("program1");
    const program2Select = document.getElementById("program2");

    program1Select.innerHTML = "";
    program2Select.innerHTML = "";

    for (const program in localScores) {
        const option1 = new Option(program, program);
        const option2 = new Option(program, program);
        program1Select.add(option1);
        program2Select.add(option2);
    }
}

// Update Scores by Dimension
function updateScoresByDimension(program1, program2, scoreList, winner, dimension, kFactor = 32) {
    const score1 = scoreList[program1][dimension];
    const score2 = scoreList[program2][dimension];

    const expected1 = 1 / (1 + Math.pow(10, (score2 - score1) / 400));
    const expected2 = 1 - expected1;

    if (winner === program1) {
        scoreList[program1][dimension] += kFactor * (1 - expected1);
        scoreList[program2][dimension] += kFactor * (0 - expected2);
    } else if (winner === program2) {
        scoreList[program1][dimension] += kFactor * (0 - expected1);
        scoreList[program2][dimension] += kFactor * (1 - expected2);
    }
}

// Update Rankings
function updateRankings() {
    const rankings = document.getElementById("rankings");
    rankings.innerHTML = "";

    const rankList = Object.keys(localScores)
        .map(program => ({
            program,
            score: calculateOverallScore(program),
        }))
        .sort((a, b) => b.score - a.score);

    rankList.forEach((entry, index) => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${index + 1}</td><td>${entry.program}</td><td>${entry.score.toFixed(2)}</td>`;
        rankings.appendChild(row);
    });
}

// Calculate Overall Score
function calculateOverallScore(programName) {
    const scores = localScores[programName];
    let overallScore = 0;

    for (const [dimension, weight] of Object.entries(dimWeights)) {
        overallScore += scores[dimension] * weight;
    }

    return overallScore;
}

// Update Weights
function updateWeights() {
    for (const dimension of Object.keys(dimWeights)) {
        const slider = document.getElementById(`weight-${dimension}`);
        const valueSpan = document.getElementById(`weight-${dimension}-value`);
        dimWeights[dimension] = parseFloat(slider.value);
        valueSpan.textContent = slider.value;
    }
    updateRankings();
}

// Upload Local Scores
function uploadLocalScores(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            localScores = JSON.parse(e.target.result);
            updateProgramOptions();
            updateRankings();
        };
        reader.readAsText(file);
        updateRankings();
    }
    updateRankings();
}

// Download Local Scores
function downloadLocalScores() {
    const blob = new Blob([JSON.stringify(localScores, null, 4)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "local_scores.json";
    a.click();
}
