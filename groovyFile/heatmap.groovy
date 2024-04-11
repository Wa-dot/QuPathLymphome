// Supprimez la ligne qui spécifie le chemin vers un fichier JSON spécifique
// String jsonFilePath = 'C:\\Users\\Computer\\Desktop\\Projet\\QuPathLymphome\\blendmaps2\\WSI 2\\annotation 1\\012B HES.tif - Series 1_0annotation.json'
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
import javax.swing.JFrame
import javax.swing.JOptionPane
import java.nio.file.Files
import java.nio.file.Paths
import com.google.gson.JsonArray
import com.google.gson.JsonElement
import com.google.gson.JsonObject
import com.google.gson.JsonParser

//Clear previous annotation
selectObjects{p -> (p.getLevel()==1) && (p.isAnnotation() == false)};
clearSelectedObjects(false);

boolean heatmap = false

int res = JOptionPane.showOptionDialog(new JFrame(), 'Do you want to display previous heatmap on this image ?', 'Heatmap',
     JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE, null,
     new Object[] { 'Yes', 'No' }, JOptionPane.YES_OPTION)
  if (res == JOptionPane.YES_OPTION) {
    heatmap = true
    println("Display on")
  }
  else{
    println("display off")
  }

// Obtenez le chemin du répertoire du projet
String projectDirectory = 'C:\\Users\\Computer\\Desktop\\Projet\\QuPathLymphome\\blendmaps2\\WSI 2'

if (heatmap) {
    // Utilisez Files pour parcourir tous les fichiers du répertoire
    Files.walk(Paths.get(projectDirectory)).forEach { filePath ->
        // Vérifiez si le fichier est un fichier JSON
        if (Files.isRegularFile(filePath) && filePath.toString().toLowerCase().endsWith('.json')) {
            try {
                // Lisez le contenu du fichier JSON
                String jsonString = new String(Files.readAllBytes(filePath))
                // Parsez le contenu JSON et poursuivez comme avant
                JsonElement element = JsonParser.parseString(jsonString)
                JsonObject jsonObject = element.getAsJsonObject()
                JsonArray tilesArray = jsonObject.getAsJsonArray('tiles')

                // Définissez le plan et les classes de chemin
                int z = 0
                int t = 0
                def plane = ImagePlane.getPlane(z, t)
                def pathclass0 = PathClassFactory.getPathClass('predictor-', 0x800000)
                def pathclass1 = PathClassFactory.getPathClass('predictor+', 0x008000)

                // Liste pour stocker les détections
                def detections = []

                // Itérer sur chaque élément du tableau JSON et créer des objets de détection
                for (JsonElement tileElement : tilesArray) {
                    JsonObject tileObject = tileElement.getAsJsonObject()
                    // Extraire x, y, largeur et hauteur
                    double x = tileObject.get('xmin').getAsDouble()
                    double y = tileObject.get('ymin').getAsDouble()
                    double probability = tileObject.get('lymphoma_probability').getAsDouble()
                    double width = Math.abs(tileObject.get('xmax').getAsDouble() - x)
                    double height = Math.abs(tileObject.get('ymax').getAsDouble() - y)

                    // Créer une ROI basée sur les coordonnées du tile
                    def roi = ROIs.createRectangleROI(x, y, width, height, plane)

                    // Créer un objet de détection basé sur la probabilité
                    def detection
                    if (probability < 0.5) {
                        detection = PathObjects.createDetectionObject(roi, pathclass0)
                } else {
                        detection = PathObjects.createDetectionObject(roi, pathclass1)
                    }

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
