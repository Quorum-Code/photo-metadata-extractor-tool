import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle
from ocr_lines_new import read_data
from query_worker import QueryWorker
from oclc_api import Query, OCLCSession
import json
import pandas as pd

class WindowDesigner:
    def __init__(self, parent):
        self.parent = parent
        self.style_flag = False
        self.path_value = None #initialize path_value as None
        self.path_message = None

    def create_login_window(self):
        parent = self.parent
        parent.setWindowTitle("PMET Login")
        parent.setGeometry(900, 500, 900, 500)
        
        # Add a label for "Login"
        program_label = QLabel("<h1>Photo-Meta Data Extractor Tool</h1>", parent=parent)
        program_label.setGeometry(60, 15,750,50)

        # Set Humboldt logo icon on taskbar
        parent.setWindowIcon(QIcon("hsu_logo2.png"))
        
        # Add a "Login" push button
        parent.loginButton = QPushButton("Login", parent=parent)
        parent.loginButton.setGeometry(400, 400, 100,50)
        parent.loginButton.clicked.connect(parent.open_home)

        # Notify user to enter credential for .sercrets file
        loginInstructions = QLabel("<h5>Please enter your credentials for WorldCat API<h5>", parent=parent)
        loginInstructions.setGeometry(60, 150,600,50)

        # Create text boxes for username and password
        parent.loginUsername = QLineEdit("Johnny", parent=parent)
        parent.loginPassword = QLineEdit("abc123", parent=parent)
        loginUsernameLabel = QLabel("Username", parent=parent)
        loginPasswordLabel = QLabel("Password", parent=parent)
        loginPasswordLabel.setGeometry(200, 310,300,50)
        parent.loginUsername.move(200, 250)
        loginUsernameLabel.setGeometry(200, 210,300,50)
        parent.loginPassword.move(200, 350)

        # Create an option for the user to exit
        parent.exitButton = QPushButton("Exit", parent=parent)
        parent.exitButton.setGeometry(560, 400, 100,50)
        parent.exitButton.clicked.connect(parent.close_window)

    """
        create_homepage_window:
            Creates an instance of the homepage instance of
            the PMET tool    
    """

    def create_homepage_window(self):
        parent = self.parent
        self.homepage = QMainWindow()  # Create a new window for the homepage
        self.homepage.setWindowTitle("PMET Homepage")
        self.homepage.setGeometry(100, 100, 900, 900)
        self.homepage.setWindowIcon(QIcon("hsu_logo2.png"))
        # Add widgets specific to the homepage
        homepage_label = QLabel("Welcome to the PMET Homepage", parent=self.homepage)
        
        homepage_label.setGeometry(60, 60, 400, 40)  # Adjust the position and size of the label
            

        # Create select folder button along with label
        self.homepage.selectButton = QPushButton('Select File', parent=self.homepage)
        self.homepage.selectButton.setGeometry(500, 200, 120, 50)
        self.homepage.selectButton.clicked.connect(self.parent.openFile)
        tool_instructions = QLabel("Select a file containing images of documents SuDoc's", parent=self.homepage)
        tool_instructions.setGeometry(100,150,500,50)

        # Create a push button for begin OCLC query process
        self.homepage.beginquery = QPushButton('Begin Query', parent = self.homepage)
        self.homepage.beginquery.setGeometry(500, 700, 120, 50)
        self.homepage.beginquery.clicked.connect(self.parent.beginQuery)

        # Create an exit button to close window
        self.homepage.exitButton = QPushButton("Exit", parent=self.homepage)
        self.homepage.exitButton.setGeometry(700, 800,100,50)
        self.homepage.exitButton.clicked.connect(self.parent.closeHomepage)

        # Create a button to begin image proccesing 
        self.homepage.selectButton = QPushButton('Process Images', parent=self.homepage)
        self.homepage.selectButton.setGeometry(500,350,200,50)
        self.homepage.selectButton.clicked.connect(self.parent.beginImageProcessing)

        # Toggle theme button 
        toggle_theme_button = QPushButton("Toggle Theme", parent=self.homepage)
        toggle_theme_button.setGeometry(650, 100, 200, 50)
        toggle_theme_button.clicked.connect(self.parent.toggleStyle)

        # Display window
        self.homepage.show()  # Show the homepage window

    def close_window(self):
        self.parent.close()

    """
        verify_path:
           Displays choosen directory path from user in window for user verification 
           if path is larger than window the path is truncated fit on screen   
    """

    def verify_path(self, directory_path, window):
        if self.path_value:
            self.path_value.deleteLater()
            window.homepage.update()
        if len(directory_path) > 850 / 9:
            verifiedString =  "Chosen File was: \n "+ "..." + directory_path[-int(850/12)::]
        else:
            verifiedString = "Chosen File was: \n " +  directory_path
        self.path_value = QLabel(verifiedString, parent=window.homepage)
        self.path_value.setGeometry(20, 260, 850, 50)
        if self.path_message:
            self.path_message.deleteLater()
        self.path_value.show()
        window.homepage.update()

    """
        choose_path:
            Pings user in the case a process request is made before a direcotry is choosen
    """
    def choose_path(self,window):
        self.path_message = QLabel("Please pick a directory before begining Procesing", parent=window.homepage)
        self.path_message.setGeometry(200, 600, 850, 50)
        self.path_message.show()
        window.homepage.update()

    """
        single_query_warning:
            Pings user in the case a process request is made twice and before the first request
            has been completed
    """

    def single_query_warning(self,window):
        self.path_warning = QLabel("Please wait for the first query to finish", parent=window.homepage)
        self.path_warning.setGeometry(100,700,850,50)
        self.path_warning.show()
        window.homepage.update()

    
