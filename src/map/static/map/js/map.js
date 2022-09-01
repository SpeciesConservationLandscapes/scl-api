let map;
const INIT_LATITUDE = 25;
const INIT_LONGITUDE = 70;
const INIT_ZOOM = 2;
const MIN_ZOOM = 2;
const MAX_ZOOM = 14;
const CHART_LABELS = {
  nodeHoverLabelSeries1: "first generation",
  nodeHoverLabelSeries2: "second generation",
  yaxisLabel: "Mean Impact",
};
const ANALYSIS_LAYERS = {
  "scl_species": {
    "name": "Species",
    "style": {
      'fill-color': '#f0bc59',
      'fill-opacity': 0.6,
      'fill-antialias': true,
    },
  },
  "scl_species_fragment": {
    "name": "Species Fragment",
    "style": {
      'fill-color': '#fff1ca',
      'fill-opacity': 0.6,
      'fill-antialias': true,
    },
  },
  "scl_survey": {
    "name": "Survey",
    "style": {
      'fill-color': '#c8ff59',
      'fill-opacity': 0.6,
      'fill-antialias': true,
      
    },
  },
  "scl_survey_fragment": {
    "name": "Survey Fragment",
    "style": {
      'fill-color': '#e3ffd6',
      'fill-opacity': 0.6,
      'fill-antialias': true,
    },
  },
  "scl_restoration": {
    "name": "Restoration",
    "style": {
      'fill-color': '#aeaeae',
      'fill-opacity': 0.6,
      'fill-antialias': true,
    },
  },
  "scl_survey_fragment": {
    "name": "Restoration Fragment",
    "style": {
      'fill-color': '#dedede',
      'fill-opacity': 0.6,
      'fill-antialias': true,
    },
  },
  // "": {
  //   "name": "Structural Habitat",
  //   "style": {},
  // },
  // "": {
  //   "name": "Indigenous Range",
  //   "style": {},
  // },
}

// Need to fetch dates
let dateChoices = []; // For fetching data
let yearChoices = []; // For display
let currentDateIndex = 0;
let currentDate = null;
let currentColourScheme = null;
let currentBasemap = "roads";
let currentCountry = "global";



const parseOutYear = function(dateString) {
  const arr = dateString.split('-');
  if (arr.length !== 3) {
    throw new Error("Invalid date string");
  }
  return parseInt(arr[0], 10);
} 

const fetchData = function() {
  return $.get("/v1/choices/")
    .then(function(data) {
      data.dates = data.dates || [];
      dateChoices = data.dates.sort((a, b) => {return b - a});
      yearChoices = dateChoices.map(parseOutYear);
    })
    .catch(function(err) {
      console.error(err);
    });
};

const setBaseMap = function(basemap) {
  if (map.getLayer("basemap-layer")) {
    map.removeLayer("basemap-layer");
  }
  map.addLayer({
      id: "basemap-layer",
      type: "raster",
      source: basemap,
      minzoom: MIN_ZOOM,
      maxzoom: MAX_ZOOM,
    },
    "background"
  );
};

const setCountryLayer = function(iso2) {
  const sourceName = 'scl_country';
  const layerName = 'country';
  let geojsonUrl = `https://cache.speciescl.org/masked_countries/${iso2}.geojson`;

  if (map.getLayer(layerName)) {
    map.removeLayer(layerName);
    map.removeSource(sourceName);
  }

  if (!iso2 || iso2.toUpperCase() === "GLOBAL") {
    // geojsonUrl = `https://cache.speciescl.org/countries/global.geojson`;
    return;
  }

  map.addSource(sourceName, {
    type: 'geojson',
    data: geojsonUrl
  });

  map.addLayer({
    'id': layerName,
    'type': 'fill',
    'source': sourceName,
    'layout': {},
    'paint': {
        'fill-color': 'rgba(0, 0, 0, 1)',
        'fill-opacity': 0.4,
        'fill-antialias': true,
        'fill-outline-color': 'rgba(0, 0, 0, 0)',
    }
  });
}

const setCountry = function(iso2) {
  setCountryLayer(iso2);
};

const redraw = function() {
  refreshNavigateDateControls();
  setAnalysisLayers(dateChoices[currentDateIndex]);
}


/* MAP */

const setAnalysisLayer = function(layerName, date, opts) {
  const sourceName = `scl_${layerName}`;
  const geojsonUrl = `https://cache.speciescl.org/ls_stats/Panthera_tigris/canonical/${date}/${layerName}.geojson`;
  const source = map.getSource(sourceName);

  console.log('source', source);
  

  if (source) {
    source.setData(geojsonUrl);
    return;
  }

  map.addSource(sourceName, {
    type: 'geojson',
    data: geojsonUrl
  });

  map.addLayer({
    'id': layerName,
    'type': 'fill',
    'source': sourceName,
    'layout': {},
    'paint': opts.style
  });
};

