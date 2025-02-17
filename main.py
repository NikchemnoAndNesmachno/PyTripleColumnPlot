import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QWidget, \
    QLabel, QComboBox, QLineEdit, QSplitter, QSizePolicy
from PyQt5.QtCore import Qt
import matplotlib.style as mplstyle
mplstyle.use('fast')

class DataVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("3D Data Plotter")
        self.setGeometry(100, 100, 1000, 700)
        main_layout = QHBoxLayout()
        control_layout = QVBoxLayout()

        self.label = QLabel("Load and plot 3D data")
        control_layout.addWidget(self.label)

        self.file_path_edit = QLineEdit(self)
        self.file_path_edit.setPlaceholderText("Select or enter file path")
        self.select_file_button = QPushButton("Select File")
        self.select_file_button.clicked.connect(self.on_select_file)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.select_file_button)
        control_layout.addLayout(file_layout)

        self.load_button = QPushButton("Load Data")
        self.load_button.clicked.connect(self.on_load_data)
        control_layout.addWidget(self.load_button)

        self.combo_x = QComboBox()
        self.combo_y = QComboBox()
        self.combo_z = QComboBox()
        self.combo_plot_type = QComboBox()
        self.combo_plot_type.addItems(["Scatter", "Wireframe", "Surface"])

        control_layout.addWidget(QLabel("Select X-axis:"))
        control_layout.addWidget(self.combo_x)
        control_layout.addWidget(QLabel("Select Y-axis:"))
        control_layout.addWidget(self.combo_y)
        control_layout.addWidget(QLabel("Select Z-axis:"))
        control_layout.addWidget(self.combo_z)
        control_layout.addWidget(QLabel("Select Plot Type:"))
        control_layout.addWidget(self.combo_plot_type)

        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.on_plot)
        control_layout.addWidget(self.plot_button)

        self.save_button = QPushButton("Save to File")
        self.save_button.clicked.connect(self.on_save_to_file)
        control_layout.addWidget(self.save_button)

        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.on_copy_to_clipboard)
        control_layout.addWidget(self.copy_button)

        splitter = QSplitter(Qt.Horizontal)
        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        splitter.addWidget(control_widget)

        self.canvas_frame = QWidget()
        splitter.addWidget(self.canvas_frame)

        main_layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        plt.margins(x=1,y=1)
        plt.rcParams['axes.xmargin'] = 0
        plt.gca().spines[['right', 'top']].set_visible(False)
        self.fig = plt.figure()
        self.data = None
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout(self.canvas_frame)
        layout.addWidget(self.canvas)
        self.canvas_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.updateGeometry()

    def on_select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Data File", "",
                                                   "CSV Files (*.csv);;DAT Files (*.dat);;Excel Files (*.xlsx)",
                                                   options=options)

        if file_path:
            self.file_path_edit.setText(file_path)

    def load_file(self):
        file_path = self.file_path_edit.text()

        if not file_path:
            self.show_error("Please specify a file path.")
            return None

        if file_path.endswith(".dat"):
            return pd.read_csv(file_path, delim_whitespace=True)
        elif file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            return pd.read_excel(file_path)
        else:
            self.show_error("Unsupported file type")
            return None

    def plot_3d(self, data, col_x, col_y, col_z, plot_type):
        try:
            self.fig.clear()
            ax = self.fig.add_subplot(111, projection='3d')
            ax.margins(x=0,y=0)
            x = data[col_x]
            y = data[col_y]
            z = data[col_z]

            if plot_type == "Scatter":
                ax.scatter(x, y, z, c='b', marker='o')
            elif plot_type == "Wireframe":
                X, Y = np.meshgrid(np.linspace(x.min(), x.max(), 30), np.linspace(y.min(), y.max(), 30))
                Z = np.interp(X, x, z)  # Interpolate Z values for the grid
                ax.plot_wireframe(X, Y, Z, color='b')
            elif plot_type == "Surface":
                X, Y = np.meshgrid(np.linspace(x.min(), x.max(), 30), np.linspace(y.min(), y.max(), 30))
                Z = np.interp(X, x, z)
                ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')

            ax.set_xlabel(col_x)
            ax.set_ylabel(col_y)
            ax.set_zlabel(col_z)
            self.canvas.draw()
        except Exception as e:
            self.show_error(f"Failed to plot data: {e}")

    def show_error(self, message):
        error_dialog = QWidget(self)
        error_layout = QVBoxLayout(error_dialog)
        error_layout.addWidget(QLabel(message))
        button = QPushButton("OK", error_dialog)
        button.clicked.connect(error_dialog.close)
        error_layout.addWidget(button)
        error_dialog.setWindowTitle("Error")
        error_dialog.setLayout(error_layout)
        error_dialog.show()

    def on_load_data(self):
        data = self.load_file()
        if data is not None:
            if len(data.columns) < 3:
                self.show_error("Dataset must have at least 3 columns.")
                return

            column_names = list(data.columns)
            self.combo_x.addItems(column_names)
            self.combo_y.addItems(column_names)
            self.combo_z.addItems(column_names)

            self.data = data

    def on_plot(self):
        if self.data is None:
            self.show_error("Please load data first.")
            return

        col_x = self.combo_x.currentText()
        col_y = self.combo_y.currentText()
        col_z = self.combo_z.currentText()
        plot_type = self.combo_plot_type.currentText()

        if col_x and col_y and col_z and plot_type:
            self.plot_3d(self.data, col_x, col_y, col_z, plot_type)
        else:
            self.show_error("Please select all required options.")

    def on_save_to_file(self):
        if self.fig is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)")
            if file_path:
                self.fig.savefig(file_path)
                self.show_error(f"Saved to {file_path}")

    def on_copy_to_clipboard(self):
        if self.fig is not None:
            QApplication.clipboard().setPixmap(self.canvas_frame.grab())
            self.show_error("Image copied to clipboard.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataVisualizer()
    window.show()
    sys.exit(app.exec())
