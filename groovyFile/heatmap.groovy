import qupath.lib.objects.PathObjects
import qupath.lib.roi.ROIs
import qupath.lib.regions.ImagePlane
import qupath.lib.objects.classes.PathClassFactory
import qupath.lib.gui.dialogs.Dialogs
import java.nio.file.Files
import java.nio.file.Paths
import java.lang.reflect.Type
import java.util.List
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

//Clear previous annotation
selectObjects{p -> (p.getLevel()==1) && (p.isAnnotation() == false)};
clearSelectedObjects(false);


/* Define classes for JSON parsing */
class Coordinates {
    long x
    long y
    long width
    long height
}

class Geometry {
    Coordinates coordinates
}

class Properties {
    String objectType
}

class Feature {
    String id
    Geometry geometry
    Properties properties
    float probability
}

// Get the location of the JSON file
def jsonfile = "C:\\Users\\Computer\\Desktop\\Projet\\groovyFile\\jsonfile\\testColor.json"

// Read the JSON file
String json = new String(Files.readAllBytes(Paths.get(jsonfile)))

// Create a Gson object
Gson gson = new Gson()

// Define the type of the objects in the JSON file
Type listType = new TypeToken<List<Feature>>() {}.type

// Parse the JSON file into a list of Feature objects
List<Feature> features = gson.fromJson(json, listType)

// Define plane and path classes
int z = 0
int t = 0
def plane = ImagePlane.getPlane(z, t)
def pathclass0 = PathClassFactory.getPathClass("predictor-", 0x800000)
def pathclass1 = PathClassFactory.getPathClass("predictor+", 0x008000)

// List to store detections
def detections = []

// Iterate over each feature and create detection objects
features.each { feature ->
    // Print feature information for debugging
    println("ID: ${feature.id}")
    println("Geometry - X: ${feature.geometry.coordinates.x}, Y: ${feature.geometry.coordinates.y}, Width: ${feature.geometry.coordinates.width}, Height: ${feature.geometry.coordinates.height}")
    println("Object Type: ${feature.properties.objectType}")
    println("Probability: ${feature.probability}")
    println("-----")

    // Create ROI based on feature coordinates
    def roi = ROIs.createRectangleROI(feature.geometry.coordinates.x, feature.geometry.coordinates.y, feature.geometry.coordinates.width, feature.geometry.coordinates.height, plane)
    
    // Create detection object based on feature probability
    def detection
    if (feature.probability < 0.5) {
        detection = PathObjects.createDetectionObject(roi, pathclass0)
    } else {
        detection = PathObjects.createDetectionObject(roi, pathclass1)
    }
    
    // Add detection object to the list
    detections.add(detection)
}

// Add all detection objects to the QuPath project
addObjects(detections)