const setAnalysisLayers = function(date) {
  Object.entries(ANALYSIS_LAYERS).forEach(([layerName, opts]) => {
    setAnalysisLayer(layerName, date, opts);
  });
};

const initMap = function() {
  map = new maplibregl.Map({
    container: "map", // container id
    style: {
      sources: {
        roads: {
          type: "raster",
          tiles: [
            "https://server.arcgisonline.com/ArcGIS/rest/services//World_Street_Map/MapServer/tile/{z}/{y}/{x}",
          ],
          tileSize: 256,
        },
        satellite: {
          type: "raster",
          tiles: [
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
          ],
          tileSize: 256,
        },
        light: {
          type: "raster",
          tiles: [
            "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
          ],
          tileSize: 256,
        },
        dark: {
          type: "raster",
          tiles: [
            "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
          ],
          tileSize: 256,
        },
      },
      layers: [
        {
          id: "basemap-layer",
          type: "raster",
          source: "roads",
          minzoom: 2,
          maxzoom: 14,
        },
        {
          // consistent layer to draw basemap-layer lower than in draw order
          id: "background",
          type: "background",
          layout: {
            visibility: "none",
          },
        },
      ],
      version: 8,
    },
    center: [INIT_LONGITUDE, INIT_LATITUDE], // starting position [lng, lat]
    zoom: INIT_ZOOM, // starting zoom
    minZoom: MIN_ZOOM,
    maxZoom: MAX_ZOOM
  });
  
  return new Promise((resolve, reject) => {
    map.on("load", function () {
      setCountry(currentCountry);
      setAnalysisLayers("2020-01-01");
      resolve();
    });
  });
};

/* CHART */

const newChart = function (xData, yData, title) {
  var splitData = splitChartData(xData, yData);

  var id1 = {
    x: splitData[0],
    y: splitData[2],
    mode: "lines+markers",
    type: "scatter",
    name: CHART_LABELS.nodeHoverLabelSeries1,
    marker: {
      color: "rgb(138, 184, 214)",
      symbol: "diamond",
    },
    line: {
      color: "rgb(23, 114, 174)",
    },
  };
  var id2 = {
    x: splitData[1],
    y: splitData[3],
    mode: "lines+markers",
    type: "scatter",
    name: labels.nodeHoverLabelSeries2,
    marker: {
      color: "rgb(140, 214,138)",
    },
    line: {
      color: "rgb(26,174,23)",
    },
  };
  var chartData = [id1, id2];
  var layout = {
    font: {
      color: "#21282A",
      family: "Montserrat",
      size: "18",
    },
    title: {
      text: title,
      font: {
        size: "28",
      },
      x: 0,
      xanchor: "left",
      yanchor: "top",
      pad: {
        b: "0",
        l: "10",
        r: "0",
        t: "00",
      },
    },
    margin: {
      l: 65,
      r: 0,
      b: 50,
      t: 55,
      pad: 0,
    },
    showlegend: true,
    legend: {
      orientation: "h",
      x: 0,
      y: -0.2,
    },
    xaxis: {
      fixedrange: true,
    },
    yaxis: {
      fixedrange: true,
      title: {
        text: labels.yaxisLabel,
        font: { size: 18 },
      },
    },
  };

  Plotly.newPlot("graph", chartData, layout, {
    scrollZoom: false,
    displayModeBar: false,
    responsive: true,
  });
};

/* CONTROLS */

const refreshNavigateDateControls = function() {
  const numDates = dateChoices.length;

  $("#current-date").html(yearChoices[currentDateIndex]);
  $("#date-down").prop("disabled", numDates === 0 || currentDateIndex + 1 >= numDates);
  $("#date-up").prop("disabled", numDates === 0 || currentDateIndex <= 0);
}

const navigateDate = function(event) {
  const elem = event.currentTarget;
  const numDates = dateChoices.length;
  const indexChange = elem.id === "date-up" ? -1 : 1;
  const dateIndex = currentDateIndex + indexChange;

  if (numDates === 0 || dateIndex < 0 || dateIndex > numDates - 1) return;
  
  currentDateIndex = dateIndex;
  redraw();
};


/*

1. Fetch choices
2. Set default year, base map, country
3. Load Map and chart

*/

const createEventListeners = function() {
  $(".baseSelector").change(function (e) {
    const basemap = $(this)[0].value;
    setBaseMap(basemap);
  });

  $(".countrySelector").change(function (e) {
    var iso2 = $(this)[0].value;
    setCountry(iso2);
  });

  $("#date-down, #date-up").click(navigateDate);
};

window.onload = function () {
  $(".baseSelector")
    .filter(`[value="${currentBasemap}"]`)
    .prop("checked", true);
  
  $(".countrySelector")
    .filter(`[value="${currentCountry}"]`).prop("checked", true);
 
  fetchData()
    .then(function() {
      currentDate = dateChoices[currentDateIndex];
      refreshNavigateDateControls();
      return initMap();
    })
    .then(createEventListeners);

};
