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
const LAYER_STYLES = {

}

// Need to fetch dates
let DATES = ["2000-12-31","2001-12-31","2002-12-31","2003-12-31","2004-12-31","2005-12-31","2006-12-31","2007-12-31","2008-12-31","2009-12-31","2010-12-31","2011-12-31","2012-12-31","2013-12-31","2014-12-31","2015-12-31","2016-12-31","2017-12-31","2018-12-31","2019-12-31"];

let currentDateIndex = null;
let currentDate = null;
let currentColourScheme = null;
let currentBasemap = "roads";
let currentCountry = "global";



const getData = function() {
  return $.get()
    .then(function() {
      
    })
    .catch(function() {
      
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
  let geojsonUrl;

  if (!iso2) {
    geojsonUrl = `https://cache.speciescl.org/countries/global.geojson`;
  }
  else {
    geojsonUrl = `https://cache.speciescl.org/masked_countries/${iso2}.geojson`;
  }
  
  map.addSource('scl_country', {
    type: 'geojson',
    data: geojsonUrl
  });
  map.addLayer({
    'id': 'country',
    'type': 'fill',
    'source': 'scl_country',
    'layout': {},
    'paint': {
        "fill-color": "rgba(0, 0, 0, 1)",
        "fill-opacity": 0.4,
        "fill-antialias": true,
        "fill-outline-color": "rgba(0, 0, 0, 0)",
    }
    });
}

const setCountry = function(iso2) {
  console.log("iso2", iso2);
};


// rename this function
const addLayer = function(layerName, date) {
  const geojsonUrl = `https://cache.speciescl.org/ls_stats/Panthera_tigris/canonical/${date}/${layerName}.geojson`;
  map.addSource('scl_states', {
    type: 'geojson',
    data: geojsonUrl
  });
  map.addLayer({
    'id': 'scl_states',
    'type': 'fill',
    'source': 'scl_states',
    'layout': {},
    'paint': {
    'fill-color': '#088',
    'fill-opacity': 0.8
    }
    });
};

const reDraw = function(dateIndex, colourScheme, basemap) {
  
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
  
  map.on("load", function () {
    // addLayer("scl_states", "2020-01-01");
    setCountryLayer("LK");
  });
};


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

$(document).ready(function () {
  $(".baseSelector")
    .filter(`[value="${currentBasemap}"]`)
    .prop("checked", true);
  
    $(".countrySelector")
      .filter(`[value="${currentCountry}"]`)
      .prop("checked", true);

  initMap();
  $(".baseSelector").change(function (e) {
    var basemap = $(this)[0].value;
    reDraw(currentDateIndex, currentColourScheme, basemap);
  });



  // Events
  $(".baseSelector").change(function (e) {
    var basemap = $(this)[0].value;
    setBaseMap(basemap);
    // reDraw(currentDateIndex, currentColourScheme, basemap);
  });

  $(".countrySelector").change(function (e) {
    var iso2 = $(this)[0].value;
    setCountry(iso2);
  });



  // $(".hiiSelector").filter('[value="legacy"]').prop("checked", true);
  // $(".baseSelector").filter('[value="roads"]').prop("checked", true);
  // $(".countrySelector").filter('[value="global"]').prop("checked", true);

  // start by getting global stats, which provides a list of dates
  // $.get("../api/stats/global/", function (data, status) {
  //   var dates = data["dates"];
  //   var numDates = dates.length;

  //   // hii layer can have one of two colour schemes, or be turned off
  //   // within each colour scheme, there is a source and a layer for each date
  //   // var hiiLegacy = Object.assign(
  //   //   {},
  //   //   ...dates.map((x) => ({ [x]: { layerId: null } }))
  //   // );
  //   // var hiiLinear = Object.assign(
  //   //   {},
  //   //   ...dates.map((x) => ({ [x]: { layerId: null } }))
  //   // );
  //   // var hiiLayers = { legacy: hiiLegacy, linear: hiiLinear };

  //   // var currentColourScheme = null;
  //   // var currentDateIndex = null;
  //   // var currentDate = null;

  //   // var currentPolygonLayer = null;

  //   var currentBasemap = "roads";

  //   // var splitIndex = firstIndexPast2013(dates);

  //   // function for changing which date is displayed on map,
  //   // and highlighted on chart
  //   var reDraw = function (dateIndex, colourScheme, basemap) {
  //     // highlight date in graph
  //     var sizes = new Array(numDates);
  //     for (let i = 0; i < numDates; i++) {
  //       if (i == dateIndex) {
  //         sizes[i] = 20;
  //       } else {
  //         sizes[i] = 10;
  //       }
  //     }
  //     Plotly.restyle("graph", {
  //       "marker.size": [sizes.slice(0, splitIndex), sizes.slice(splitIndex)],
  //     });

  //     // remove previous layer
  //     if (currentColourScheme != "none") {
  //       if (currentDate) {
  //         var layerId = hiiLayers[currentColourScheme][currentDate]["layerId"];
  //         if (layerId) {
  //           if (map.getLayer(layerId)) {
  //             map.removeLayer(layerId);
  //           }
  //         }
  //       }
  //     }

  //     // add new layer, along with source if not already added
  //     var newDate = dates[dateIndex];
  //     var newColourScheme = colourScheme;

  //     if (newColourScheme != "none") {
  //       var newLayerId = hiiLayers[newColourScheme][newDate]["layerId"];
  //       if (newLayerId) {
  //       } else {
  //         newLayerId = `hii-${newDate}-tiles-${newColourScheme}`;
  //         hiiLayers[newColourScheme][newDate]["layerId"] = newLayerId;
  //         map.addSource(newLayerId, {
  //           type: "raster",
  //           tiles: [
  //             `../api/tiles-${newColourScheme}/hii/${newDate}/{z}/{x}/{y}`,
  //           ],
  //           tileSize: 256,
  //         });
  //       }
  //       map.addLayer(
  //         {
  //           id: newLayerId,
  //           type: "raster",
  //           source: newLayerId,
  //           minzoom: 2,
  //           maxzoom: 14,
  //         },
  //         currentPolygonLayer
  //       );
  //     }

  //     //basemap
  //     if (map.getLayer("basemap-layer")) {
  //       map.removeLayer("basemap-layer");
  //     }
  //     map.addLayer(
  //       {
  //         id: "basemap-layer",
  //         type: "raster",
  //         source: basemap,
  //         minzoom: 2,
  //         maxzoom: 14,
  //       },
  //       "background"
  //     );

  //     // set global vars with new values
  //     currentDateIndex = dateIndex;
  //     currentDate = newDate;
  //     currentColourScheme = newColourScheme;
  //     currentBasemap = basemap;
  //   };

  //   var setCountry = function (iso2) {
  //     // fetch geometry
  //     $.get(
  //       `../api/countries_geometry?iso2=${iso2}&mask=true`,
  //       function (data, status) {
  //         var geojsonFeature = data["results"]["features"][0];

  //         map.addSource(`${iso2}`, {
  //           type: "geojson",
  //           data: geojsonFeature,
  //           buffer: 512,
  //         });
  //         map.addLayer({
  //           id: `${iso2}`,
  //           type: "fill",
  //           source: `${iso2}`,
  //           layout: {},
  //           paint: {
  //             "fill-color": "rgba(0, 0, 0, 1)",
  //             "fill-opacity": 0.4,
  //             "fill-antialias": true,
  //             "fill-outline-color": "rgba(0, 0, 0, 0)",
  //           },
  //         });
  //         currentPolygonLayer = `${iso2}`;

  //         // if multipolygon, flatten one more level
  //         if (geojsonFeature.geometry.type === "GeometryCollection") {
  //           var geom2 = geojsonFeature.geometry.geometries[1];
  //         } else {
  //           var geom2 = geojsonFeature.geometry;
  //         }

  //         if (geom2 === "Polygon") {
  //           var coordinates = geom2.coordinates.flat(1).slice(5);
  //         } else {
  //           var coordinates = geom2.coordinates.flat(2).slice(5);
  //         }

  //         var bounds = coordinates.reduce(function (bounds, coord) {
  //           return bounds.extend(coord);
  //         }, new maplibregl.LngLatBounds(coordinates[0], coordinates[0]));

  //         map.fitBounds(bounds, {
  //           padding: 20,
  //         });

  //         $.get(`../api/stats/country/${iso2}`, function (data, status) {
  //           var restyleChartData1 = {
  //             y: [data["means"].slice(0, splitIndex)],
  //             name: labels.nodeHoverLabelSeries1,
  //           };
  //           var restyleChartData2 = {
  //             y: [data["means"].slice(splitIndex)],
  //             name: labels.nodeHoverLabelSeries2,
  //           };

  //           Plotly.restyle("graph", restyleChartData1, 0);
  //           Plotly.restyle("graph", restyleChartData2, 1);
  //           Plotly.update("graph", {}, { title: data["name"] });
  //         });
  //       }
  //     );
  //   };

  //   var setGlobal = function () {
  //     currentPolygonLayer = null;

  //     map.jumpTo({
  //       center: [0, 0],
  //       zoom: 2,
  //     });

  //     $.get("../api/stats/global", function (data, status) {
  //       var globalRestyle1 = {
  //         y: [data["means"].slice(0, splitIndex)],
  //         name: labels.nodeHoverLabelSeries1,
  //       };
  //       var globalRestyle2 = {
  //         y: [data["means"].slice(splitIndex)],
  //         name: labels.nodeHoverLabelSeries2,
  //       };
  //       Plotly.restyle("graph", globalRestyle1, 0);
  //       Plotly.restyle("graph", globalRestyle2, 1);
  //       Plotly.update("graph", {}, { title: "Global" });
  //     });
  //   };

  //   // function on country change
  //   var changeCountry = function (iso2) {
  //     // remove source and layer
  //     if (currentPolygonLayer) {
  //       if (map.getLayer(currentPolygonLayer)) {
  //         map.removeLayer(currentPolygonLayer);
  //       }
  //       if (map.getSource(currentPolygonLayer)) {
  //         map.removeSource(currentPolygonLayer);
  //       }
  //     }

  //     if (iso2 === "global") {
  //       setGlobal();
  //     } else {
  //       setCountry(iso2);
  //     }
  //   };

  //   // initialize chart
  //   console.warn("use years only, not full dates, as chart x-axis");
  //   newChart(
  //     data["dates"].map((x) => x.slice(0, 4)),
  //     data["means"],
  //     "Global"
  //   );

  //   // init map
  //   // var map = new maplibregl.Map({
  //   //   container: "map", // container id
  //   //   style: {
  //   //     sources: {
  //   //       roads: {
  //   //         type: "raster",
  //   //         tiles: [
  //   //           "https://server.arcgisonline.com/ArcGIS/rest/services//World_Street_Map/MapServer/tile/{z}/{y}/{x}",
  //   //         ],
  //   //         tileSize: 256,
  //   //       },
  //   //       satellite: {
  //   //         type: "raster",
  //   //         tiles: [
  //   //           "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  //   //         ],
  //   //         tileSize: 256,
  //   //       },
  //   //       light: {
  //   //         type: "raster",
  //   //         tiles: [
  //   //           "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
  //   //         ],
  //   //         tileSize: 256,
  //   //       },
  //   //       dark: {
  //   //         type: "raster",
  //   //         tiles: [
  //   //           "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
  //   //         ],
  //   //         tileSize: 256,
  //   //       },
  //   //     },
  //   //     layers: [
  //   //       {
  //   //         id: "basemap-layer",
  //   //         type: "raster",
  //   //         source: "roads",
  //   //         minzoom: 2,
  //   //         maxzoom: 14,
  //   //       },
  //   //       {
  //   //         // consistent layer to draw basemap-layer lower than in draw order
  //   //         id: "background",
  //   //         type: "background",
  //   //         layout: {
  //   //           visibility: "none",
  //   //         },
  //   //       },
  //   //     ],
  //   //     version: 8,
  //   //   },
  //   //   center: [0, 48.8534], // starting position [lng, lat]
  //   //   zoom: 2, // starting zoom
  //   //   minZoom: 2,
  //   //   maxZoom: 14,
  //   // });

  //   // map.on("load", function () {
  //   //   reDraw(numDates - 1, "legacy", "roads");

  //   //   // add event listeners to buttons

  //   //   $(".hiiSelector").change(function (e) {
  //   //     var colourScheme = $(this)[0].value;
  //   //     reDraw(currentDateIndex, colourScheme, currentBasemap);
  //   //   });

  //   //   $(".baseSelector").change(function (e) {
  //   //     var basemap = $(this)[0].value;
  //   //     reDraw(currentDateIndex, currentColourScheme, basemap);
  //   //   });

  //   //   $(".countrySelector").change(function (e) {
  //   //     var iso2 = $(this)[0].value;
  //   //     changeCountry(iso2);
  //   //   });

  //   //   // some date stepper stuff
  //   //   $("#date-down, #date-up").click(function () {
  //   //     let currentStepperDate = parseInt($("#current-date").html(), 10);
  //   //     const min = 2000;
  //   //     const max = 2019;
  //   //     $("#date-down, #date-up").prop("disabled", false);
  //   //     if (this.id === "date-up" && currentStepperDate < max) {
  //   //       $("#current-date").html(++currentStepperDate);
  //   //       reDraw(++currentDateIndex, currentColourScheme, currentBasemap);
  //   //     } else if (this.id === "date-down" && currentStepperDate > min) {
  //   //       $("#current-date").html(--currentStepperDate);
  //   //       reDraw(--currentDateIndex, currentColourScheme, currentBasemap);
  //   //     }
  //   //     if (currentStepperDate === min) {
  //   //       $("#date-down").prop("disabled", true);
  //   //     } else if (currentStepperDate === max) {
  //   //       $("#date-up").prop("disabled", true);
  //   //     }
  //   //   });
  //   //   var graphDiv = document.getElementById("graph");
  //   //   graphDiv.on("plotly_click", function (data) {
  //   //     var curveNumber = data.points[0].curveNumber;
  //   //     var pointIndex = data.points[0].pointIndex;
  //   //     $("#current-date").html(2000 + curveNumber * splitIndex + pointIndex);
  //   //     reDraw(
  //   //       curveNumber * splitIndex + pointIndex,
  //   //       currentColourScheme,
  //   //       currentBasemap
  //   //     );
  //   //   });
  //   // });
  // });
});
