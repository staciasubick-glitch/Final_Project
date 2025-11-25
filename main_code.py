#Interactive checkers game
#Software Carpentry Fall 2025 Final Project
#Created by Stacia Subick

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np

class SquareButton(QPushButton):
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window().start_drag(self.row, self.col, self)
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData().text()
        old_row, old_col = map(int, data.split(","))
        self.window().finish_drag(old_row, old_col, self.row, self.col)
        event.acceptProposedAction()



class Checkers(QMainWindow):
    def __init__(self):
        super(Checkers, self).__init__()
        self.setWindowTitle("Checkers")
        self.setGeometry(300, 300, 600, 600)

        # central widget + layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QGridLayout(self.central_widget)
        self.grid_layout.setSpacing(0)

        # initialize buttons and drag state
        self.buttons = []
        self.dragging_piece = None
        self.drag_start = None

        # create game board array
        self.board = self.setup_board()

        # make visual board
        self.setup_gui()


    def setup_board(self):
        """Creates an 8×8 array holding 'r', 'b', or None."""
        board = [[None for _ in range(8)] for _ in range(8)]

        for row in range(8):
            for col in range(8):
                is_dark = (row + col) % 2 == 1
                if row in (0, 1, 2) and is_dark:
                    board[row][col] = "b"
                if row in (5, 6, 7) and is_dark:
                    board[row][col] = "r"

        return board

    def setup_gui(self):
        """Creates 8×8 buttons that act as checkerboard squares."""
        for row in range(8):
            row_buttons = []
            for col in range(8):
                # IMPORTANT: parent should be the central widget (not the QMainWindow)
                button = SquareButton(row, col, parent=self.central_widget)
                button.setFixedSize(70, 70)

                # set square color
                if (row + col) % 2 == 0:
                    button.setStyleSheet("background-color: tan;")
                else:
                    button.setStyleSheet("background-color: saddlebrown;")

                # DO NOT connect clicked() while debugging mouse handlers
                # button.clicked.connect(lambda checked, r=row, c=col: self.on_square_clicked(r, c))

                self.grid_layout.addWidget(button, row, col)
                row_buttons.append(button)

            self.buttons.append(row_buttons)

        self.update_board()

    def update_board(self):
        """Place icons on the board according to self.board."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                button = self.buttons[row][col]

                if piece is None:
                    button.setIcon(QIcon())
                else:
                    icon = self.create_piece_icon("red" if piece == "r" else "black")
                    button.setIcon(QIcon(icon))
                    button.setIconSize(QSize(60, 60))

    def create_piece_icon(self, color, size=60):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        brush_color = QColor(200, 30, 30) if color == "red" else QColor(30, 30, 30)
        painter.setBrush(brush_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()

        return pixmap

    def on_square_clicked(self, row, col):
        print(f"Clicked square ({row}, {col})")

    # DEBUG prints to confirm functions are called
    def start_drag(self, row, col, button):
        piece = self.board[row][col]
        if piece is None:
            return

        drag = QDrag(button)
        mime = QMimeData()

        # encode starting location
        mime.setText(f"{row},{col}")
        drag.setMimeData(mime)

        # show the checker piece while dragging
        icon = button.icon()
        pixmap = icon.pixmap(60, 60)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(30, 30))

        drag.exec_(Qt.MoveAction)

    def finish_drag(self, old_row, old_col, new_row, new_col):
        piece = self.board[old_row][old_col]
        if piece is None:
            return

        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = piece
        self.update_board()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    checkers = Checkers()
    checkers.show()
    sys.exit(app.exec_())
