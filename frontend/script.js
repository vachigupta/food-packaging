/* ============================================================
   WRAPWISE — INTELLIGENT FOOD PACKAGING
   FRONTEND CONTROLLER
   ============================================================ */

const API_ENDPOINT = "/api/recommend";

// ============================================================
// COMMODITY KNOWLEDGE BASE
// ============================================================

const COMMODITIES = {

  wheat: {
    name: "Wheat grain",
    group: "Grain",
    forms: ["whole_grain"],
    moistureSensitivity: "High",
    gasRequirement: "Medium–High",
    lightSensitivity: "Medium",
    mechanicalSensitivity: "Medium–High",
    fungalRisk: "High",
    defaultTemperature: 30,
    defaultHumidity: 70,
    defaultShelfLife: 180,
    defaultStorage: "ambient"
  },

  rice: {
    name: "Rice grain",
    group: "Grain",
    forms: ["whole_grain"],
    moistureSensitivity: "High",
    gasRequirement: "Medium",
    lightSensitivity: "Medium",
    mechanicalSensitivity: "Medium",
    fungalRisk: "High",
    defaultTemperature: 30,
    defaultHumidity: 65,
    defaultShelfLife: 180,
    defaultStorage: "ambient"
  },

  maize: {
    name: "Maize / Corn grain",
    group: "Grain",
    forms: ["whole_grain"],
    moistureSensitivity: "High",
    gasRequirement: "Medium",
    lightSensitivity: "Medium",
    mechanicalSensitivity: "High",
    fungalRisk: "High",
    defaultTemperature: 30,
    defaultHumidity: 65,
    defaultShelfLife: 180,
    defaultStorage: "ambient"
  },

  potato: {
    name: "Potato",
    group: "Fresh produce",
    forms: ["fresh_whole"],
    moistureSensitivity: "Medium",
    gasRequirement: "Controlled permeability",
    lightSensitivity: "High",
    mechanicalSensitivity: "High",
    fungalRisk: "Medium",
    defaultTemperature: 12,
    defaultHumidity: 90,
    defaultShelfLife: 30,
    defaultStorage: "ambient"
  },

  tomato: {
    name: "Tomato",
    group: "Fresh produce",
    forms: ["fresh_whole", "fresh_cut"],
    moistureSensitivity: "Medium",
    gasRequirement: "Controlled permeability",
    lightSensitivity: "Medium",
    mechanicalSensitivity: "High",
    fungalRisk: "Medium",
    defaultTemperature: 15,
    defaultHumidity: 90,
    defaultShelfLife: 7,
    defaultStorage: "ambient"
  }

};


// ============================================================
// DOM REFERENCES
// ============================================================

const foodSelect = document.getElementById("foodSelect");
const formSelect = document.getElementById("formSelect");

const temperatureInput =
  document.getElementById("temperatureInput");

const humidityInput =
  document.getElementById("humidityInput");

const shelfInput =
  document.getElementById("shelfInput");

const storageSelect =
  document.getElementById("storageSelect");

const transportInput =
  document.getElementById("transportInput");

const prioritySelect =
  document.getElementById("prioritySelect");

const profileTags =
  document.getElementById("profileTags");

const requirementsGrid =
  document.getElementById("requirementsGrid");

const generateBtn =
  document.getElementById("generateBtn");

const loadingText =
  document.getElementById("loadingText");

const resultsPlaceholder =
  document.getElementById("results-placeholder");

const resultsBody =
  document.getElementById("results-body");

const resultsTitle =
  document.getElementById("resultsTitle");

const resultsDescription =
  document.getElementById("resultsDescription");

const resultsMeta =
  document.getElementById("resultsMeta");

const cardsHost =
  document.getElementById("cardsHost");

const validationWarning =
  document.getElementById("validationWarning");


// ============================================================
// CURRENT COMMODITY
// ============================================================

function currentCommodity() {

  return COMMODITIES[foodSelect.value];

}


// ============================================================
// UPDATE COMMODITY PROFILE
// ============================================================

