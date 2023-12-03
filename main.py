from Interactive_Program_Interface import *

app = QApplication([])  # Create the QApplication instance
pmet_app = PMETApp()
pmet_app.run()
sys.exit(app.exec())  # Start the event loop with app.exec()
