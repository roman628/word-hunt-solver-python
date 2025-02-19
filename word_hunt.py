import sys
from collections import defaultdict
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QGridLayout
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPoint

class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.is_word = False

def make_trie(words):
    root = TrieNode()
    for word in words:
        node = root
        for char in word:
            node = node.children[char]
        node.is_word = True
    return root

def find_words(board, trie):
    def dfs(i, j, node, word, path):
        if node.is_word and len(word) > 2:
            results.add((word, tuple(path)))
        
        if i < 0 or i >= 4 or j < 0 or j >= 4 or (i, j) in path:
            return
        
        char = board[i][j]
        if char not in node.children:
            return
        
        new_path = path + [(i, j)]
        new_node = node.children[char]
        
        directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        
        for di, dj in directions:
            dfs(i+di, j+dj, new_node, word+char, new_path)

    results = set()
    for i in range(4):
        for j in range(4):
            dfs(i, j, trie, "", [])
    
    return sorted(results, key=lambda x: (-len(x[0]), x[0]))

class WordHuntSolver(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Word Hunt Solver')
        self.setGeometry(100, 100, 400, 500)
        
        layout = QVBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter 16 letters")
        layout.addWidget(self.input_field)
        
        self.solve_button = QPushButton('Solve')
        self.solve_button.clicked.connect(self.solve)
        layout.addWidget(self.solve_button)
        
        self.word_label = QLabel()
        layout.addWidget(self.word_label)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        layout.addWidget(self.grid_widget)
        
        self.next_button = QPushButton('Next Word')
        self.next_button.clicked.connect(self.next_word)
        layout.addWidget(self.next_button)
        
        self.setLayout(layout)
        
        self.words = []
        self.current_word_index = 0
        
    def solve(self):
        board_string = self.input_field.text().lower()
        if len(board_string) != 16:
            self.word_label.setText("Please enter exactly 16 letters.")
            return
        
        self.board = [list(board_string[i:i+4]) for i in range(0, 16, 4)]
        
        with open('words.txt', 'r') as f:
            words = [word.strip().lower() for word in f if len(word.strip()) > 2]
        
        trie = make_trie(words)
        
        start_time = time.time()
        self.words = find_words(self.board, trie)
        end_time = time.time()
        
        self.word_label.setText(f"Found {len(self.words)} words in {end_time - start_time:.4f} seconds.")
        
        self.current_word_index = 0
        self.display_word()
        
    def display_word(self):
        if self.current_word_index < len(self.words):
            word, path = self.words[self.current_word_index]
            self.word_label.setText(f"Word: {word.upper()} ({self.current_word_index + 1}/{len(self.words)})")
            
            for i in reversed(range(self.grid_layout.count())): 
                self.grid_layout.itemAt(i).widget().setParent(None)
            
            for i in range(4):
                for j in range(4):
                    label = QLabel(self.board[i][j].upper())
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("border: 1px solid black; font-size: 20px;")
                    self.grid_layout.addWidget(label, i, j)
            
            self.path = path
            self.update()
        else:
            self.word_label.setText("No more words.")
    
    def next_word(self):
        self.current_word_index += 1
        self.display_word()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if hasattr(self, 'path'):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen(Qt.red, 3)
            painter.setPen(pen)
            
            grid_pos = self.grid_widget.pos()
            cell_width = self.grid_widget.width() // 4
            cell_height = self.grid_widget.height() // 4
            
            for i in range(len(self.path) - 1):
                start = QPoint(grid_pos.x() + self.path[i][1] * cell_width + cell_width // 2,
                               grid_pos.y() + self.path[i][0] * cell_height + cell_height // 2)
                end = QPoint(grid_pos.x() + self.path[i+1][1] * cell_width + cell_width // 2,
                             grid_pos.y() + self.path[i+1][0] * cell_height + cell_height // 2)
                painter.drawLine(start, end)
            
            # Mark start and end
            painter.setBrush(Qt.green)
            start = QPoint(grid_pos.x() + self.path[0][1] * cell_width + cell_width // 2,
                           grid_pos.y() + self.path[0][0] * cell_height + cell_height // 2)
            painter.drawEllipse(start, 5, 5)
            
            painter.setBrush(Qt.blue)
            end = QPoint(grid_pos.x() + self.path[-1][1] * cell_width + cell_width // 2,
                         grid_pos.y() + self.path[-1][0] * cell_height + cell_height // 2)
            painter.drawEllipse(end, 5, 5)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WordHuntSolver()
    ex.show()
    sys.exit(app.exec_())