function refreshCommodityProfile() {

  const commodity = currentCommodity();

  if (!commodity) {
    return;
  }

  // Default values

  temperatureInput.value =
    commodity.defaultTemperature;

  humidityInput.value =
    commodity.defaultHumidity;

  shelfInput.value =
    commodity.defaultShelfLife;

  storageSelect.value =
    commodity.defaultStorage;


  // Select form

  if (commodity.group === "Fresh produce") {

    formSelect.value = "fresh_whole";

  } else {

    formSelect.value = "whole_grain";

  }


  // Display food characteristics

  profileTags.innerHTML = `

    <span class="tag">
      moisture:
      <strong>${commodity.moistureSensitivity}</strong>
    </span>

    <span class="tag">
      gas exchange:
      <strong>${commodity.gasRequirement}</strong>
    </span>

    <span class="tag">
      light:
      <strong>${commodity.lightSensitivity}</strong>
    </span>

    <span class="tag">
      mechanical:
      <strong>${commodity.mechanicalSensitivity}</strong>
    </span>

    <span class="tag">
      fungal risk:
      <strong>${commodity.fungalRisk}</strong>
    </span>

  `;
}


// Run when food changes

foodSelect.addEventListener(
  "change",
  refreshCommodityProfile
);


// ============================================================
// SLIDER VALUES
// ============================================================

["wShelf", "wCost", "wEco"].forEach(id => {

  const slider =
    document.getElementById(id);

  const value =
    document.getElementById(id + "Val");

  if (!slider || !value) {
    return;
  }

  slider.addEventListener(
    "input",
    () => {
      value.textContent = slider.value;
    }
  );

});


// ============================================================
// COLLECT USER INPUT
// ============================================================

function collectRequest() {

  return {

    commodity:
      foodSelect.value,

    form:
      formSelect.value,

    temperature:
      Number(temperatureInput.value),

    relative_humidity:
      Number(humidityInput.value),

    target_shelf_life:
      Number(shelfInput.value),

    storage_condition:
      storageSelect.value,

    transportation_distance_km:
      Number(transportInput.value),

    priority:
      prioritySelect.value,

    weights: {

      shelf_life:
        Number(
          document.getElementById("wShelf").value
        ),

      cost:
        Number(
          document.getElementById("wCost").value
        ),

      sustainability:
        Number(
          document.getElementById("wEco").value
        )

    }

  };

}


// ============================================================
// VALIDATE INPUT
// ============================================================

function validateRequest(data) {

  if (!data.commodity) {
    return "Please select a commodity.";
  }

  if (Number.isNaN(data.temperature)) {
    return "Please enter a valid temperature.";
  }

  if (Number.isNaN(data.relative_humidity)) {
    return "Please enter a valid humidity.";
  }

  if (
    data.relative_humidity < 0 ||
    data.relative_humidity > 100
  ) {

    return "Relative humidity must be between 0 and 100%.";
  }

  if (
    Number.isNaN(data.target_shelf_life) ||
    data.target_shelf_life <= 0
  ) {

    return "Target shelf life must be greater than zero.";
  }

  if (
    Number.isNaN(data.transportation_distance_km) ||
    data.transportation_distance_km < 0
  ) {

    return "Transportation distance cannot be negative.";
  }

  return null;
}


// ============================================================
// SEND REQUEST TO FASTAPI
// ============================================================

async function requestRecommendation(data) {

  const response = await fetch(
    API_ENDPOINT,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify(data)
    }
  );


  if (!response.ok) {

    throw new Error(
      `Backend returned ${response.status}`
    );

  }


  return await response.json();
}


// ============================================================
// GENERATE RECOMMENDATION
// ============================================================

generateBtn.addEventListener(
  "click",
  generateRecommendation
);


async function generateRecommendation() {

  const request =
    collectRequest();


  const validation =
    validateRequest(request);


  if (validation) {

    showError(validation);

    return;
  }


  setLoading(true);


  try {

    // Send request to your real backend

    const result =
      await requestRecommendation(request);


    console.log(
      "Backend response:",
      result
    );


    if (result.status !== "success") {

      throw new Error(
        result.summary ||
        "Backend could not generate recommendation."
      );

    }


    // Display requirements

    renderRequirements(
      result.requirements
    );


    // Display Top 3

    renderRecommendations(
      request,
      result
    );

  }

  catch (error) {

    console.error(
      "Recommendation error:",
      error
    );


    showError(
      "Unable to connect to the backend. " +
      "Make sure FastAPI is running on " +
      "http://127.0.0.1:8000"
    );

  }

  finally {

    setLoading(false);

  }

}


