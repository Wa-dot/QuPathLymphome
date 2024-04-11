import javax.swing.JFrame;
import javax.swing.JOptionPane;
void main() {
  int res = JOptionPane.showOptionDialog(new JFrame(), "Do you like Cricket?","Hobbies",
     JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE, null,
     new Object[] { "Yes", "No" }, JOptionPane.YES_OPTION);
  if (res == JOptionPane.YES_OPTION) {
     println("Selected Yes!");
  } else if (res == JOptionPane.NO_OPTION) {
     println("Selected No!");
  } else if (res == JOptionPane.CLOSED_OPTION) {
     println("Window closed without selecting!");
  }
}
main()