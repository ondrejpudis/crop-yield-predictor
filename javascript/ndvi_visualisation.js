// Load a landsat image and select three bands.
var geometry = /* color: #d63000 */ee.Geometry.Point([17.48297908719917, 48.32044955771002]);
var landsat_collection = ee.ImageCollection("LANDSAT/LE07/C01/T1");
var landsat = ee.Algorithms.Landsat.simpleComposite({ "collection": landsat_collection, "asFloat": true });

var ndvi_landsat = landsat.addBands(landsat.normalizedDifference({ "bandNames": ["B4", "B3"] }));

var ndvi_visualisation = ndvi_landsat.visualize({
    "min": -0.2,
    "max": 1,
    "bands": ["nd"],
    "palette": [
        'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901',
        '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01',
        '012E01', '011D01', '011301'
    ]
});

var region_circle = geometry.buffer(40000);

// Export the image, specifying scale and region.
Export.image.toDrive({
    image: ndvi_visualisation,
    description: "NDVI_visualisation",
    scale: 100,
    region: region_circle
});
