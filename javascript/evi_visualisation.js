// Load a landsat image and select three bands.
var geometry = /* color: #d63000 */ee.Geometry.Point([18.727861612562833, 49.23260382795243]);
var landsat_collection = ee.ImageCollection("LANDSAT/LE07/C01/T1");
var landsat = ee.Algorithms.Landsat.simpleComposite({ "collection": landsat_collection, "asFloat": true });

var red = landsat.select("B3")
var blue = landsat.select("B1")
var infrared = landsat.select("B4")

var evi_landsat = landsat.addBands(infrared.subtract(red)
                                           .multiply(2.5)
                                           .divide(infrared.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)));

var evi_visualisation = evi_landsat.visualize({
    "min": -0.2,
    "max": 1,
    "bands": ["B4_1"],
    "palette": [
        'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901',
        '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01',
        '012E01', '011D01', '011301'
    ]
});

var region_circle = geometry.buffer(40000);

// Export the image, specifying scale and region.
Export.image.toDrive({
    image: evi_visualisation,
    description: "EVI_visualisation",
    scale: 50,
    region: region_circle
});
