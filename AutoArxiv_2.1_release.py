import sys
import feedparser
import html
import webbrowser
import os
import urllib.parse
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QMessageBox

base_url = "http://export.arxiv.org/api/query?"

# Define the categories to search
categories = {
    'Quantum Physics (quant-ph)': 'quant-ph',
    'Applied Physics (physics.app-ph)': 'physics.app-ph',
    'Condensed Matter (cond-mat)': 'cond-mat',
    'Artificial Intelligence (cs.AI)': 'cs.AI',
    'Data Structures and Algorithms (cs.DS)': 'cs.DS',
    'Machine Learning (cs.LG)': 'cs.LG',
    'Systems and Control (cs.SY)': 'cs.SY'
}
max_results_per_category = 10  # Number of results to return per category

class ArxivSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Design the layout
        layout = QVBoxLayout()

        instruction_label = QLabel('Use this GUI to search for papers on arXiv within specified categories and keywords.')
        layout.addWidget(instruction_label)

        example_keywords_label = QLabel('Example keywords: ("spin" AND "qubit") OR ("resonator" AND "qubit" AND "coupling") OR ("hall bar")')
        layout.addWidget(example_keywords_label)

        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText('Enter your keywords here...')
        layout.addWidget(self.keywords_input)

        self.category_checkboxes = {}
        for category_name in categories.keys():
            checkbox = QCheckBox(category_name)
            checkbox.setChecked(True)
            layout.addWidget(checkbox)
            self.category_checkboxes[category_name] = checkbox

        search_button = QPushButton('Search')
        search_button.clicked.connect(self.perform_search)
        layout.addWidget(search_button)

        self.setLayout(layout)
        self.setWindowTitle('arXiv Search GUI')
        #self.setGeometry(300, 300, 400, 400)

    def perform_search(self):
        keywords = self.keywords_input.text().strip()
        if not keywords:
            QMessageBox.warning(self, 'Input Error', 'Please enter some keywords to search for.')
            return

        selected_categories = []
        for category_name, checkbox in self.category_checkboxes.items():
            if checkbox.isChecked():
                selected_categories.append(categories[category_name])
        if not selected_categories:
            QMessageBox.warning(self, 'Input Error', 'Please select at least one category.')
            return

        combined_entries = []
        for category in selected_categories:
            category_query = f'cat:{category} AND ({keywords})'
            entries = self.fetch_papers(category_query)
            combined_entries.extend(entries)
        if not combined_entries:
            QMessageBox.information(self, 'No Results', 'No papers found for the given keywords and categories.')
            return

        self.create_html_file(combined_entries, selected_categories, keywords)

    def fetch_papers(self, query):
        query_url = f"{base_url}search_query={urllib.parse.quote(query)}&start=0&max_results={max_results_per_category}&sortBy=submittedDate&sortOrder=descending"
        feed = feedparser.parse(query_url)
        return feed.entries

    def create_html_file(self, entries, categories, keywords):
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>arXiv Automatic Search Results</title>
    <style>
        .toggle-content {{
            display: none;
            margin-left: 20px;
        }}
        .toggle-button {{
            cursor: pointer;
            font-size: 1.5em;  /* Increase the font size */
        }}
        .toggle-button::before {{
            content: "\\25B6"; /* Triangle symbol */
            display: inline-block;
            margin-right: 6px;
        }}
        .toggle-button.active::before {{
            content: "\\25BC"; /* Downwards triangle symbol */
        }}
    </style>
    <script>
        function toggleContent(id) {{
            var content = document.getElementById(id);
            var button = content.previousElementSibling;
            if (content.style.display === "none") {{
                content.style.display = "block";
                button.classList.add("active");
            }} else {{
                content.style.display = "none";
                button.classList.remove("active");
            }}
        }}
    </script>
</head>
<body>
    <h1>arXiv Automatic Search Results</h1>
    <h2>Searched within: {', '.join(categories)}</h2>
    <p>Keywords: {html.escape(keywords)}</p>
    <p>10 most recent papers in each category and keyword-based search</p>
    <ol>
"""
        for idx, entry in enumerate(entries):
            title = html.escape(entry.title)
            published = entry.published
            link = entry.link
            abstract = html.escape(entry.summary)
            pdf_link = link.replace('abs', 'pdf')  
            content_id = f"content-{idx}"
            html_content += f"""
    <li>
        <div class="toggle-button" onclick="toggleContent('{content_id}')">{title}</div>
        <div id="{content_id}" class="toggle-content">
            <p><strong>Published:</strong> {published}</p>
            <p><strong>Abstract:</strong> {abstract}</p>
            <p><a href="{pdf_link}" target="_blank">Download PDF</a></p>
        </div>
    </li>
    """
        html_content += """
    </ol>
</body>
</html>
"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"arxiv_search_results_{timestamp}.html"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(html_content)
        QMessageBox.information(self, 'Search Completed', f'Search results saved to {filename}')
        webbrowser.open('file://' + os.path.realpath(filename))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ArxivSearchApp()
    ex.show()
    sys.exit(app.exec_())
