// Load a landsat image and select three bands.
var table = ee.FeatureCollection("users/pudisond/region_borders");

var borders_image = table.style({ "color": "black", "width": 1, "fillColor": "white" });

// Export the image, specifying scale and region.
Export.image.toDrive({
    image: borders_image,
    description: 'BORDERS_visualisation',
    scale: 50,
});
