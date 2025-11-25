#Interactive checkers game
#Software Carpentry Fall 2025 Final Project
#Created by Stacia Subick

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
from rich import layout


#create a class to contain the board
class Checkers(QMainWindow):
    def __init__(self):
        super(Checkers, self).__init__()
        self.setWindowTitle("Checkers")
        self.setGeometry(300, 300, 400, 400)

        #create board widget and set to have no spacing between each spot on the grid
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QGridLayout(self.central_widget)
        self.grid_layout.setSpacing(0)

        self.generate_board()
        self.setup_board()

    def generate_board(self):
        #set size of each square on grid
        size = 50
        #initialize board
        board = np.zeros((8, 8), dtype=int)

        #assign colors  on the grid to tan and brown
        for i in range(8):
            for j in range(8):
                square = QLabel()
                square.setFixedSize(size, size)

                if (i+j)%2==0:
                    square.setStyleSheet("background-color:tan")
                else:
                    square.setStyleSheet("background-color:saddle brown")

                self.grid_layout.addWidget(square, i, j)

    def setup_board(self):
        #create list to hold locations of checkers pieces
        board=[[None for i in range(8)] for j in range(8)]

        # place checkers in initial location
        for i in range(8): #columns
            for j in range(8): #rows
                if j==0 or 1 or 2:
                    if i%2==0: #assign black pieces to first 3 rows
                        None
                    else:
                        board[i][j]='b'
                if j==6 or 7 or 8: #assign red pieces to last 3 rows
                    if i%2==0:
                        None
                    else:
                        board[i][j]='r'

        return board

    def setup_gui(self):
        # Creating buttons for each square on the board
        for row in range(8):
            row_buttons = []
            for col in range(8):
                button = QPushButton()
                button.setFixedSize(100, 100)
                button.clicked.connect(lambda checked, r=row, c=col: self.on_square_clicked(r, c))
                layout.addWidget(button, row, col)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

        self.update_board()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    checkers = Checkers()
    checkers.show()
    sys.exit(app.exec_())