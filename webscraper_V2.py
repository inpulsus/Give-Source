import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QTextEdit, QProgressBar, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import json

class Worker(QThread):
    update_progress = pyqtSignal(int)
    result_ready = pyqtSignal(dict)

    def __init__(self, keywords, search_mode):
        super().__init__()
        self.keywords = keywords
        self.search_mode = search_mode

    def run(self):
        results = {
            'Google Scholar': [],
            'Project Gutenberg': [],
            'LibGen': [],
            'PubMed': [],
            'PDFDrive': [],
            'Open Library': []
        }
        
        total_steps = len(results) * len(self.keywords)
        current_step = 0
        
        for keyword in self.keywords:
            if self.search_mode == 'Broad':
                results['Google Scholar'].extend(extract_google_scholar(keyword))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
                results['Project Gutenberg'].extend(extract_gutendex(keyword))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
                results['LibGen'].extend(extract_libgen(keyword))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
                results['PubMed'].extend(extract_pubmed(keyword))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
                results['PDFDrive'].extend(extract_pdfdrive(keyword))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
                results['Open Library'].extend(extract_open_library(keyword))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
            elif self.search_mode == 'Narrow':
                combined_query = ' '.join(self.keywords)
                results['Google Scholar'].extend(extract_google_scholar(combined_query))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
                results['Project Gutenberg'].extend(extract_gutendex(combined_query))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
                results['LibGen'].extend(extract_libgen(combined_query))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
                results['PubMed'].extend(extract_pubmed(combined_query))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
                results['PDFDrive'].extend(extract_pdfdrive(combined_query))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
                results['Open Library'].extend(extract_open_library(combined_query))
                current_step += 1
                self.update_progress.emit(current_step * 100 // total_steps)
                
        self.result_ready.emit(results)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Academic Search')
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        h_layout = QHBoxLayout()
        
        self.keywords_input = QLineEdit(self)
        self.keywords_input.setPlaceholderText('Enter keywords separated by commas')
        h_layout.addWidget(self.keywords_input)
        
        self.search_button = QPushButton('Search', self)
        self.search_button.clicked.connect(self.start_search)
        h_layout.addWidget(self.search_button)
        
        layout.addLayout(h_layout)
        
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)
        
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)
        
        self.search_mode_checkbox = QCheckBox('Narrow Search Mode', self)
        layout.addWidget(self.search_mode_checkbox)
        
        self.setLayout(layout)
        
        dark_style = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QTextEdit, QLineEdit, QPushButton, QProgressBar, QCheckBox {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 10px;
        }
        QPushButton:hover, QCheckBox:hover {
            background-color: #777777;
        }
        QProgressBar {
            border: 2px solid #555555;
            border-radius: 5px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #777777;
            width: 20px;
        }
        """
        self.setStyleSheet(dark_style)

    def start_search(self):
        keywords = self.keywords_input.text().split(',')
        keywords = [keyword.strip() for keyword in keywords]
        
        if not keywords:
            QMessageBox.warning(self, "Warning", "Please enter keywords.")
            return
        
        search_mode = 'Narrow' if self.search_mode_checkbox.isChecked() else 'Broad'

        self.progress_bar.setValue(0)
        self.worker = Worker(keywords, search_mode)
        self.worker.update_progress.connect(self.progress_bar.setValue)
        self.worker.result_ready.connect(self.display_results)
        self.worker.start()

    def display_results(self, results):
        self.output.clear()
        for source, articles in results.items():
            self.output.append(f"\nResults from {source}:\n\n")
            for article in articles:
                self.output.append(f"<font color='lightgrey'>Title: {article['title']}</font>\n")
                self.output.append(f"<a href='{article['link']}' style='color: blue; text-decoration: underline;'>Link: {article['link']}</a>\n\n")
            self.output.append("-------------------------------------------------\n")

def fetch_results(url, headers=None, verify=True):
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    try:
        response = requests.get(url, headers=headers, verify=verify, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def extract_google_scholar(query):
    base_url = "https://scholar.google.com/scholar"
    query = quote(query)
    url = f"{base_url}?q={query}"
    
    html_content = fetch_results(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        results = soup.find_all('h3', {'class': 'gs_rt'})
        articles = []
        for result in results:
            title_element = result.find('a')
            if title_element:
                title = title_element.text.strip()
                link = title_element['href']
                articles.append({'title': title, 'link': link})
        return articles
    else:
        return []

def extract_gutendex(query):
    base_url = "https://gutendex.com/books/"
    query = quote(query)
    url = f"{base_url}?search={query}"
    
    response = fetch_results(url)
    if response:
        data = response.decode('utf-8')
        data = json.loads(data)
        books = []
        for book in data['results']:
            title = book['title']
            link = f"https://www.gutenberg.org/ebooks/{book['id']}"
            books.append({'title': title, 'link': link})
        return books
    else:
        return []

def extract_libgen(query):
    base_url = "http://gen.lib.rus.ec/search.php?req="
    query = quote(query)
    url = f"{base_url}{query}&res=100&column=def"
    
    html_content = fetch_results(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        results = soup.find_all('tr', {'valign': 'top'})
        books = []
        for result in results:
            details = result.find_all('td')
            if len(details) > 2:
                title = details[2].text.strip()
                link = details[2].find('a')['href']
                books.append({'title': title, 'link': link})
        return books
    else:
        return []

def extract_pubmed(query):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    query = quote(query)
    url = f"{base_url}?term={query}"
    
    html_content = fetch_results(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        results = soup.find_all('article', {'class': 'full-docsum'})
        articles = []
        for result in results:
            title_element = result.find('a', {'class': 'docsum-title'})
            if title_element:
                title = title_element.text.strip()
                link = base_url + title_element['href']
                articles.append({'title': title, 'link': link})
        return articles
    else:
        return []

def extract_pdfdrive(query):
    base_url = "https://www.pdfdrive.com/search?q="
    query = quote(query)
    url = f"{base_url}{query}"
    
    html_content = fetch_results(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        results = soup.find_all('div', {'class': 'file-right'})
        books = []
        for result in results:
            title_element = result.find('a', {'class': 'ai-search'})
            if title_element:
                title = title_element.text.strip()
                link = "https://www.pdfdrive.com" + title_element['href']
                books.append({'title': title, 'link': link})
        return books
    else:
        return []

def extract_open_library(query):
    base_url = "https://openlibrary.org/search.json?"
    query = quote(query)
    url = f"{base_url}q={query}"
    
    response = fetch_results(url)
    if response:
        data = response.decode('utf-8')
        data = json.loads(data)
        books = []
        for doc in data['docs']:
            title = doc.get('title', 'No title')
            link = f"https://openlibrary.org{doc.get('key', '')}"
            books.append({'title': title, 'link': link})
        return books
    else:
        return []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

