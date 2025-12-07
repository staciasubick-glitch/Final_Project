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
    '''
    main class defining the GUI window and the functions that define how pieces move
    '''
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

        # call function to set up board visual
        self.setup_gui()


    def setup_board(self):
        """Creates an 8×8 array holding 'r' or 'b' that creates the colors of the checkers."""
        #initialize empty list of board spaces
        board = [[None for _ in range(8)] for _ in range(8)]

        #assign colors to pieces
        for row in range(8):
            for col in range(8):
                is_dark = (row + col) % 2 == 1
                if row in (0, 1, 2) and is_dark:
                    board[row][col] = "b"
                if row in (5, 6, 7) and is_dark:
                    board[row][col] = "r"

        return board

    def setup_gui(self):
        """Creates buttons that act as checkerboard squares."""
        for row in range(8):
            row_buttons = []
            for col in range(8):
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
        """Place icons on the board according to the array defined in by self.board."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                button = self.buttons[row][col]

                if piece is None:
                    button.setIcon(QIcon())
                else:
                    icon = self.create_piece_icon(piece)
                    button.setIcon(QIcon(icon))
                    button.setIconSize(QSize(60, 60))

    def create_piece_icon(self, piece, size=60):
        ''' create circular icon to represent checkers piece'''
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        color = piece.lower()
        brush_color = QColor(200, 30, 30) if color == "r" else QColor(30, 30, 30)
        painter.setBrush(brush_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)

        #draw a crown if piece is a king
        if piece.isupper():
            yellow=QColor(255, 215, 0)
            painter.setPen(QPen(yellow))
            painter.setBrush(QBrush(yellow))

            crown = QPolygon([
                QPoint(int(size * 0.25), int(size * 0.55)),  # left base
                QPoint(int(size * 0.25), int(size * 0.20)),  # left spike

                QPoint(int(size * 0.50), int(size * 0.20)),  # middle spike (tallest)

                QPoint(int(size * 0.75), int(size * 0.20)),  # right spike
                QPoint(int(size * 0.75), int(size * 0.55)),  # right base
            ])
            painter.drawPolygon(crown)
        painter.end()

        return pixmap

    def on_square_clicked(self, row, col):
        '''function prints the coordinates of square that was clicked'''
        print(f"Clicked square ({row}, {col})")

    # DEBUG prints to confirm functions are called
    def start_drag(self, row, col, button):
        '''define button behavior when piece is clicked and dragged'''
        self.reset_highlights()

        piece = self.board[row][col]
        if piece is None:
            return

        #add highlights for valid moves
        moves = self.find_valid_moves(row, col)
        self.create_highlights(moves)

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
        '''define button behavior when piece is released'''
        #clear highlights after move finishes
        self.reset_highlights()

        if not self.is_valid_move(old_row, old_col, new_row, new_col):
            print("Invalid move!")
            return

        piece = self.board[old_row][old_col]

        # Check if captured:
        if abs(new_row - old_row) == 2:
            mid_row = (old_row + new_row) // 2
            mid_col = (old_col + new_col) // 2
            self.board[mid_row][mid_col] = None  # remove captured piece

        # Move piece
        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = piece

        # if red reaches top row it becomes a king
        if piece == "r" and new_row == 0:
            self.board[new_row][new_col] = "R"

        # if black reaches bottom row it becomes a king
        if piece == "b" and new_row == 7:
            self.board[new_row][new_col] = "B"

        self.update_board()

    def find_valid_moves(self, row, col):
        moves = []
        piece =self.board[row][col]
        if piece is None:
            return moves

        #assign movement direction
        if piece == 'r':
            directions = [(-1, -1), (-1, 1)]
        elif piece == 'b':
            directions = [(1, -1), (1, 1)]
        else: #kings can move up and down
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        #test single step moves
        for dr, dc in directions:
            #assign coords of potential moves
            nr = row +dr
            nc= col +dc
            #check if move is on the board and an empty spot
            if 0 <= nr < 8 and 0<= nc< 8:
                if self.board[nr][nc] is None:
                    moves.append((nr,nc))

        #test capturing moves
        for dr, dc in directions:
            nr = row +2*dr
            nc= col+2*dc
            #find middle square
            mr = row +dr
            mc= col +dc
            if 0 <= nr < 8 and 0<= nc < 8:
                middle_checker = self.board[mr][mc]
                #check is middle piece exists and if its the same color as jumping piece
                if (middle_checker is not None and middle_checker.lower() != piece.lower()
                    and self.board[nr][nc] is None):
                    moves.append((nr,nc))

        return moves
    def create_highlights(self, moves):
        for (r, c) in moves:
            self.buttons[r][c].setStyleSheet("background-color: yellow;")


    def reset_highlights(self):
        for row in range(8):
            for col in range(8):
                button = self.buttons[row][col]
                if (row +col)%2 == 0:
                    button.setStyleSheet("background-color: tan;")
                else:
                    button.setStyleSheet("background-color: saddlebrown;")


    def is_valid_move(self, old_row, old_col, new_row, new_col):
        piece = self.board[old_row][old_col]
        if piece is None:
            return False

        # cannot move onto an occupied square
        if self.board[new_row][new_col] is not None:
            return False

        # decide allowed movement directions
        if piece == "r":  # red man
            allowed_rows = (-1,)
        elif piece == "b":  # black man
            allowed_rows = (1,)
        else:  # "R" or "B" = king
            allowed_rows = (-1, 1) #kings can move forward and backwards

        row_diff = new_row - old_row
        col_diff = new_col - old_col

        # single move forward
        if row_diff in allowed_rows and abs(col_diff) == 1:
            return True

        # two rows forward (capture move)
        if row_diff in tuple(d*2 for d in allowed_rows) and abs(col_diff) == 2:
            mid_row = (old_row + new_row) // 2
            mid_col = (old_col + new_col) // 2
            middle_piece = self.board[mid_row][mid_col]

            # Can capture only the opposite color
            if middle_piece is not None and middle_piece.lower() != piece.lower():
                return True

        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    checkers = Checkers()
    checkers.show()
    sys.exit(app.exec_())
