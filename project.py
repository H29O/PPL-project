import sys
import time
import pandas as pd
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QMessageBox, QShortcut, QTableView, QSplashScreen
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QAbstractTableModel, QModelIndex

class PandasModel(QAbstractTableModel):
    """A model to interface between a pandas DataFrame and QTableView."""

    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            elif orientation == Qt.Vertical:
                return str(section + 1)
        return None


class PlayerSearchApp(QMainWindow):
    def __init__(self, csv_file_path):
        super().__init__()
        self.setWindowTitle("Player Search - IPL Auction")
        self.setGeometry(100, 100, 500, 400)

        # Load player data
        self.player_data = pd.read_csv(csv_file_path)  # Load the CSV file into a DataFrame
        for col in self.player_data.select_dtypes(include=['object']):  # Strip whitespace in string columns
            self.player_data[col] = self.player_data[col].str.strip()
        if "Year" in self.player_data.columns:
            self.player_data["Year"] = pd.to_numeric(self.player_data["Year"], errors="coerce").fillna(0).astype(int)

        # Main UI
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Add heading label
        self.header_label = QLabel("Search IPL Players by Name")
        self.header_label.setStyleSheet("""
            font-size: 24px; font-weight: bold; color: white; background-color: #4CAF50;
            padding: 10px; border-radius: 5px; text-align: center;
        """)
        self.layout.addWidget(self.header_label)

        self.input_name = QLineEdit()
        self.layout.addWidget(self.input_name)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_player)
        self.layout.addWidget(self.search_button)

        enter_return = QShortcut(QKeySequence(Qt.Key_Return), self)
        enter_return.activated.connect(self.search_button.click)
        enter = QShortcut(QKeySequence(Qt.Key_Enter), self)
        enter.activated.connect(self.search_button.click)

        # Table for results
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setStretchLastSection(True)  # Stretch the last column to fit
        self.layout.addWidget(self.table_view)

        self.central_widget.setLayout(self.layout)

    def search_player(self):
        """Search and display player data."""
        player_name = self.input_name.text().strip()

        if not player_name:
            QMessageBox.warning(self, "Input Error", "Please enter a player name.")
            return

        # Filter data for the matching player name
        matching_players = self.player_data[self.player_data["Player Name"].str.lower() == player_name.lower()]

        if matching_players.empty:
            QMessageBox.information(self, "No Results", f"No data found for player: {player_name}")
            self.table_view.setModel(None)
        else:
            # Update table view with results
            model = PandasModel(matching_players)
            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()


def show_splash_screen(app):
    """Display a splash screen with a custom image while the application initializes."""
    # Load custom image for the splash screen
    splash_pix = QPixmap("C:\\Users\\heeto\\Desktop\\ppl assignments\\splash_image.jpg")
    splash_pix = splash_pix.scaled(500, 300, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    # Create the splash screen with the loaded image
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.showMessage(
        "IPL Auction Player Search\nLoading Data...",
        Qt.AlignCenter | Qt.AlignBottom,
        Qt.white,
    )
    splash.show()
    QTimer.singleShot(2000, splash.close)  # Close splash screen after 2 seconds
    return splash



if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Path to your CSV file
    csv_file_location = "C:\\Users\\heeto\\Desktop\\ppl assignments\\IPLPlayerAuctionData.csv"

    # Show splash screen
    splash = show_splash_screen(app)

    # Start the app
    main_window = PlayerSearchApp(csv_file_location)
    QTimer.singleShot(2000, main_window.show)  # Show the main window after splash

    sys.exit(app.exec_())
