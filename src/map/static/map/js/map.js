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
    "layerTitle": "Species",
    "layerName": "scl_species",
    "paint": {
      'fill-color': '#f0bc59',
      'fill-opacity': 0.6,
      'fill-antialias': true,
    },
  },
  "scl_species_fragment": {
    "layerTitle": "Species Fragment",
    "layerName": "scl_species_fragment",
    "paint": {
      'fill-color': '#fff1ca',
      'fill-opacity': 0.6,
      'fill-antialias': true,
    },
  },
  "scl_survey": {
    "layerTitle": "Survey",
    "layerName": "scl_survey",
    "paint": {
      'fill-color': '#c8ff59',
      'fill-opacity': 0.6,
      'fill-antialias': true,

    },
  },
  "scl_survey_fragment": {
    "layerTitle": "Survey Fragment",
    "layerName": "scl_survey_fragment",
    "paint": {
      'fill-color': '#e3ffd6',
      'fill-opacity': 0.6,
      'fill-antialias': true,
    },
  },
  "scl_restoration": {
    "layerTitle": "Restoration",
    "layerName": "scl_restoration",
    "paint": {
      'fill-color': '#aeaeae',
      'fill-opacity': 0.6,
      'fill-antialias': true,
    },
  },
  "scl_survey_fragment": {
    "layerTitle": "Restoration Fragment",
    "layerName": "scl_survey_fragment",
    "paint": {
      'fill-color': '#dedede',
      'fill-opacity': 0.6,
      'fill-antialias': true,
    },
  },
}
// "": {
//   "layerTitle": "Structural Habitat",
//   "paint": {},
// },
// "tcl3_indigenous_range_07302022": {
//   "layerTitle": "Indigenous Range",
//   "paint": {
//     'fill-color': '#ebebeb',
//     'fill-opacity': 0.6,
//     'fill-antialias': true,
//   },
// },
// }

const INDIGENOUS_RANGE_LAYER = {
  'layerTitle': 'Indigenous Range',
  'layerName': 'tcl3_indigenous_range_07302022',
  'urlPath': 'tcl3_indigenous_range_07302022.geojson',
  "paint": {
    'fill-color': '#ebebeb',
    'fill-opacity': 0.6,
    'fill-antialias': true,
  },
}

// Need to fetch dates
let dateChoices = []; // For fetching data
let yearChoices = []; // For display
let currentDateIndex = 0;
let currentDate = null;
let currentColourScheme = null;
let currentBasemap = "roads";
let currentCountry = "global";



const parseOutYear = function (dateString) {
  const arr = dateString.split('-');
  if (arr.length !== 3) {
    throw new Error("Invalid date string");
  }
  return parseInt(arr[0], 10);
}

const fetchData = function () {
  return $.get("/v1/choices/")
    .then(function (data) {
      data.dates = data.dates || [];
      dateChoices = data.dates.sort((a, b) => { return b - a });
      yearChoices = dateChoices.map(parseOutYear);
    })
    .catch(function (err) {
      console.error(err);
    });
};

const setBaseMap = function (basemap) {
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

const setCountryLayer = function (iso2) {
  const sourceName = 'scl_country';
  const layerName = 'country';
  let geojsonUrl = `masked_countries/${iso2}.geojson`;

  if (map.getLayer(layerName)) {
    map.removeLayer(layerName);
    map.removeSource(sourceName);
  }

  if (!iso2 || iso2.toUpperCase() === "GLOBAL") {
    return;
  }
  setLayer(layerName, geojsonUrl, {
    'fill-color': 'rgba(0, 0, 0, 1)',
    'fill-opacity': 0.4,
    'fill-antialias': true,
    'fill-outline-color': 'rgba(0, 0, 0, 0)',
  });
}

const setCountry = function (iso2) {
  setCountryLayer(iso2);
};

const redraw = function () {
  refreshNavigateDateControls();
  setAnalysisLayers(dateChoices[currentDateIndex]);
}


/* MAP */

const setLayer = function (layerName, urlPath, paint) {
  const sourceName = `scl_${layerName}`;
  const geojsonUrl = `https://cache.speciescl.org/${urlPath}`;
  const source = map.getSource(sourceName);

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
    'paint': paint
  });
};

const setAnalysisLayer = function (layerName, date, paint) {
  setLayer(layerName, `ls_stats/Panthera_tigris/canonical/${date}/${layerName}.geojson`, paint);
};

const setAnalysisLayers = function (date) {
  Object.values(ANALYSIS_LAYERS).forEach((config) => {
    setAnalysisLayer(config.layerName, date, config.paint);
  });
};

const setInigenousRangeLayer = function () {
  setLayer(INDIGENOUS_RANGE_LAYER.layerName, INDIGENOUS_RANGE_LAYER.urlPath, INDIGENOUS_RANGE_LAYER.paint);
}

const initMap = function () {
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
      setInigenousRangeLayer();
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

const refreshNavigateDateControls = function () {
  const numDates = dateChoices.length;

  $("#current-date").html(yearChoices[currentDateIndex]);
  $("#date-down").prop("disabled", numDates === 0 || currentDateIndex + 1 >= numDates);
  $("#date-up").prop("disabled", numDates === 0 || currentDateIndex <= 0);
}

const navigateDate = function (event) {
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

const createEventListeners = function () {
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
    .then(function () {
      currentDate = dateChoices[currentDateIndex];
      refreshNavigateDateControls();
      return initMap();
    })
    .then(createEventListeners);

};
