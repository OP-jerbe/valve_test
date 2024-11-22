import sys
from PySide6.QtCore import QEvent, Qt, QObject, QThread, QRegularExpression
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QLabel, QLineEdit, QMessageBox, 
    QHBoxLayout, QVBoxLayout, QFrame, QGridLayout
    )
from PySide6.QtGui import QIcon, QMouseEvent, QRegularExpressionValidator, QAction, QFont
from qt_material import apply_stylesheet

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.installEventFilter(self)
        self.create_gui()

    def create_gui(self) -> None:
        input_box_width = 130
        input_box_height = 28
        go_to_input_box_width = 100
        go_to_input_box_height = 28
        button_width = 100
        button_height = 40
        window_width = 470
        window_height = 275

        self.setFixedSize(window_width,window_height)
        self.setWindowTitle('Automated Valve Test')
        if hasattr(sys, 'frozen'):  # Check if running from the bundled app
            icon_path = sys._MEIPASS + '/scan.ico'  # type: ignore
        else:
            icon_path = 'icon/valve_icon.ico'  # Use the local icon file in dev mode
        self.setWindowIcon(QIcon(icon_path))
        apply_stylesheet(self, theme='dark_lightgreen.xml', invert_secondary=True)
        self.setStyleSheet(self.styleSheet() + """QLineEdit, QTextEdit {color: lightgreen;}""")

        # Create Left Side of Main Window Elements
        self.left_title_label = QLabel('Valve Test')
        self.left_title_label.setStyleSheet('font-size: 25px; font-weight: bold; font-family: Arial;')
        self.serial_number_label = QLabel('Serial Number')
        self.serial_number_input = QLineEdit()
        self.serial_number_input.setFixedSize(input_box_width, input_box_height)
        self.rework_letter_label = QLabel('Rework Letter')
        self.rework_letter_input = QLineEdit()
        self.rework_letter_input.setFixedSize(input_box_width, input_box_height)
        self.base_pressure_label = QLabel('Base Pressure')
        self.base_pressure_input = QLineEdit()
        self.base_pressure_input.setFixedSize(input_box_width, input_box_height)
        self.start_test_button = QPushButton('Start Test')
        self.start_test_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_test_button.setDisabled(True)

        # Create Right Side of Main Window Elements
        self.right_title_label = QLabel('Motor Control')
        self.right_title_label.setStyleSheet('font-size: 25px; font-weight: bold; font-family: Arial;')
        self.open_button = QPushButton('Open')
        self.open_button.setFixedSize(button_width, button_height)
        self.open_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button = QPushButton('Close')
        self.close_button.setFixedSize(button_width, button_height)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.home_button = QPushButton('Home')
        self.home_button.setFixedSize(button_width, button_height)
        self.home_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_zero_button = QPushButton('Set Zero')
        self.set_zero_button.setFixedSize(button_width, button_height)
        self.set_zero_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.actual_position_label = QLabel('Position:')
        self.actual_position_reading = QLabel()

        self.go_to_position_input = QLineEdit()
        self.go_to_position_input.setFixedSize(go_to_input_box_width, go_to_input_box_height)
        self.go_to_position_input.setPlaceholderText('Set Postion')
        self.go_to_position_button = QPushButton('Go To Position')
        self.go_to_position_button.setFixedSize(200, button_height)
        self.go_to_position_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Arrange left side widgets in window
        g_left_title_layout = QGridLayout()
        g_left_title_layout.addWidget(self.left_title_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        v_left_labels_layout = QVBoxLayout()
        v_left_labels_layout.addWidget(self.serial_number_label)
        v_left_labels_layout.addWidget(self.rework_letter_label)
        v_left_labels_layout.addWidget(self.base_pressure_label)
        v_left_inputs_layout = QVBoxLayout()
        v_left_inputs_layout.addWidget(self.serial_number_input)
        v_left_inputs_layout.addWidget(self.rework_letter_input)
        v_left_inputs_layout.addWidget(self.base_pressure_input)
        h_left_labels_and_inputs_layout = QHBoxLayout()
        h_left_labels_and_inputs_layout.addLayout(v_left_labels_layout)
        h_left_labels_and_inputs_layout.addLayout(v_left_inputs_layout)

        g_start_button_layout = QGridLayout()
        g_start_button_layout.addWidget(self.start_test_button, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        g_left_sub_main_layout = QGridLayout()
        g_left_sub_main_layout.addLayout(g_left_title_layout, 0, 0)
        g_left_sub_main_layout.addLayout(h_left_labels_and_inputs_layout, 1, 0)
        g_left_sub_main_layout.addLayout(g_start_button_layout, 2, 0)

        # Create a vertical line
        vertical_line = QFrame()
        vertical_line.setFrameShape(QFrame.Shape.VLine)

        # Arrange right side widgets in window
        g_right_title_layout = QGridLayout()
        g_right_title_layout.addWidget(self.right_title_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        g_right_title_layout.setContentsMargins(0, 0, 0, 35)

        g_right_buttons_layout = QGridLayout()
        g_right_buttons_layout.addWidget(self.open_button, 0, 0, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        g_right_buttons_layout.addWidget(self.close_button, 0, 1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        g_right_buttons_layout.addWidget(self.home_button, 1, 0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        g_right_buttons_layout.addWidget(self.set_zero_button, 1, 1, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        h_right_position_layout = QHBoxLayout()
        h_right_position_layout.addWidget(self.actual_position_label, alignment=Qt.AlignmentFlag.AlignRight)
        h_right_position_layout.addWidget(self.actual_position_reading, alignment=Qt.AlignmentFlag.AlignLeft)
        v_right_goto_layout = QVBoxLayout()
        v_right_goto_layout.addWidget(self.go_to_position_input, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        v_right_goto_layout.addWidget(self.go_to_position_button, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        v_right_pos_and_goto_layout = QVBoxLayout()
        v_right_pos_and_goto_layout.addLayout(h_right_position_layout)
        v_right_pos_and_goto_layout.addLayout(v_right_goto_layout)

        g_right_sub_main_layout = QGridLayout()
        g_right_sub_main_layout.addLayout(g_right_title_layout, 0, 0)
        g_right_sub_main_layout.addLayout(g_right_buttons_layout, 1, 0)
        g_right_sub_main_layout.addLayout(v_right_pos_and_goto_layout, 2, 0)

        h_main_layout = QHBoxLayout()
        h_main_layout.addLayout(g_left_sub_main_layout)
        h_main_layout.addWidget(vertical_line)
        h_main_layout.addLayout(g_right_sub_main_layout)

        container = QWidget()
        container.setLayout(h_main_layout)

        self.setCentralWidget(container)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if isinstance(event, QMouseEvent) and event.type() == QEvent.Type.MouseButtonPress:
            focused_widget = QApplication.focusWidget()
            if focused_widget is not None:
                focused_widget.clearFocus()
        return super().eventFilter(watched, event)
    
    # def closeEvent(self, event) -> None:
    #     # Confirm the user wants to exit the application.
    #     reply = QMessageBox.question(self, 'Confirmation',
    #                                  'Are you sure you want to close the window?',
    #                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    #     if reply == QMessageBox.StandardButton.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()



if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())