// ============================================================
// LOADING STATE
// ============================================================

function setLoading(isLoading) {

  generateBtn.disabled =
    isLoading;

  loadingText.style.display =
    isLoading
      ? "inline"
      : "none";

  generateBtn.textContent =
    isLoading
      ? "Analysing..."
      : "Generate recommendation";

}


// ============================================================
// RENDER REQUIREMENTS
// ============================================================

function renderRequirements(
  requirements
) {

  if (!requirements) {
    return;
  }


  requirementsGrid.innerHTML = "";


  const properties = [

    {
      key: "moisture_barrier",
      name: "Moisture barrier",
      description:
        "Controls moisture ingress or loss."
    },

    {
      key: "gas_requirement",
      name: "Gas barrier / permeability",
      description:
        "Controls oxygen and carbon-dioxide exchange."
    },

    {
      key: "light_barrier",
      name: "Light barrier",
      description:
        "Protects against harmful light exposure."
    },

    {
      key: "mechanical_strength",
      name: "Mechanical strength",
      description:
        "Protects during handling, stacking and transport."
    },

    {
      key: "sealability",
      name: "Sealability",
      description:
        "Maintains package integrity."
    },

    {
      key: "temperature_suitability",
      name: "Temperature suitability",
      description:
        "Ensures compatibility with storage conditions."
    },

    {
      key: "food_contact",
      name: "Food-contact suitability",
      description:
        "Required eligibility check for food packaging."
    }

  ];


  properties.forEach(property => {

    const value =
      requirements[property.key] ??
      "Not specified";


    const card =
      document.createElement("div");


    card.className =
      "requirement";


    card.innerHTML = `

      <div class="requirement-head">

        <span class="requirement-name">
          ${property.name}
        </span>

        <span class="requirement-level">
          ${formatText(value)}
        </span>

      </div>

      <div class="requirement-description">
        ${property.description}
      </div>

    `;


    requirementsGrid.appendChild(card);

  });

}


// ============================================================
// RENDER RECOMMENDATIONS
// ============================================================

function renderRecommendations(
  request,
  result
) {

  resultsPlaceholder.style.display =
    "none";

  resultsBody.style.display =
    "block";


  const commodity =
    COMMODITIES[request.commodity];


  resultsTitle.textContent =
    `Recommended for ${commodity.name}`;


  resultsDescription.textContent =
    result.summary ||
    "The ranking engine evaluated available packaging structures against the inferred requirements.";


  resultsMeta.textContent =
    `${request.target_shelf_life}d · ` +
    `${request.temperature}°C · ` +
    `${request.relative_humidity}% RH`;


  cardsHost.innerHTML = "";


  const recommendations =
    result.recommendations || [];


  if (recommendations.length === 0) {

    cardsHost.innerHTML = `

      <div class="requirement empty">
        Insufficient validated data
        for this recommendation.
      </div>

    `;

    return;
  }


  recommendations
    .slice(0, 3)
    .forEach(
      (recommendation, index) => {

        renderRecommendationCard(
          recommendation,
          index
        );

      }
    );


  // Validation warning

  if (result.warning) {

    validationWarning.style.display =
      "block";

    validationWarning.innerHTML = `

      <b>
        Validation warning
      </b>

      ${result.warning}

    `;

  } else {

    validationWarning.style.display =
      "none";

  }


  resultsBody.scrollIntoView({

    behavior: "smooth",

    block: "nearest"

  });

}


// ============================================================
// RENDER SINGLE CARD
// ============================================================

