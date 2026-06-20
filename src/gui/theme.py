B3_STYLE = """
QMainWindow, QWidget {
    background-color: #1a1a1f;
    color: #e8e8ea;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #2d2d35;
    border-radius: 6px;
    background-color: #1a1a1f;
    top: -1px;
}

QTabBar::tab {
    background-color: #25252d;
    color: #a0a0a8;
    padding: 10px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #1a1a1f;
    color: #ffffff;
    border-bottom: 2px solid #e85d04;
}

QTabBar::tab:hover {
    color: #ffffff;
}

QLabel#HeaderLabel {
    font-size: 20px;
    font-weight: bold;
    color: #ffffff;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #25252d;
    border: 1px solid #3a3a45;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 22px;
    color: #e8e8ea;
    selection-background-color: #e85d04;
}

QLineEdit:read-only {
    color: #c8c8cc;
}

QLineEdit:disabled {
    background-color: #1f1f26;
    color: #666670;
}

QPushButton {
    background-color: #2d2d35;
    border: 1px solid #3a3a45;
    border-radius: 4px;
    padding: 8px 14px;
    color: #e8e8ea;
}

QPushButton:hover {
    background-color: #3a3a45;
    border-color: #e85d04;
}

QPushButton:pressed {
    background-color: #25252d;
}

QPushButton:disabled {
    background-color: #1f1f26;
    color: #666670;
    border-color: #2d2d35;
}

QPushButton#PrimaryAction {
    background-color: #e85d04;
    border: 1px solid #dc2f02;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
    padding: 12px;
}

QPushButton#PrimaryAction:hover {
    background-color: #f48c06;
}

QPushButton#PrimaryAction:pressed {
    background-color: #dc2f02;
}

QPushButton#ExitButton {
    background-color: #A93226;
    border: 1px solid #7B241C;
    color: #ffffff;
    min-width: 80px;
    max-width: 80px;
    min-height: 26px;
    max-height: 26px;
    padding: 2px 8px;
}

QPushButton#ExitButton:hover {
    background-color: #7B241C;
}

QTextEdit#LogConsole {
    background-color: #121218;
    border: 1px solid #2d2d35;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    color: #b8b8c0;
    min-height: 120px;
}

/* --- APARATUROWY, PANCERNY QGROUPBOX --- */
QGroupBox {
    border: 1px solid #2d2d35;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px; /* KLUCZOWY FIX: Odpycha zawartość layoutu poniżej linii ramki i tytułu */
    font-weight: bold;
    color: #c8c8cc;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 3px;
    padding: 0 6px;
    background-color: #1a1a1f; /* Maskuje linię ramki pod tekstem tytułu */
}
"""