class PMETApp(QWidget):

    
    """
        Attributes:

        designer: An instance of Window designer which is orignally
                  instantiated as teh login window.
        
        homepage: Instance of the homepage window.

        directory_path: Choosen file path for image selection
        style_flag: Flag variable for window color theme.
        
        query_worker: Intance of queryWorker to thread image proccessing.

        extracted_csv: Holds proccessed SuDoc text and query data.

        credential: Flag variable for active API token session.

        credentials_saved: Flag variable for creation of .sercrets file    .
    """

    def __init__(self):
        
        """
            Generation of the intial interface window along with needed functionality
            for operating within the program     
        
        """
        super().__init__()
        self.designer = WindowDesigner(self)
        self.designer.create_login_window()
        self.homepage = None #Initialize homepage as None
        self.directory_path= None
        self.style_flag = False # added to track the flag state
        self.query_worker = None
        self.extracted_csv = None
        self.credential = False
        self.credentials_saved = False
        self.OCLC = None

    def run(self):
        self.show()
        
    """
        open_home:
            Saves login credentials to .secrets and takes user to the programs main page
    """   

    def open_home(self):
        self.grab_credentials()
        if self.credentials_saved:
            if self.credentials_saved:
                self.designer.parent.close()
                self.homepage = WindowDesigner(self) 
                self.homepage.create_homepage_window() # Store the homepage reference
        else:
            # Display a warning message when login fails
            QMessageBox.critical(self, "Error", "Please input your credentials")

    def close_window(self):
        self.close()

    def closeHomepage(self):    
        self.close()
        self.homepage = None

    def authenticate_user(self):
        if self.OCLC.hasToken:
            self.credential = True
            print("login success")
            return 200  # Authentication successful 
        else:
            print("login failure")
            return 401  # Authentication failed 
        
    """
        grab_credentials: 
            Writes credential inputted at the login hompage into 
            the .sercrets file for later proccessing
    """

    def grab_credentials(self):
        if not self.credentials_saved:
            file = open(".secrets_temp","w")
            string = "[SECRETS] \nclient_id= " + self.loginUsername.text() + "\nclient_secret = " +  self.loginPassword.text()
            file.write(string)
            self.credentials_saved = True
            

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.open_home()
   
    """
        openFile: 
            Allows user to toggle directory path for image proccessing
    """
    def openFile(self):
        options = QFileDialog.Options()
        directoryPath = QFileDialog.getExistingDirectory(self, "Select a Directory",   options=options)

        if directoryPath:
            print("Selected File:", directoryPath)
            self.directory_path=directoryPath
            self.designer.verify_path(directoryPath,self.homepage)
    """
        toggleStyle:
            Changes window theme
    """
    def toggleStyle(self):
        self.style_flag = not self.style_flag  # Toggle the style flag
        if self.style_flag:
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            app.setStyleSheet('')

    """
        beginImageProccessing:
            Instantiates a query_worker instance to run image
            query proccess from user-selected folder on another thread
    """

    def beginImageProcessing(self):
        if self.query_worker is not None:
            print("A query is already in progress. Please wait for it to finish")
            self.designer.single_query_warning(self.homepage)
        elif self.directory_path:
            self.query_worker = QueryWorker(self.directory_path)
            self.query_worker.finished.connect(self.queryFinished)
            self.query_worker.result_ready.connect(self.handleResult)  # Connect the signal to the slot
            self.query_worker.start()
            print(self.extracted_csv)
        else:
            self.designer.choose_path(self.homepage)
    
    """ 
        queryFinished:
            Removes query worker instance
    """

    def queryFinished(self):
        print("Query finished")
        self.query_worker = None

    def handleResult(self,result):
        print("Query Result:", result)
        self.extracted_csv = result
    
    """
        BeginQuery:
            Begins processing already extracted text through begining 
            a query through the CCLC class
    """

    def beginQuery(self):
        if not self.extracted_csv:
            print("ping user to process images first")
            #FIX
        if self.credential:
            print("no credential")  
            self.extract_query_data()
        else:
            print("current credential")
            self.OCLC = OCLCSession("config.ini") #create OCLCSession Instance
            token_response = self.authenticate_user() #Verify user login to the system
            if token_response == 200:
                self.credentail = True
                self.extract_query_data()              
            else:
                print("create error function ping user to relogin")
            #add a function call for 


    def extract_query_data(self):
        extracted_sudocs = pd.read_csv("./extracted_data/extracted_data.csv")
        print(extracted_sudocs)

        for i in range(len(extracted_sudocs)):
            print(len(extracted_sudocs))
            print(extracted_sudocs.loc[i, "SuDoc"])
            query_result = self.OCLC.query(extracted_sudocs.loc[i, "SuDoc"])
            query_result = json.loads(query_result)
            print(query_result)
            if int(query_result["numberOfRecords"]) != 1:
                if extracted_sudocs.loc[i, "Query Status"]:
                    extracted_sudocs.loc[i, "Query Status"] += 1
                else:
                    print(extracted_sudocs.loc[i, "Query Status"], extracted_sudocs.loc[i, "SuDoc"])
                    extracted_sudocs.loc[i, "Query Status"] = 1
                    print(extracted_sudocs.loc[i, "Query Status"])

                print("Start error sequence")

                if int(query_result["numberOfRecords"]) > 1:
                    extracted_sudocs.loc[i, "Error Code"] = "multiple records"

                if int(query_result["numberOfRecords"]) == 0:
                    extracted_sudocs.loc[i, "Error Code"] = "no records"
            else:
                text = query_result['bibRecords'][0]['title']['mainTitles'][0]['text']
                year = query_result['bibRecords'][0]['date']['publicationDate']

                extracted_sudocs.loc[i, "Title"] = text
                extracted_sudocs.loc[i, "Publication Year"] = year

        extracted_sudocs.reset_index(drop=True, inplace=True)
        extracted_sudocs.to_csv("extracted_data/extracted_data.csv", index=False)
        self.verify_extracted_data()


    def verify_extracted_data(self):
        extracted_sudocs = pd.read_csv('./extracted_data/extracted_data.csv')
        extracted_sudocs = extracted_sudocs.dropna()
        pending_queries = pd.concat([extracted_sudocs[extracted_sudocs['Error Code'] == "no records"],
                                     extracted_sudocs[extracted_sudocs['Error Code'] == "multiple records"]])
        for i in pending_queries["Error Code"]:
            print(i)

if __name__ == '__main__':
    app = QApplication([])  # Create the QApplication instance
    pmet_app = PMETApp()
    toggle_style_button = QPushButton("Toggle Style", pmet_app)
    toggle_style_button.setGeometry(650, 100, 200, 50)
    toggle_style_button.clicked.connect(pmet_app.toggleStyle)
  
    pmet_app.run()
    sys.exit(app.exec())  # Start the event loop with app.exec()
