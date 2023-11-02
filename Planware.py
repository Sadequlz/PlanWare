# Import the required modules
import sqlite3  # For SQLite database operations
from PyQt5.QtWidgets import QWidget, QApplication, QListWidgetItem, QMessageBox  # PyQt5 GUI elements
from PyQt5.uic import loadUi  # Loading the UI from a file
import sys  # System-related functions
from PyQt5 import QtCore  # PyQt5 core functionalities
# Create a GUI window class that inherits from QWidget
class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        # Load the user interface from the "main.ui" file
        loadUi("main.ui", self)

        # Connect GUI elements to their respective functions
        self.calendarWidget.selectionChanged.connect(self.calendarDateChanged)
        self.calendarDateChanged()  # Call the function to initialize the calendar
        self.saveButton.clicked.connect(self.saveChanges)
        self.addButton.clicked.connect(self.addNewTask)

    def calendarDateChanged(self):
        # Function called when the calendar date changes
        print("The calendar date was changed.")
        dateSelected = self.calendarWidget.selectedDate().toPyDate()
        print("Date selected:", dateSelected)
        self.updateTaskList(dateSelected)  # Update the task list based on the selected date

    def updateTaskList(self, date):
        # Function to update the list of tasks displayed
        self.tasksListWidget.clear()  # Clear the existing task list

        # Connect to the SQLite database
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        # Query to retrieve tasks for a specific date
        query = "SELECT task, completed FROM tasks WHERE date = ?"
        row = (str(date),)  # Convert date to string for comparison
        results = cursor.execute(query, row).fetchall()

        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)

            # Set the check state based on whether the task is completed or not
            if result[1] == "YES":
                item.setCheckState(QtCore.Qt.Checked)
            elif result[1] == "NO":
                item.setCheckState(QtCore.Qt.Unchecked)

            # Add the task item to the list widget
            self.tasksListWidget.addItem(item)

    def saveChanges(self):
        # Function to save changes made to task completion status
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        date = self.calendarWidget.selectedDate().toPyDate()

        for i in range(self.tasksListWidget.count()):
            item = self.tasksListWidget.item(i)
            task = item.text()

            # Determine whether the task is marked as completed or not
            if item.checkState() == QtCore.Qt.Checked:
                query = "UPDATE tasks SET completed = 'YES' WHERE task = ? AND date = ?"
            else:
                query = "UPDATE tasks SET completed = 'NO' WHERE task = ? AND date = ?"
            row = (task, str(date),)  # Convert date to string for comparison
            cursor.execute(query, row)

        db.commit()  # Commit the changes to the database

        # Display a message box to confirm that changes have been saved
        messageBox = QMessageBox()
        messageBox.setText("Changes saved.")
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()

    def addNewTask(self):
        # Function to add a new task to the database
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        newTask = str(self.taskLineEdit.text())
        date = self.calendarWidget.selectedDate().toPyDate()

        # Insert a new task with default completion status ("NO") into the database
        query = "INSERT INTO tasks(task, completed, date) VALUES (?,?,?)"
        row = (newTask, "NO", str(date))  # Convert date to string for storage

        cursor.execute(query, row)
        db.commit()  # Commit the changes to the database

        self.updateTaskList(date)  # Update the task list to reflect the newly added task
        self.taskLineEdit.clear()  # Clear the task input field

# Run the application if this script is the main entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())