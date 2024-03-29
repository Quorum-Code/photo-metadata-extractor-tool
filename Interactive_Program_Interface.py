import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle
from ocr_lines import read_data
from query_worker import QueryWorker
from oclc.oclc_api import *
import json
import pandas as pd
import os
import datetime


class WindowDesigner:
    """
        parent: sets the window instance
        style_flag: signifies style theme
        path_value: user choosen directory for images
        path_message: display of choosen directory 
        status_bar: Bar to display image-proccessing status
        sudoc_image_label: Label to hold pixmap image for display
        title_image_label: Label to holp pixmap image for display
        path_warning: displayed warning for necessary path selection
        image_warning: displayed warning for necessary image processing
        query_in_process: displayed warning during query process
        query_sucess_rate: value for displaying total successful queries
    """

    def __init__(self, parent):
        self.parent = parent
        self.style_flag = False
        self.path_value = None  # initialize path_value as None
        self.path_message = None
        self.status_bar = None
        self.sudoc_image_label = None
        self.title_image_label = None
        self.path_warning = None
        self.image_warning = None
        self.query_in_process = None
        self.success_rate = None

    def create_login_window(self) -> None:
        """
        create_login_window:
            generates the login window
        
        """
        parent = self.parent
        parent.setWindowTitle("PMET Login")
        parent.setGeometry(900, 500, 900, 500)

        # Add a label for "Login"
        program_label = QLabel("<h1>Photo-Meta Data Extractor Tool</h1>", parent=parent)
        program_label.setGeometry(60, 15, 750, 50)

        # Set Humboldt logo icon on taskbar
        parent.setWindowIcon(QIcon("hsu_logo2.png"))

        # Add a "Login" push button
        parent.loginButton = QPushButton("Login", parent=parent)
        parent.loginButton.setGeometry(400, 400, 100, 50)
        parent.loginButton.clicked.connect(parent.open_home)

        # Notify user to enter credential for .sercrets file
        loginInstructions = QLabel("<h5>Please enter your credentials for WorldCat API<h5>", parent=parent)
        loginInstructions.setGeometry(60, 150, 600, 50)

        # Create text boxes for username and password
        parent.loginUsername = QLineEdit("Johnny", parent=parent)
        parent.loginPassword = QLineEdit("abc123", parent=parent)
        loginUsernameLabel = QLabel("Username", parent=parent)
        loginPasswordLabel = QLabel("Password", parent=parent)
        loginPasswordLabel.setGeometry(200, 310, 300, 50)
        parent.loginUsername.move(200, 250)
        loginUsernameLabel.setGeometry(200, 210, 300, 50)
        parent.loginPassword.move(200, 350)

        # Create an option for the user to exit
        parent.exitButton = QPushButton("Exit", parent=parent)
        parent.exitButton.setGeometry(560, 400, 100, 50)
        parent.exitButton.clicked.connect(parent.close_window)

        toggle_style_button = QPushButton("Toggle Style", parent=parent)
        toggle_style_button.setGeometry(650, 100, 200, 50)
        toggle_style_button.clicked.connect(parent.toggle_style)

        parent.show()

    def create_homepage_window(self) -> None:
        """
        create_homepage_window:
            Creates an instance of the homepage instance of
            the PMET tool    
        """
        parent = self.parent
        self.homepage = QMainWindow()  # Create a new window for the homepage
        self.homepage.setWindowTitle(" PMET Homepage")
        self.homepage.setGeometry(100, 100, 900, 900)
        self.homepage.setWindowIcon(QIcon("hsu_logo2.png"))
        # Add widgets specific to the homepage
        homepage_label = QLabel("Welcome to the PMET Homepage", parent=self.homepage)

        print(type(self.status_bar))
        homepage_label.setGeometry(60, 60, 400, 40)  # Adjust the position and size of the label

        # Create select folder button along with label
        self.homepage.selectButton = QPushButton('Select File', parent=self.homepage)
        self.homepage.selectButton.setGeometry(500, 200, 200, 50)
        self.homepage.selectButton.clicked.connect(self.parent.open_file)
        tool_instructions = QLabel("Select a file containing images of documents SuDoc's", parent=self.homepage)
        tool_instructions.setGeometry(100, 150, 520, 50)

        # Create a push button for begin OCLC query process
        self.homepage.beginquery = QPushButton('Begin Query', parent=self.homepage)
        self.homepage.beginquery.setGeometry(500, 700, 200, 50)
        self.homepage.beginquery.clicked.connect(self.parent.begin_query)

        # Create an exit button to close window
        self.homepage.exitButton = QPushButton("Exit", parent=self.homepage)
        self.homepage.exitButton.setGeometry(680, 800, 200, 50)
        self.homepage.exitButton.clicked.connect(self.parent.close_homepage)

        # Create a button to begin image proccesing 
        self.homepage.selectButton = QPushButton('Process Images', parent=self.homepage)
        self.homepage.selectButton.setGeometry(500, 340, 200, 50)
        self.homepage.selectButton.clicked.connect(self.parent.begin_image_processing)

        # Toggle theme button 
        toggle_theme_button = QPushButton("Toggle Theme", parent=self.homepage)
        toggle_theme_button.setGeometry(680, 100, 200, 50)
        toggle_theme_button.clicked.connect(self.parent.toggle_style)

        self.homepage.show()  # Show the homepage window

    def create_verification_window(self) -> QMainWindow:
        """
            create_verification_window:
            creates an instance of the verification window
        
        """
        self.verification_window = QMainWindow()  # Create a new window for the homepage
        self.verification_window.setWindowTitle(" PMET: Verifier")
        self.verification_window.setGeometry(100, 100, 900, 900)
        self.verification_window.setWindowIcon(QIcon("hsu_logo2.png"))

        self.verification_window.verify = QPushButton("Verify", parent=self.verification_window)
        self.verification_window.verify.setGeometry(400, 800, 200, 50)
        self.verification_window.verify.clicked.connect(self.parent.update_exceptions)

        self.sudoc_image_label = None
        self.title_image_label = None

        self.verification_window.show()
        return self.verification_window

    def update_verification_window(self, image_path, sudoc_path, extracted_sudoc, extracted_title,
                                   extracted_year) -> None:

        """
        update_verification_window:
            Updates the window to diplay the images and previously extracted data for those image instances
        """

        if self.title_image_label is not None:
            self.title_image_label.deleteLater()
        if self.sudoc_image_label is not None:
            self.sudoc_image_label.deleteLater()

        self.title_image_label = QLabel(parent=self.verification_window)
        self.sudoc_image_label = QLabel(parent=self.verification_window)
        pixmap = QPixmap(str(image_path))
        pixmap2 = QPixmap(str(sudoc_path))

        if (pixmap.height() > 0):
            aspect_ratio = pixmap.width() / pixmap.height()

        new_width = 475
        new_height = 475

        pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio)
        self.title_image_label.setPixmap(pixmap)

        if (pixmap2.height() > 0):
            aspect_ratio = pixmap.width() / pixmap.height()

        pixmap2 = pixmap2.scaled(new_width, new_height, Qt.KeepAspectRatio)
        self.sudoc_image_label.setPixmap(pixmap2)

        print("VERIFICATION IS CALLED")
        extracted_title = str(extracted_title)
        extracted_sudoc = str(extracted_sudoc)
        extracted_year = str(extracted_year)

        self.verification_window.sudoc_textbox = QLineEdit(extracted_sudoc, parent=self.verification_window)
        self.verification_window.sudoc_label = QLabel("SuDoc", parent=self.verification_window)
        self.verification_window.title_label = QLabel("Title", parent=self.verification_window)
        self.verification_window.pub_label = QLabel("Publication Year", parent=self.verification_window)
        self.verification_window.publication_year = QLineEdit(extracted_year, parent=self.verification_window)

        if len(extracted_title) > 200:
            extracted_title = extracted_title[::300]
        self.verification_window.title_textbox = QLineEdit(extracted_title, parent=self.verification_window)

        self.verification_window.title_label.setGeometry(10, 660, 300, 50)
        self.verification_window.sudoc_label.setGeometry(350, 660, 300, 50)
        self.verification_window.pub_label.setGeometry(10, 750, 300, 50)

        box_width = max(pixmap.width(), pixmap2.width())
        box_height = max(pixmap.height(), pixmap2.height())

        self.sudoc_image_label.setGeometry(10, 10, box_width, box_height)
        self.title_image_label.setGeometry(470, 10, box_width, box_height)
        self.verification_window.sudoc_textbox.setGeometry(10, 710, 300, 30)
        self.verification_window.title_textbox.setGeometry(350, 710, 400, 30)
        self.verification_window.publication_year.setGeometry(10, 800, 300, 30)

        self.title_image_label.show()
        self.sudoc_image_label.show()
        self.verification_window.pub_label.show()
        self.verification_window.publication_year.show()
        self.verification_window.sudoc_textbox.show()
        self.verification_window.title_textbox.show()
        self.verification_window.sudoc_label.show()
        self.verification_window.title_label.show()

        self.verification_window.update()
        self.verification_window.show()

    def close_window(self) -> None:
        """
        close_window: 
            Closes the window instance
        """
        self.parent.close()

    def verify_path(self, directory_path, window) -> None:
        """
        verify_path:
           Displays choosen directory path from user in window for user verification 
           if path is larger than window the path is truncated fit on screen   
        """
        if self.path_value:
            self.path_value.deleteLater()
            window.homepage.update()
        if len(directory_path) > 850 / 9:
            verifiedString = "Chosen File was: \n " + "..." + directory_path[-int(850 / 12)::]
        else:
            verifiedString = "Chosen File was: \n " + directory_path
        self.path_value = QLabel(verifiedString, parent=window.homepage)
        self.path_value.setGeometry(20, 260, 850, 60)
        if self.path_message:
            self.path_message.deleteLater()
        self.path_value.show()
        window.homepage.update()

    def choose_path(self, window) -> None:
        """
        choose_path:
            Pings user in the case a process request is made before a direcotry is choosen
        """
        self.path_message = QLabel("Please pick a directory before begining Procesing", parent=window.homepage)
        self.path_message.setGeometry(200, 600, 850, 50)
        self.path_message.show()
        window.homepage.update()

    def single_query_warning(self, window) -> None:
        """
        single_query_warning:
            Pings user in the case a process request is made twice and before the first request
            has been completed
        """
        if not self.path_warning:
            self.path_warning = QLabel("Please wait for the first query to finish", parent=window.homepage)
            self.path_warning.setGeometry(10, 700, 450, 50)
            self.path_warning.show()
            window.homepage.update()

    def single_query_warning_delete(self, window) -> None:
        """
        single_query_warning_delete:
            removes the single_query_warning after image proccessing has been completed
        """
        if self.path_warning:
            self.path_warning.deleteLater()
            self.path_warning = None
            window.homepage.update()

    def update_progress_bar(self, progress) -> None:
        """
        updateProgressBar
            updates the progress bar     
        """
        progress_percentage = int(progress * 100)
        self.status_bar.setValue(progress_percentage)

    def create_progress_bar(self, window) -> None:
        """
        createProgressBar
            Generates an initial progress bar and shows it within
            then window
        """
        self.status_bar = QProgressBar(parent=window.homepage)
        self.status_bar.setGeometry(200, 400, 400, 20)
        self.status_bar.show()
        window.homepage.update()

    def preview_results(self, window, string) -> None:
        """
        previewResults
            Updates the window to display a button associated
            with the function "preview"    
        """
        # if self.preview:
        # self.preview.deleteLater()
        self.preview = QLabel(string, parent=window.homepage)
        self.preview.setGeometry(100, 460, 180, 150)
        self.preview.show()
        window.homepage.update()

    def query_finished(self, window) -> None:
        """
        query_finished
            Updates the window to download the results from a successful
            query
        """
        self.downloadButton = QPushButton('Download Results', parent=self.homepage)
        self.downloadButton.setGeometry(100, 700, 200, 50)
        self.downloadButton.clicked.connect(self.parent.download_csv)
        self.downloadButton.show()
        window.homepage.update()

    def preview(self, window) -> None:
        """
        previewResults
            Displays in text form the head of the error codes
            within the dataframe after the query process
        """
        self.previewButton = QPushButton('Preview Results', parent=self.homepage)
        self.previewButton.setGeometry(100, 640, 200, 50)
        self.previewButton.clicked.connect(self.parent.preview_csv)
        self.previewButton.show()
        window.homepage.update()

    def toggleClose(self, window) -> None:
        """
        toggleClose
            Creates a buttun on the homepage window and connects
            its to the new_query function within the PMET App. Allowing
            the user to reinitialize the program and begin a new query.
        """
        self.closeButton = QPushButton('New Query', parent=self.homepage)
        self.closeButton.setGeometry(100, 760, 200, 50)
        self.closeButton.clicked.connect(self.parent.new_query)
        self.closeButton.show()
        window.homepage.update()

    def querySuccessRate(self, window, found, total) -> None:
        """
        querySuccessRate: 
            Displays the total number of documents which are able
            to be found during the query process
    
        """
        if not self.success_rate:
            self.success_rate = QLabel(str(found) + " of " + str(total) + " found.", parent=window.homepage)
            self.success_rate.setGeometry(510, 600, 150, 50)
            self.success_rate.show()
            window.homepage.update()
            QApplication.processEvents()

    def query_success_rate_delete(self, window, callback) -> None:
        """
            query_success_rate_delete: 
                Deletes success rate message from the window
        
        """
        if self.success_rate:
            self.success_rate.deleteLater()
            self.success_rate = None
            window.homepage.update()
            QCoreApplication.processEvents()
        callback()

    def process_images_first_warning(self, window) -> None:
        """
        process_images_first_warning:
            Warns the user to process users before instantiating a query
        """
        if not self.image_warning:
            self.image_warning = QLabel("Please process images first", parent=window.homepage)
            self.image_warning.setGeometry(10, 410, 450, 50)
            self.image_warning.show()
            window.homepage.update()

    def process_images_first_delete(self, window) -> None:
        """
        process_images_first_delete:
            Updates window to delete warning message after user processes images
        """
        if self.image_warning:
            self.image_warning.deleteLater()
            self.image_warning = None
            window.homepage.update()

    def query_in_process_warning(self, window, callback) -> None:
        """
            query_in_process_warning:
                displays a warning to the window that a query is running
        
        """
        if not self.query_in_process:
            self.query_in_process = QLabel("Querying...Please Wait", parent=window.homepage)
            self.query_in_process.setGeometry(510, 650, 250, 50)
            self.query_in_process.show()
            window.homepage.update()
        QApplication.processEvents()
        callback()

    def query_in_process_warning_delete(self, window) -> None:
        """
        query_in_process_warning:
           deletes the displayed warning that a query is running to the window
        """
        if self.query_in_process:
            self.query_in_process.deleteLater()
            self.query_in_process = None
            window.homepage.update()

    def update_window_events(self) -> None:
        """
            update_window_events:
            forces window to update un-processed events before preceding
        """
        QApplication.processEvents()


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

        credentials_saved: Flag variable for creation of .sercrets file  

        OCLC: Holds an instance of the OCLC class for the query process  

        verification_window: Holds an instance of the WindowDesigner class 

        exceptions: A list value of all pending queries after a query instantiation
    """

    def __init__(self):

        """
            Generation of the intial interface window along with needed functionality
            for operating within the program     
        
        """
        super().__init__()
        self.designer = WindowDesigner(self)
        self.designer.create_login_window()
        self.homepage = None  # Initialize homepage as None
        self.directory_path = None
        self.style_flag = False  # added to track the flag state
        self.query_worker = None
        self.extracted_csv = None
        self.credential = False
        self.credentials_saved = False
        self.OCLC = None
        self.verification_window = None
        self.exceptions = None
        self.query_in_process = False

    def run(self) -> None:
        """
        run:
            displays the program
        """
        self.show()

    def open_home(self) -> None:
        """
        open_home:
            Saves login credentials to .secrets and takes user to the programs main page
        """
        self.grab_credentials()
        self.OCLC = OCLCSession("config.ini")  # create OCLCSession Instance
        token_response = self.authenticate_user()  # Verify user login to the system
        print(token_response)
        if token_response == 200:
            self.credentail = True
            self.designer.parent.close()
            self.homepage = WindowDesigner(self)
            self.homepage.create_homepage_window()  # Store the homepage reference

    def close_window(self) -> None:
        """
        close_window:
            closes the window instance
        """
        self.close()

    def close_homepage(self) -> None:
        """
        close_homepage:
            closes the window instance
        """
        self.close()
        # os.remove("./extracted_data/extracted_data.csv") UNCOMMENT IN FINAL VERSION!
        self.homepage = None

    def authenticate_user(self) -> int:
        """
        authenticate_user:
            Returns the login status code for collecting the API token
        """
        print(self.OCLC.hasToken)
        if self.OCLC.hasToken:
            self.credential = True
            print("login success")
            return 200  # Authentication successful 
        else:
            print("login failure")
            QMessageBox.critical(self, "Error", "Please check your credentials")
            self.credentails_saved = False
            return 401  # Authentication failed 

    def grab_credentials(self) -> None:
        """
        grab_credentials: 
            Writes credential inputted at the login hompage into 
            the .sercrets file for later proccessing
        """
        print(self.credentials_saved)
        file = open(".secrets", "w")
        print(self.loginUsername.text(), self.loginPassword.text())
        string = "[SECRETS] \nclient_id = " + self.loginUsername.text() + "\nclient_secret = " + self.loginPassword.text()
        file.write(string)
        self.credentials_saved = True

    def keyPressEvent(self, event) -> None:
        """
        Defines a keypressEvent so users can loging by hitting "enter"
        """
        if event.key() == Qt.Key_Return:
            self.open_home()

    def open_file(self) -> None:
        """
        open_file: 
            Allows user to toggle directory path for image proccessing
        """
        options = QFileDialog.Options()
        directoryPath = QFileDialog.getExistingDirectory(self, "Select a Directory", options=options)
        if directoryPath:
            print("Selected File:", directoryPath)
            self.directory_path = directoryPath
            self.designer.verify_path(directoryPath, self.homepage)

    def toggle_style(self) -> None:
        """
        toggle_style:
            Changes window theme
         """
        self.style_flag = not self.style_flag  # Toggle the style flag
        if self.style_flag:
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            app.setStyleSheet('')

    def begin_image_processing(self) -> None:
        """
        begin_image_proccessing:
            Instantiates a query_worker instance to run image
            query proccess from user-selected folder on another thread
        """
        self.designer.process_images_first_delete(self.homepage)
        if self.query_worker is not None:
            print("A query is already in progress. Please wait for it to finish")
            self.designer.single_query_warning(self.homepage)
        elif self.directory_path:
            self.designer.create_progress_bar(self.homepage)
            self.query_worker = QueryWorker(self.directory_path)
            self.query_worker.finished.connect(self.query_finished)
            self.query_worker.result_ready.connect(self.handle_result)  # Connect the signal to the slot
            self.query_worker.progress_updated.connect(self.designer.update_progress_bar)  # Connect the progress signal

            self.designer.status_bar.setValue(0)
            self.query_worker.start()
            print(self.extracted_csv)
        else:
            self.designer.choose_path(self.homepage)

    def query_finished(self) -> None:
        """ 
        query_finished:
            Removes query worker instance
        """
        print("Query finished")
        self.query_worker = None
        self.designer.single_query_warning_delete(self.homepage)
        self.designer.status_bar.setValue(100)

    def handle_result(self, result) -> None:
        """
        handle_result:
            Saves the resulting data from extraction to the extracted_csv attribute
        
        """
        print("Query Result:", result)
        self.extracted_csv = result

    def begin_query(self) -> None:
        """
        begin_query:
            Begins processing already extracted text through begining 
            a query through the CCLC class.
            Error handling: 
                If there is not extracted csv their is no function call
                If the user has a credential data is processed
                If the user has no credential the OCLC token is requested 
                    then data is processed if the token is recieved
        """
        self.designer.query_success_rate_delete(self.homepage, callback=self.display_query)

    def display_query(self) -> None:
        """
        display_query:
            Displays a warning for query in progress, and calls process_query
        
        """
        self.designer.query_in_process_warning(self.homepage, callback=self.process_query)

    def process_query(self):
        """
        process_query:
            Instnatiates a OCLC session and calls extract_query_data
        
        """
        # self.extracted_csv = "./extracted_data/extracted_data.csv"
        if not self.extracted_csv:
            print("ping user to process images first")
            self.designer.process_images_first_warning(self.homepage)

        else:
            self.OCLC = OCLCSession("config.ini")  # create OCLCSession Instance
            token_response = self.authenticate_user()  # Verify user login to the system
            if token_response == 200:
                self.credentail = True
                self.extract_query_data()
                self.query_in_process = True
            else:
                print("create error function ping user to relogin")
            # add a function call for

    def extract_query_data(self) -> None:
        """
        extract_query_data:
            Pulls processed SuDocs from extracted csv files and sends
            each unique instance to the query system. Failed queries are 
            documented according -> error processing is called as a side 
            effect
        """
        extracted_sudocs = pd.read_csv("./extracted_data/extracted_data.csv")
        print("before", len(extracted_sudocs))
        extracted_sudocs = extracted_sudocs[extracted_sudocs["SuDoc"].notna()]
        print("after", len(extracted_sudocs))
        count = 0
        for i in range(len(extracted_sudocs)):
            query_result = self.OCLC.query(extracted_sudocs.iloc[i]["SuDoc"])
            query_result = json.loads(query_result)
            print(query_result)
            if int(query_result["numberOfRecords"]) != 1:
                print("here")
                if pd.isna(extracted_sudocs.iloc[i]["Query Status"]):
                    extracted_sudocs.loc[i, "Query Status"] = 1
                else:
                    extracted_sudocs.loc[i, "Query Status"] += 1

                if int(query_result["numberOfRecords"]) > 1:
                    extracted_sudocs.loc[i, "Error Code"] = "multiple records"

                if int(query_result["numberOfRecords"]) == 0:
                    extracted_sudocs.loc[i, "Error Code"] = "no records"
            else:
                text = query_result['bibRecords'][0]['title']['mainTitles'][0]['text']
                year = query_result['bibRecords'][0]['date']['publicationDate']

                extracted_sudocs.at[i, "Title"] = text
                extracted_sudocs.loc[i, "Publication Year"] = year
                extracted_sudocs.loc[i, "Error Code"] = "Data Collected"
                count += 1
        total = len(extracted_sudocs)
        extracted_sudocs.reset_index(drop=True, inplace=True)
        extracted_sudocs.to_csv("extracted_data/extracted_data.csv", index=False)
        if count != total:
            self.verify_extracted_data()

    def verify_extracted_data(self) -> None:
        """
        verify_extracted_data:
            Verification process for query failures on the first instance 
            Implementation TBD
    
        """
        extracted_sudocs = pd.read_csv('./extracted_data/extracted_data.csv')
        pending_queries = pd.concat([extracted_sudocs[extracted_sudocs['Error Code'] == "no records"],
                                     extracted_sudocs[extracted_sudocs['Error Code'] == "multiple records"],
                                     ])
        self.exceptions = pending_queries

        self.verification_window = WindowDesigner(self)
        self.verification_window = self.designer.create_verification_window()
        print(self.exceptions)
        self.designer.update_verification_window(self.exceptions.iloc[0]['Sudoc Image'],
                                                 self.exceptions.iloc[0]['Title Image'],
                                                 self.exceptions.iloc[0]['SuDoc'], self.exceptions.iloc[0]['Title'],
                                                 self.exceptions.iloc[0]['Publication Year'])

        self.homepage.query_finished(self.homepage)
        self.homepage.preview(self.homepage)
        self.homepage.toggleClose(self.homepage)

    def next_instance(self):
        """ 
            next_instance:
                records user verified data from the verifier window and writes it
                to the csv
        
        """
        extracted_sudocs = pd.read_csv("./extracted_data/extracted_data.csv")
        print(self.exceptions)
        print(len(self.exceptions))
        identifier = self.exceptions.iloc[0]["ID"]
        print(identifier)

        sudoc = self.verification_window.sudoc_textbox.text()
        title = self.verification_window.title_textbox.text()
        year = self.verification_window.publication_year.text()

        extracted_sudocs.at[identifier, 'SuDoc'] = sudoc
        extracted_sudocs.at[identifier, 'Title'] = title
        extracted_sudocs.at[identifier, 'Publication Year'] = year

        extracted_sudocs.reset_index(drop=True, inplace=True)
        extracted_sudocs.to_csv("extracted_data/extracted_data.csv", index=False)

    def update_exceptions(self) -> None:
        """
        update_exceptions:
            Reads and writes updated user which user verifies/inputs
            Deletes instance from verification list, and updates[closes]
            the verification window for the next verification instance
        """
        if len(self.exceptions) > 1:
            self.next_instance()
            self.exceptions = self.exceptions.drop(self.exceptions.index[0])
            self.designer.update_verification_window(self.exceptions.iloc[0]['Sudoc Image'],
                                                     self.exceptions.iloc[0]['Title Image'],
                                                     self.exceptions.iloc[0]['SuDoc'], self.exceptions.iloc[0]['Title'],
                                                     self.exceptions.iloc[0]['Publication Year'])
        else:
            self.next_instance()
            self.exceptions = self.exceptions.drop(self.exceptions.index[0])
            self.verification_window.close()
            self.verification_window = None
            requeried_result = self.query_sudoc()
            self.merge_pending_queries(requeried_result)

    def query_sudoc(self) -> pd.DataFrame():
        """
             query_sudoc:
             Instantiates the query process on the pending_quires dataframe
        """
        extracted_sudocs = pd.read_csv("./extracted_data/extracted_data.csv")
        pending_queries = pd.concat([extracted_sudocs[extracted_sudocs['Error Code'] == "no records"],
                                     extracted_sudocs[extracted_sudocs['Error Code'] == "multiple records"]])
        for i in range(len(pending_queries)):
            query_result = self.OCLC.query(pending_queries.iloc[i]["SuDoc"])
            query_result = json.loads(query_result)
            # print(query_result)
            if int(query_result["numberOfRecords"]) != 1:
                if pd.isna(pending_queries.iloc[i]["Query Status"]):
                    pending_queries.loc[i, "Query Status"] = 1
                else:
                    pending_queries.loc[i, "Query Status"] += 1

            else:
                text = query_result['bibRecords'][0]['title']['mainTitles'][0]['text']
                year = query_result['bibRecords'][0]['date']['publicationDate']

                pending_queries.iloc[i]["Title"] = text
                pending_queries.iloc[i]["Publication Year"] = year
                pending_queries.iloc[i]["Error Code"] = "Data Collected"
        return pending_queries

    def merge_pending_queries(self, outliers) -> None:
        """
        merge_pending_queries:
            writes the finalized results from the verification process back
            into the main csv
         """
        extracted_sudocs = pd.read_csv("./extracted_data/extracted_data.csv")
        for i in outliers['ID']:
            extracted_sudocs.at[i, 'SuDoc'] = outliers.at[i, 'SuDoc']
            extracted_sudocs.at[i, 'Title'] = outliers.at[i, 'Title']
            extracted_sudocs.at[i, 'Publication Year'] = outliers.at[i, 'Publication Year']
        count = len(extracted_sudocs[extracted_sudocs["Error Code"] == "Data Collected"])
        total = len(extracted_sudocs)
        self.designer.query_in_process_warning_delete(self.homepage)
        self.designer.querySuccessRate(self.homepage, count, total)
        self.query_in_process = False

    def preview_csv(self) -> None:
        """
        preview_csv:
            displays a preview of the first 5[or less] instances of the
            pulled data on the homepage window
    
        """
        extracted_data = pd.read_csv("./extracted_data/extracted_data.csv")
        preview = extracted_data["Error Code"].head().to_string()
        self.homepage.preview_results(self.homepage, preview)

    def download_csv(self) -> None:
        """
        download_csv: 
            Saves the resulting data from the query into the users
            downloads folder
        """
        time = datetime.datetime.now()
        time = time.strftime('%Y-%m-%d %H-%M-%S')[:-3]
        extracted_data = pd.read_csv("./extracted_data/extracted_data.csv")
        extracted_data = extracted_data[["ID", "Title", "SuDoc", "Publication Year"]]
        extracted_data.to_csv("~/Downloads/resulting_data_" + time + ".csv", index=False)

    def new_query(self) -> None:
        """
        new_query: 
            Resets the interface. Will return the user to the login
            window and reinitialize all PMET APP flags and variables.
            Serves the purpose of restricting multiple queries in order
            to stay within the token time frame
         """

        # print("Function was called")
        # os.remove("./extracted_data/extracted_data.csv") UNCOMMENT IN FINAL VERSION!
        self.homepage.parent.close()
        self.homepage = None
        self.designer = WindowDesigner(self)
        print("Creating Login Window")

        self.designer.create_login_window()
        self.homepage = None
        self.directory_path = None
        self.style_flag = False
        self.query_worker = None
        self.extracted_csv = None
        self.credential = False
        self.credentials_saved = False
        self.OCLC = None
        # Reset entire system and all flag variables to reinstantiate the window


if __name__ == '__main__':
    app = QApplication([])  # Create the QApplication instance
    pmet_app = PMETApp()
    pmet_app.run()
    sys.exit(app.exec())  # Start the event loop with app.exec()
