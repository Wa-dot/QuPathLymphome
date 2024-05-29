/* groovylint-disable JavaIoPackageAccess, LineLength */
import java.awt.image.BufferedImage
import java.nio.file.Files
import java.nio.file.Paths
import javax.imageio.ImageIO
import javax.swing.JFileChooser
import javax.swing.JFrame
import javax.swing.JOptionPane
import qupath.lib.images.servers.openslide.OpenslideImageServer
import qupath.lib.objects.PathObjects
import qupath.lib.roi.ROIs
import qupath.lib.regions.ImagePlane
import qupath.lib.objects.classes.PathClassFactory
import com.google.gson.JsonArray
import com.google.gson.JsonElement
import com.google.gson.JsonObject
import com.google.gson.JsonParser


PYTHON_ENV_NAME = 'pythonEnv'
SCRIPT_NAME = 'launchApp.py'



// Optional output path (can be removed)
def pathOutput = chooseDirectory('Choose the QupathLymphoma folder')

var gson = GsonTools.getInstance(true)

// Get the current image name
var imageData = QP.getCurrentImageData()

// Remove the file extension ".tif"
imageName = GeneralTools.getNameWithoutExtension(imageData.getServer().getMetadata().getName())

imageName = imageName.substring(0, imageName.lastIndexOf('.'))
print imageName
// Construct the full path for the image folder
def imageFolder = buildFilePath(pathOutput + '\\blendmaps2\\data', imageName)

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
  var fileOutput = buildFilePath(annotationFolderPath, annotationName + '.json')

  // Write (save) the JSON file
  try (Writer writer = new FileWriter(fileOutput)) {
    gson.toJson(roi, writer)
  } catch (IOException e) {
    e.printStackTrace()
  }

  //PARTIE IMAGE
  // Chargez l'image à partir du chemin
  def originalImage = new OpenslideImageServer(QP.getCurrentImageData().getServer().getURIs()[0])
  print 'image : ' + originalImage
  // Obtenez la région sélectionnée (ROI)
  def region = roi.getROI()
  print region
  // Obtenez les coordonnées de la région
  int x = region.getBoundsX()
  int y = region.getBoundsY()
  int width = region.getBoundsWidth()
  int height = region.getBoundsHeight()

  // Découpez la région de l'image originale
  BufferedImage regionImage = originalImage.readRegion(1.5,x, y, width, height) //au plus le premier argument est grand au plus la résolution est petite

  // Construisez le chemin de sortie pour l'image PNG
  String imageOutputPath = buildFilePath(annotationFolderPath, annotationName + '.png')

  // Enregistrez l'image découpée au format PNG
  ImageIO.write(regionImage, 'png', new File(imageOutputPath))
}

private static String chooseFile(String message) {
  JFileChooser chooser = new JFileChooser()
  chooser.setDialogTitle(message)
  if (chooser.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
    File selectedFile = chooser.getSelectedFile()
    return selectedFile.getAbsolutePath()
  }
    else {
    print 'No file selected. Exiting...'
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
    print 'No file selected. Exiting...'
    return null
    }
}
//Clear previous annotation
// selectObjects { p -> (p.getLevel() == 1) && (p.isAnnotation() == false) };
// clearSelectedObjects(false)

int res = JOptionPane.showOptionDialog(new JFrame(), 'Do you want to display previous heatmap on this image ?', 'Heatmap',
     JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE, null,
     new Object[] { 'Yes', 'No' }, JOptionPane.YES_OPTION)
  if (res == JOptionPane.YES_OPTION) {
  println('Display on')
  displayHeatMapOnQupath(imageFolder)
  }
  else {
  println('display off')
  }
 
def displayHeatMapOnQupath(imageFolder) {
  selectObjects { p -> (p.getLevel() == 1) && (p.isAnnotation() == false) };
  clearSelectedObjects(false)
  println('Displaying heatmap')
  // Utiliser Files pour parcourir tous les fichiers du répertoire
  Files.walk(Paths.get(imageFolder)).forEach { filePath ->
        // Vérifier si le fichier est un fichier JSON
        if (Files.isRegularFile(filePath) && filePath.toString().toLowerCase().endsWith('result.json')) {
        try {
          // Lire le contenu du fichier JSON
          String jsonString = new String(Files.readAllBytes(filePath))
          // Parser le contenu JSON et poursuivre comme avant
          JsonElement element = JsonParser.parseString(jsonString)
          JsonObject jsonObject = element.getAsJsonObject()
          JsonArray tilesArray = jsonObject.getAsJsonArray('tiles')
 
          // Définir le plan et les classes de chemin
          int z = 0
          int t = 0
          def plane = ImagePlane.getPlane(z, t)
 
          // Liste pour stocker les détections
          def detections = []
 
          // Itérer sur chaque élément du tableau JSON et créer des objets de détection
          for (JsonElement tileElement : tilesArray) {
            JsonObject tileObject = tileElement.getAsJsonObject()
            // Extraire x, y, largeur et hauteur
            double x = tileObject.get('xmin').getAsDouble()
            double y = tileObject.get('ymin').getAsDouble()
            double probability = tileObject.get('lymphome_probability').getAsDouble()
            double width = Math.abs(tileObject.get('xmax').getAsDouble() - x)
            double height = Math.abs(tileObject.get('ymax').getAsDouble() - y)
 
            // Créer une ROI basée sur les coordonnées du tile
            def roi = ROIs.createRectangleROI(x, y, width, height, plane)
 
          // Créer un objet de détection basé sur la probabilité
 
            def pathclass = PathClass.getInstance('predictor+')
 
            detection = PathObjects.createDetectionObject(roi, pathclass)
            def red = (170 * probability) + 20
            def green = (170 * (1 - probability)) + 20
            def blue = 40
 
            if (probability >= 0 && probability <= 1) {
              detection.setColor((int)red, (int)green, (int)blue)
            }
          else {
              detection.setColor(255, 255, 255)}
 
            // Ajouter l'objet de détection à la liste
            detections.add(detection)
          }
 
          // Ajouter tous les objets de détection au projet QuPath
          addObjects(detections)
        } catch (Exception e) {
          println('Erreur lors de la lecture du fichier: ' + filePath.toString())
          e.printStackTrace()
        }
        }
  }
}

try {
  String pythonExecutable = buildFilePath(pathOutput, PYTHON_ENV_NAME,"Scripts//python.exe")
  print pythonExecutable
  if (pythonExecutable == null) {
    print 'Python path error'
    return null
  }
  String outputFolder = pathOutput + '\\blendmaps2'
  if (outputFolder == null) {
    print 'Output folder error'
    return null
  }
  var pythonScript = buildFilePath(outputFolder, SCRIPT_NAME)

  //var name = QP.getCurrentImageName()
  var path = QP.getCurrentImageData().getServer().getURIs()[0].getPath().substring(1)
  ProcessBuilder processBuilder = new ProcessBuilder(pythonExecutable, pythonScript, '--path', outputFolder, '--wsi', path)
  processBuilder.inheritIO()
  Process process = processBuilder.start()
  print 'Executing python script'
  int exitCode = process.waitFor()
  print 'python script exited with code ' + exitCode
} catch (IOException | InterruptedException e) {
  e.printStackTrace()
}