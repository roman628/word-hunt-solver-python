import sys
from collections import defaultdict
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QGridLayout, QTabWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPoint

class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.is_word = False
        self.frequency_rank = float('inf')

def make_trie(words):
    root = TrieNode()
    for rank, word in enumerate(words):
        node = root
        for char in word:
            node = node.children[char]
        node.is_word = True
        node.frequency_rank = rank
    return root

def find_words(board, trie):
    def dfs(i, j, node, word, path):
        if node.is_word and len(word) > 2:
            results.append((word, tuple(path), node.frequency_rank))
        
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

    results = []
    for i in range(4):
        for j in range(4):
            dfs(i, j, trie, "", [])
    
    return results

class WordGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.path = None

    def update_grid(self, board):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
        
        for i in range(4):
            for j in range(4):
                label = QLabel(board[i][j].upper())
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("border: 1px solid black; font-size: 20px;")
                self.layout.addWidget(label, i, j)

    def set_path(self, path):
        self.path = path
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.path:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen(Qt.red, 3)
            painter.setPen(pen)
            
            cell_width = self.width() // 4
            cell_height = self.height() // 4
            
            for i in range(len(self.path) - 1):
                start = QPoint(self.path[i][1] * cell_width + cell_width // 2,
                               self.path[i][0] * cell_height + cell_height // 2)
                end = QPoint(self.path[i+1][1] * cell_width + cell_width // 2,
                             self.path[i+1][0] * cell_height + cell_height // 2)
                painter.drawLine(start, end)
            
            # Mark start and end
            painter.setBrush(Qt.green)
            start = QPoint(self.path[0][1] * cell_width + cell_width // 2,
                           self.path[0][0] * cell_height + cell_height // 2)
            painter.drawEllipse(start, 5, 5)
            
            painter.setBrush(Qt.blue)
            end = QPoint(self.path[-1][1] * cell_width + cell_width // 2,
                         self.path[-1][0] * cell_height + cell_height // 2)
            painter.drawEllipse(end, 5, 5)

class WordHuntSolver(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_words()
        self.load_frequent_words()
        
    def load_words(self):
        with open('words.txt', 'r') as f:
            self.words = set(word.strip().lower() for word in f if len(word.strip()) > 2)
        
    def load_frequent_words(self):
        self.word_ranks = {}
        with open('frequent_words.txt', 'r') as f:
            for rank, word in enumerate(f):
                word = word.strip().lower()
                if word in self.words:
                    self.word_ranks[word] = rank
        
    def initUI(self):
        self.setWindowTitle('Word Hunt Solver')
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter 16 letters")
        self.input_field.returnPressed.connect(self.solve)
        input_layout.addWidget(self.input_field)
        
        self.solve_button = QPushButton('Solve')
        self.solve_button.clicked.connect(self.solve)
        input_layout.addWidget(self.solve_button)
        
        layout.addLayout(input_layout)
        
        self.tab_widget = QTabWidget()
        self.all_words_tab = QWidget()
        self.small_words_tab = QWidget()
        self.five_letter_tab = QWidget()
        
        self.setup_tab(self.all_words_tab, "All Words")
        self.setup_tab(self.small_words_tab, "Smallest to Largest")
        self.setup_tab(self.five_letter_tab, "5-Letter Words")
        
        self.tab_widget.addTab(self.all_words_tab, "All Words")
        self.tab_widget.addTab(self.small_words_tab, "Smallest to Largest")
        self.tab_widget.addTab(self.five_letter_tab, "5-Letter Words")
        
        self.tab_widget.currentChanged.connect(self.update_word_label)
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
        
        self.words = []
        self.current_word_index = {
            "All Words": 0,
            "Smallest to Largest": 0,
            "5-Letter Words": 0
        }
        
        self.setFocusPolicy(Qt.StrongFocus)
        
    def setup_tab(self, tab, name):
        tab_layout = QVBoxLayout()
        
        word_label = QLabel()
        tab_layout.addWidget(word_label)
        
        grid = WordGrid()
        tab_layout.addWidget(grid)
        
        button_layout = QHBoxLayout()
        prev_button = QPushButton('Previous Word')
        prev_button.clicked.connect(lambda: self.prev_word(name))
        button_layout.addWidget(prev_button)
        
        next_button = QPushButton('Next Word')
        next_button.clicked.connect(lambda: self.next_word(name))
        button_layout.addWidget(next_button)
        
        tab_layout.addLayout(button_layout)
        tab.setLayout(tab_layout)
        
    def solve(self):
        board_string = self.input_field.text().lower()
        if len(board_string) != 16:
            self.update_word_label("Please enter exactly 16 letters.")
            return
        
        self.board = [list(board_string[i:i+4]) for i in range(0, 16, 4)]
        
        trie = make_trie(self.words)
        
        start_time = time.time()
        found_words = find_words(self.board, trie)
        end_time = time.time()
        
        # Remove duplicates and sort by frequency rank
        self.words = sorted(set((word, tuple(path)) for word, path, _ in found_words), 
                            key=lambda x: (self.word_ranks.get(x[0], float('inf')), -len(x[0]), x[0]))
        
        self.update_word_label(f"Found {len(self.words)} words in {end_time - start_time:.4f} seconds.")
        
        # Sort for different tabs
        self.words_all = sorted(self.words, key=lambda x: (-len(x[0]), self.word_ranks.get(x[0], float('inf')), x[0]))
        self.words_small = sorted(self.words, key=lambda x: (len(x[0]), self.word_ranks.get(x[0], float('inf')), x[0]))
        self.words_five = [word for word in self.words if len(word[0]) == 5]
        self.words_five.sort(key=lambda x: self.word_ranks.get(x[0], float('inf')))
        
        for name in self.current_word_index:
            self.current_word_index[name] = 0
            self.display_word(name)
        
    def display_word(self, tab_name):
        if tab_name == "All Words":
            words = self.words_all
            tab = self.all_words_tab
        elif tab_name == "Smallest to Largest":
            words = self.words_small
            tab = self.small_words_tab
        else:  # 5-Letter Words
            words = self.words_five
            tab = self.five_letter_tab
        
        index = self.current_word_index[tab_name]
        if index < len(words):
            word, path = words[index]
            tab.findChild(QLabel).setText(f"{tab_name}: {word.upper()} ({index + 1}/{len(words)}) Length: {len(word)}")
            
            grid = tab.findChild(WordGrid)
            grid.update_grid(self.board)
            grid.set_path(path)
        else:
            tab.findChild(QLabel).setText(f"{tab_name}: No more words.")
    
    def next_word(self, tab_name):
        words = self.get_words_for_tab(tab_name)
        if self.current_word_index[tab_name] < len(words) - 1:
            self.current_word_index[tab_name] += 1
            self.display_word(tab_name)
    
    def prev_word(self, tab_name):
        if self.current_word_index[tab_name] > 0:
            self.current_word_index[tab_name] -= 1
            self.display_word(tab_name)

    def get_words_for_tab(self, tab_name):
        if tab_name == "All Words":
            return self.words_all
        elif tab_name == "Smallest to Largest":
            return self.words_small
        else:  # 5-Letter Words
            return self.words_five

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.next_word(self.tab_widget.tabText(self.tab_widget.currentIndex()))
        elif event.key() == Qt.Key_Left:
            self.prev_word(self.tab_widget.tabText(self.tab_widget.currentIndex()))
        else:
            super().keyPressEvent(event)

    def update_word_label(self, text):
        for tab in [self.all_words_tab, self.small_words_tab, self.five_letter_tab]:
            tab.findChild(QLabel).setText(str(text))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WordHuntSolver()
    ex.show()
    sys.exit(app.exec_())