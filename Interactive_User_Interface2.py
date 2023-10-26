import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle

class WindowDesigner:
    def __init__(self, parent):
        self.parent = parent
        self.style_flag = False

    def create_login_window(self):
        parent = self.parent
        parent.setWindowTitle("PMET Login")
        parent.setGeometry(900, 500, 900, 500)
        
       

        # Add a label for "Login"
        helloMsg = QLabel("<h1>Photo-Meta Data Extractor Tool</h1>", parent=parent)
        helloMsg.move(60, 15)

        # Set Icon
        parent.setWindowIcon(QIcon("hsu_logo2.png"))
        # Add a "Login" push button
        parent.loginButton = QPushButton("Login", parent=parent)
        parent.loginButton.move(400, 400)
        parent.loginButton.clicked.connect(parent.open_home)

        # Notify the User to login
        loginInstructions = QLabel("<h5>Please enter your credentials for WorldCat API<h5>", parent=parent)
        loginInstructions.move(60, 150)

        # Create text boxes for username and password
        parent.loginUsername = QLineEdit("Johnny", parent=parent)
        parent.loginPassword = QLineEdit("abc123", parent=parent)
        loginUsernameLabel = QLabel("Username", parent=parent)
        loginPasswordLabel = QLabel("Password", parent=parent)
        loginPasswordLabel.move(200, 310)
        parent.loginUsername.move(200, 250)
        loginUsernameLabel.move(200, 210)
        parent.loginPassword.move(200, 350)

        # Create an option for the user to exit
        parent.exitButton = QPushButton("Exit", parent=parent)
        parent.exitButton.move(560, 400)
        parent.exitButton.clicked.connect(parent.close_window)

    def create_homepage_window(self):
        parent = self.parent
        self.homepage = QMainWindow()  # Create a new window for the homepage
        self.homepage.setWindowTitle("PMET Homepage")
        self.homepage.setGeometry(100, 100, 900, 900)
        self.homepage.setWindowIcon(QIcon("hsu_logo2.png"))
        # Add widgets specific to the homepage
        homepage_label = QLabel("Welcome to the PMET Homepage", parent=self.homepage)
        
        homepage_label.setGeometry(60, 60, 400, 40)  # Adjust the position and size of the label
            

        # You can add more widgets for the homepage here
        self.homepage.selectButton = QPushButton('Select File', parent=self.homepage)
        self.homepage.selectButton.setGeometry(500, 200, 120, 50)
        self.homepage.selectButton.clicked.connect(self.parent.openFile)
        tool_instructions = QLabel("Select a file containing images of documents SuDoc's", parent=self.homepage)
        tool_instructions.setGeometry(100,150,500,50)


        self.homepage.exitButton = QPushButton("Exit", parent=self.homepage)
        self.homepage.exitButton.setGeometry(700, 800,100,50)
        self.homepage.exitButton.clicked.connect(self.parent.closeHomepage)

        self.homepage.selectButton = QPushButton('Begin Query', parent=self.homepage)
        self.homepage.selectButton.setGeometry(500,700,150,50)
        self.homepage.selectButton.clicked.connect(self.parent.beginQuery)

        toggle_theme_button = QPushButton("Toggle Theme", parent=self.homepage)
        toggle_theme_button.setGeometry(650, 100, 200, 50)
        toggle_theme_button.clicked.connect(self.parent.toggleStyle)

        self.homepage.show()  # Show the homepage window

    def close_window(self):
        self.parent.close()

    def verify_path(self, directory_path, window):
        string = "Chosen File was: " + "<em>"+directory_path+"<em>"
        if len(string) > 850 / 8:
            string = string[::850/8]
        path_value = QLabel(string, parent=window.homepage)
        path_value.setGeometry(25, 250, 850, 50)
        path_value.show()
        window.homepage.update()

    
        

class PMETApp(QWidget):
    def __init__(self):
        super().__init__()
        self.designer = WindowDesigner(self)
        self.designer.create_login_window()
        self.homepage = None #Initialize homepage as None
        self.directory_path= None
        self.style_flag = False # added to track the flag state



    def run(self):
        self.show()
        

    def open_home(self):
        # Replace the following line with your authentication logic
        status_code = self.authenticate_user()

        if status_code == 200:
            if self.homepage is None:
                self.designer.parent.close()
                self.homepage = WindowDesigner(self) 
                self.homepage.create_homepage_window() # Store the homepage reference
        else:
            # Display a warning message when login fails
            QMessageBox.critical(self, "Error", "Incorrect Credentials - Please Retry")

    def close_window(self):
        self.close()

    def closeHomepage(self):    
        self.close()
        self.homepage = None

    def authenticate_user(self):
        # Implement your authentication logic here
        # Replace this mock logic with your actual authentication code
        username = self.loginUsername.text()
        password = self.loginPassword.text()

        if username == "Johnny" and password == "abc123":
            return 200  # Authentication successful (replace with your actual success code)
        else:
            return 401  # Authentication failed (replace with your actual failure code)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.open_home()
   
    
    def openFile(self):
        options = QFileDialog.Options()
        directoryPath = QFileDialog.getExistingDirectory(self, "Select a Directory",   options=options)

        if directoryPath:
            print("Selected File:", directoryPath)
            self.directory_path=directoryPath
            self.designer.verify_path(directoryPath,self.homepage)

    def toggleStyle(self):
        self.style_flag = not self.style_flag  # Toggle the style flag
        if self.style_flag:
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            app.setStyleSheet('')

    def beginQuery(self):
        #TBD
        print("If I was a unicorn my life would be better")

if __name__ == '__main__':
    app = QApplication([])  # Create the QApplication instance
    pmet_app = PMETApp()

    toggle_style_button = QPushButton("Toggle Style", pmet_app)
    toggle_style_button.setGeometry(650, 100, 200, 50)
    toggle_style_button.clicked.connect(pmet_app.toggleStyle)

    pmet_app.run()
    sys.exit(app.exec())  # Start the event loop with app.exec()
