import com.google.gson.GsonBuilder
import java.io.FileWriter
import java.io.Writer
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.awt.Rectangle;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.IOException
import javax.swing.JFileChooser
import qupath.lib.images.servers.openslide.OpenslideImageServer
// Optional output path (can be removed)
def pathOutput = chooseDirectory("Choose the data folder")

var gson = GsonTools.getInstance(true)

// Get the current image name
var imageData = QP.getCurrentImageData()

// Remove the file extension ".tif"
imageName = GeneralTools.getNameWithoutExtension(imageData.getServer().getMetadata().getName())

imageName = imageName.substring(0, imageName.lastIndexOf('.'))
print imageName
// Construct the full path for the image folder
def imageFolder = buildFilePath(pathOutput, imageName)

// Check if the image folder exists, create it if not
if (!new File(imageFolder).exists()) {
    new File(imageFolder).mkdirs()
}


// Get selected annotations
var rois = selectedObjects
print rois
for (roi in rois) {
  // Get the annotation name using getName() method
  var annotationName = roi.getName()

  // Extract the wsi folder path from the image path (modify based on your path structure)
  var wsiFolderPath = imageFolder

  // Check if wsi folder exists, create if not
  if (!new File(wsiFolderPath).exists()) {
    new File(wsiFolderPath).mkdirs()
  }

  // Create the annotation folder path within wsi folder
  var annotationFolderPath = buildFilePath(wsiFolderPath, annotationName)

  // Check if annotation folder exists, create if not
  if (!new File(annotationFolderPath).exists()) {
    new File(annotationFolderPath).mkdirs()
  }

  // Build the final JSON file path within the annotation folder
  var fileOutput = buildFilePath(annotationFolderPath, annotationName + ".json")
  print "save annotation to: " + fileOutput

  // Write (save) the JSON file
  try (Writer writer = new FileWriter(fileOutput)) {
    gson.toJson(roi, writer);
  } catch (IOException e) {
    e.printStackTrace()
  }
  
  
  //PARTIE IMAGE 
  // Obtenez le chemin de l'image
  String imagePath = QP.getCurrentImageData().getServer().getURIs()[0].getPath().substring(1);

// Chargez l'image à partir du chemin
  def originalImage = new OpenslideImageServer(QP.getCurrentImageData().getServer().getURIs()[0]);
  print "image : "+originalImage
// Obtenez la région sélectionnée (ROI)
  def region = roi.getROI();
  print region
  // Obtenez les coordonnées de la région
int x = region.getBoundsX()
int y = region.getBoundsY()
int width = region.getBoundsWidth()
int height = region.getBoundsHeight()
  
  // Découpez la région de l'image originale
  BufferedImage regionImage = originalImage.readRegion(1.5,x, y, width, height); //au plu le premier argument est grand au plus la résolution est petite

// Construisez le chemin de sortie pour l'image PNG
  String imageOutputPath = buildFilePath(annotationFolderPath, annotationName + ".png");

// Enregistrez l'image découpée au format PNG
  ImageIO.write(regionImage, "png", new File(imageOutputPath));
}
 
private static String chooseFile(String message) {
    JFileChooser chooser = new JFileChooser()
    chooser.setDialogTitle(message)
    if (chooser.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
        File selectedFile = chooser.getSelectedFile()
        return selectedFile.getAbsolutePath()
    }
    else {
        print "No file selected. Exiting..."
        return null
    }
}
 
 
private static String chooseDirectory(String message) {
    JFileChooser chooser = new JFileChooser()
    chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)
    chooser.setDialogTitle(message)
    if (chooser.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
        File selectedFile = chooser.getSelectedFile()
        return selectedFile.getAbsolutePath()
    }
    else {
        print "No file selected. Exiting..."
        return null
    }
}
 
 
try {
    String pythonExecutable = chooseFile("Select the python executable")
    if(pythonExecutable == null) {
        return null
    }
    String outputFolder = chooseDirectory("Select the working folder")
    if(outputFolder == null) {
        return null
    }
    //pythonScript = new File(new File(outputFolder), "script.py").absolutePath
    var pythonScript = buildFilePath(outputFolder, "script.py")
 
    
    //var name = QP.getCurrentImageName()
    var path = QP.getCurrentImageData().getServer().getURIs()[0].getPath().substring(1)
    ProcessBuilder processBuilder = new ProcessBuilder(pythonExecutable, pythonScript, "--path", outputFolder, "--wsi", path)
    processBuilder.inheritIO()
    Process process = processBuilder.start()
    print "Executing python script"
    int exitCode = process.waitFor()
    print "python script exited with code " + exitCode
} catch(IOException | InterruptedException e) {
    e.printStackTrace()
}