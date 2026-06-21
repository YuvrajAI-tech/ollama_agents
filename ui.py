"""UI for Ollama Agents Desktop App using PySide6"""
import sys
import threading
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (QMainWindow, QWidget, QTextEdit, QPushButton,
                               QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QLineEdit)
from ollama_client import OllamaClient
from hf_client import HFClient
from executor import Executor
from models import MODEL_PRESETS

APP_NAME = "Ollama Agents"

class App:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = MainWindow()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1000, 700)

        self.ollama = OllamaClient()
        self.hf = HFClient()
        self.executor = Executor()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)

        # Left: Chat
        chat_col = QVBoxLayout()
        layout.addLayout(chat_col, 2)

        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        chat_col.addWidget(self.chat_view)

        input_row = QHBoxLayout()
        self.input_text = QLineEdit()
        input_row.addWidget(self.input_text, 4)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.on_send)
        input_row.addWidget(self.send_btn)

        self.model_select = QComboBox()
        for m in MODEL_PRESETS:
            self.model_select.addItem(m['name'])
        input_row.addWidget(self.model_select, 1)

        chat_col.addLayout(input_row)

        # Right: Tools & Tasks
        tools_col = QVBoxLayout()
        layout.addLayout(tools_col, 1)

        tools_col.addWidget(QLabel("Autonomous Tasks"))
        self.tasks_list = QListWidget()
        tools_col.addWidget(self.tasks_list)

        tools_col.addWidget(QLabel("Run shell command"))
        cmd_row = QHBoxLayout()
        self.cmd_input = QLineEdit()
        cmd_row.addWidget(self.cmd_input)
        self.cmd_run_btn = QPushButton("Run")
        self.cmd_run_btn.clicked.connect(self.on_run_cmd)
        cmd_row.addWidget(self.cmd_run_btn)
        tools_col.addLayout(cmd_row)

        tools_col.addWidget(QLabel("Run Python code"))
        code_row = QHBoxLayout()
        self.code_input = QLineEdit()
        code_row.addWidget(self.code_input)
        self.code_run_btn = QPushButton("Run")
        self.code_run_btn.clicked.connect(self.on_run_code)
        code_row.addWidget(self.code_run_btn)
        tools_col.addLayout(code_row)

        tools_col.addWidget(QLabel("Model provider (HuggingFace Spaces/Models)"))
        self.hf_space_input = QLineEdit()
        self.hf_space_input.setPlaceholderText("owner/space or model-id (optional)")
        tools_col.addWidget(self.hf_space_input)

        tools_col.addStretch()

        # Status
        self.status = QLabel("Ready")
        self.status.setAlignment(QtCore.Qt.AlignLeft)
        tools_col.addWidget(self.status)

    def append_chat(self, who, text):
        self.chat_view.append(f"<b>{who}</b>: {text}")

    def on_send(self):
        text = self.input_text.text().strip()
        if not text:
            return
        self.append_chat("You", text)
        self.input_text.clear()
        model_name = MODEL_PRESETS[self.model_select.currentIndex()]['id']
        # Run chat in thread
        threading.Thread(target=self._send_chat, args=(model_name, text), daemon=True).start()

    def _send_chat(self, model_name, text):
        self.set_status("Thinking…")
        try:
            # Primary through Ollama
            resp = self.ollama.chat(model_name, text)
            if resp is None:
                # fallback to Hugging Face if a space/model provided
                hf_id = self.hf_space_input.text().strip()
                if hf_id:
                    resp = self.hf.chat(hf_id, text)
                else:
                    resp = "(no response)"
            self.append_chat("AI", resp)
        except Exception as e:
            self.append_chat("Error", str(e))
        finally:
            self.set_status("Ready")

    def on_run_cmd(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        self.append_chat("System", f"Running command: {cmd}")
        threading.Thread(target=self._run_cmd, args=(cmd,), daemon=True).start()

    def _run_cmd(self, cmd):
        self.set_status("Running command…")
        out, err, code = self.executor.run_shell(cmd)
        self.append_chat("Command Output", out or "(no stdout)")
        if err:
            self.append_chat("Command Error", err)
        self.set_status(f"Command exited {code}")

    def on_run_code(self):
        code = self.code_input.text().strip()
        if not code:
            return
        self.append_chat("System", "Executing Python code…")
        threading.Thread(target=self._run_code, args=(code,), daemon=True).start()

    def _run_code(self, code):
        self.set_status("Running code…")
        out, err, code_ret = self.executor.run_python(code)
        self.append_chat("Code Output", out or "(no stdout)")
        if err:
            self.append_chat("Code Error", err)
        self.set_status(f"Code exited {code_ret}")

    def set_status(self, txt):
        self.status.setText(txt)