function renderRecommendationCard(
  item,
  index
) {

  const labels = [

    "Top match",
    "Second choice",
    "Third choice"

  ];


  const score =
    Math.round(
      Number(item.score || 0)
    );


  const card =
    document.createElement("div");


  card.className =
    "card" +
    (index === 0 ? " top" : "");


  const swatchColors = [

    "#55643F",
    "#4C6B73",
    "#A85327"

  ];


  const reasons =
    item.reasons || [];


  const tradeoffs =
    item.tradeoffs || [];


  const warnings =
    item.warnings || [];


  card.innerHTML = `

    <div
      class="swatch"
      style="background:${swatchColors[index]}"
    ></div>


    <div class="card-body">


      <!-- HEADER -->

      <div class="card-head">

        <div class="card-title">

          <h3>
            ${item.packaging}
          </h3>

          <span class="family-label">
            ${item.family || ""}
          </span>

        </div>


        <!-- SCORE -->

        <div class="score-block">

          <span class="pick-label">
            ${labels[index]}
          </span>

          <div class="score-num">
            ${score}
          </div>

          <div class="score-bar">

            <div
              class="score-fill"
              style="width:${Math.min(score, 100)}%"
            ></div>

          </div>

        </div>

      </div>


      <!-- REASONS -->

      <div class="reasoning">

        ${
          reasons.length
            ? reasons.join(" ")
            : "Recommended based on the overall ranking."
        }

      </div>


      <!-- TRADE-OFFS -->

      ${
        tradeoffs.length

          ? `

            <div class="tradeoffs">

              <strong>
                Trade-offs
              </strong>

              ${tradeoffs.join(" ")}

            </div>

          `

          : ""
      }


      <!-- BADGES -->

      <div class="badges">

        ${
          item.food_contact === true

            ? `

              <span class="badge good">
                food-contact eligible
              </span>

            `

            : ""
        }


        ${
          item.recyclable === true

            ? `

              <span class="badge good">
                recyclable
              </span>

            `

            : ""
        }


        ${
          item.warning

            ? `

              <span class="badge warning">
                review required
              </span>

            `

            : ""
        }

      </div>


      <!-- SPECIFICATIONS -->

      <div class="spec-row">


        ${
          item.otr !== undefined

            ? `

              <span>
                OTR
                <b>${item.otr}</b>
                ${item.otr_unit || "cc/m²/day"}
              </span>

            `

            : ""
        }


        ${
          item.wvtr !== undefined

            ? `

              <span>
                WVTR
                <b>${item.wvtr}</b>
                ${item.wvtr_unit || "g/m²/day"}
              </span>

            `

            : ""
        }


        ${
          item.thickness !== undefined

            ? `

              <span>
                thickness
                <b>
                  ${item.thickness}
                  ${item.thickness_unit || ""}
                </b>
              </span>

            `

            : ""
        }


        ${
          item.cost_tier !== undefined

            ? `

              <span>
                cost
                <b>
                  ${formatText(item.cost_tier)}
                </b>
              </span>

            `

            : ""
        }


        ${
          item.sustainability_score !== undefined

            ? `

              <span>
                sustainability
                <b>
                  ${item.sustainability_score}
                </b>
              </span>

            `

            : ""
        }


      </div>


      <!-- WARNINGS -->

      ${
        warnings.length

          ? `

            <div class="tradeoffs">

              <strong>
                Review
              </strong>

              ${warnings.join(" ")}

            </div>

          `

          : ""
      }


    </div>

  `;


  cardsHost.appendChild(card);

}


// ============================================================
// ERROR
// ============================================================

function showError(message) {

  validationWarning.style.display =
    "block";


  validationWarning.innerHTML = `

    <b>
      Input / system warning
    </b>

    ${message}

  `;


  resultsBody.style.display =
    "block";

  resultsPlaceholder.style.display =
    "none";

}


// ============================================================
// FORMAT TEXT
// ============================================================

function formatText(value) {

  if (
    value === null ||
    value === undefined
  ) {

    return "-";
  }


  return String(value)
    .replace(/_/g, " ")
    .replace(/\b\w/g, letter =>
      letter.toUpperCase()
    );

}


// ============================================================
// INITIALISE APPLICATION
// ============================================================

refreshCommodityProfile();

console.log(
  "WrapWise frontend connected to:",
  API_ENDPOINT
);