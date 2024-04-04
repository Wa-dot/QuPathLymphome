import com.google.gson.GsonBuilder
import java.io.FileWriter
import java.io.Writer
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
 
import java.io.IOException
import javax.swing.JFileChooser
 
// chemin desiré 
def pathOutput = 'C:\\Users\\Computer\\Desktop\\Projet\\groovyFile\\jsonfile'
 
var gson = GsonTools.getInstance(true)
 
// nom du fichier de sortie a enregister 
var imageData = QP.getCurrentImageData()
var name = GeneralTools.getNameWithoutExtension(imageData.getServer().getMetadata().getName())
 
//nom du fichier en fonction de :dateheuresseconds
def timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date())
var fileOutput = buildFilePath(pathOutput, name + "_" + timestamp)
print "save annotation: "+fileOutput+".json"
 
var rois = selectedObjects
 
// write (save) the json file
try (Writer writer = new FileWriter(fileOutput+".json")) {
    gson.toJson(rois, writer);
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
    
    String pythonExecutable = "C:\\Users\\Computer\\Desktop\\Projet\\QuPathLymphome\\lymphome_containers\\python.exe"
    if(pythonExecutable == null) {
        return null
    }
    
    String outputFolder = "C:\\Users\\Computer\\Desktop\\Projet\\groovyFile"
    if(outputFolder == null) {
        return null
    }
    
    //pythonScript = new File(new File(outputFolder), "script.py").absolutePath
    var pythonScript = "C:\\Users\\Computer\\Desktop\\Projet\\groovyFile\\main.py"
 
    
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