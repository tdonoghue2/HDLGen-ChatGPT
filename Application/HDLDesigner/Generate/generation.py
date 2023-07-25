import os
from xml.dom import minidom
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import pyperclip
import sys
import configparser
import qtawesome as qta

sys.path.append("..")
from HDLDesigner.ChatGPT.chatgpt_help import ChatGPTHelpDialog
from HDLDesigner.ChatGPT.VHDLHeader import VHDLHeaderDialog
from HDLDesigner.ChatGPT.VerilogHeader import VerilogHeaderDialog
from HDLDesigner.ChatGPT.VHDLModel import VHDLModelDialog
from HDLDesigner.ChatGPT.VerilogModel import VerilogModelDialog
from HDLDesigner.ChatGPT.VHDLTestbench import VHDLTestbenchDialog
from HDLDesigner.ChatGPT.VerilogTestbench import VerilogTestbenchDialog
from ProjectManager.project_manager import ProjectManager
from Generator.generator import Generator

WHITE_COLOR = "color: white"
BLACK_COLOR = "color: black"
MEDIUM_SPACING = 25


class Gen(QWidget):
    save_signal = Signal(bool)

    def __init__(self, proj_dir):
        super().__init__()
        small_text_font = QFont()
        small_text_font.setPointSize(10)
        small_text_font.setBold(True)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        self.proj_dir = proj_dir
        #self.commands = ["None", "None", "None", "None", "None", "None"]
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        VHDLHeader = self.config.get('user', 'vhdlchatgptheader')
        VerilogHeader = self.config.get('user', 'verilogchatgptheader')
        VHDLModel = self.config.get('user', 'vhdlchatgptmodel')
        VerilogModel = self.config.get('user', 'verilogchatgptmodel')
        VHDLTestbench = self.config.get('user', 'vhdlchatgpttestbench')
        VerilogTestbench = self.config.get('user', 'verilogchatgpttestbench')
        VHDLHeader = self.remove_blank_lines(VHDLHeader)
        VerilogHeader = self.remove_blank_lines(VerilogHeader)
        VHDLModel = self.remove_blank_lines(VHDLModel)
        VerilogModel = self.remove_blank_lines(VerilogModel)
        VHDLTestbench = self.remove_blank_lines(VHDLTestbench)
        VerilogTestbench = self.remove_blank_lines(VerilogTestbench)
        self.commands = [VHDLHeader, VerilogHeader, VHDLModel, VerilogModel, VHDLTestbench, VerilogTestbench]
        self.proj_path = ""
        self.entity_name = ""
        self.mainLayout = QVBoxLayout()
        self.modelFrame = QFrame()
        self.headerModelFrame = QFrame()
        self.chatgptModelFrame = QFrame()
        self.testbenchFrame = QFrame()
        self.headerTestbenchFrame = QFrame()
        self.chatgptTestbenchFrame = QFrame()
        self.titleFrame = QFrame()
        self.headerTitleFrame = QFrame()
        self.chatgptTitleFrame = QFrame()
        
        
        self.input_layout = QGridLayout()

        self.gen_label = QLabel("Generate VHDL")
        self.gen_label.setFont(title_font)
        self.gen_label.setStyleSheet(WHITE_COLOR)

        self.chatgpt_info_btn = QPushButton()
        self.chatgpt_info_btn.setIcon(qta.icon("mdi.help"))
        self.chatgpt_info_btn.setFixedSize(25, 25)
        self.chatgpt_info_btn.clicked.connect(self.chatgpt_help_window)

        self.chatgpt_title_label = QLabel("ChatGPT message header\nfor formatting HDL\nmodel title generation")
        self.chatgpt_title_label.setStyleSheet(BLACK_COLOR)
        self.chatgpt_title_label.setFont(small_text_font)
        self.chatgpt_title_label.setFixedSize(200, 50)

        self.msg_title_label = QLabel("ChatGPT message elements:\nChatGPT message,HDL\nmodel title section")
        self.msg_title_label.setStyleSheet(BLACK_COLOR)
        self.msg_title_label.setFont(small_text_font)

        self.generate_chatgpt_title = QPushButton("Generate and Copy")

        self.generate_chatgpt_title.setFixedSize(200, 50)
        self.generate_chatgpt_title.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.chatgpt_title_bk_checkBox = QCheckBox("Enable backup of previous version (_n)")
        self.chatgpt_title_bk_checkBox.setStyleSheet(BLACK_COLOR)

        self.delete_bk_title_chatgpt = QPushButton("Delete backups")
        self.delete_bk_title_chatgpt.setFixedSize(200, 50)
        self.delete_bk_title_chatgpt.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.chatgpt_loc_title = QPushButton("Go to folder")
        self.chatgpt_loc_title.setFixedSize(200, 50)
        self.chatgpt_loc_title.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")


        self.model_label = QLabel("HDL Model Template")
        self.model_label.setStyleSheet(BLACK_COLOR)
        self.model_label.setFont(small_text_font)

        self.chatgpt_model_label = QLabel("ChatGPT message header for\nHDL model generation")
        self.chatgpt_model_label.setStyleSheet(BLACK_COLOR)
        self.chatgpt_model_label.setFont(small_text_font)
        #self.chatgpt_model_label.setFixedSize(200, 50)

        self.msg_model_label = QLabel("ChatGPT message elements:\nChatGPT message header,\nHDL model template")
        self.msg_model_label.setStyleSheet(BLACK_COLOR)
        self.msg_model_label.setFont(small_text_font)

        self.generate_model = QPushButton("Generate")
        self.generate_model.setFixedSize(200, 50)
        self.generate_model.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.model_bk_checkBox = QCheckBox("Enable backup of previous version (_n)")
        self.model_bk_checkBox.setStyleSheet(BLACK_COLOR)

        self.generate_chatgpt_model = QPushButton("Generate and Copy")
        self.generate_chatgpt_model.setFixedSize(200, 50)
        self.generate_chatgpt_model.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.chatgpt_model_bk_checkBox = QCheckBox("Enable backup of previous version (_n)")
        self.chatgpt_model_bk_checkBox.setStyleSheet(BLACK_COLOR)

        self.delete_bk_model = QPushButton("Delete backups")
        self.delete_bk_model.setFixedSize(200, 50)
        self.delete_bk_model.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.delete_bk_model_chatgpt = QPushButton("Delete backups")
        self.delete_bk_model_chatgpt.setFixedSize(200, 50)
        self.delete_bk_model_chatgpt.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.loc_model = QPushButton("Go to folder")
        self.loc_model.setFixedSize(200, 50)
        self.loc_model.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.chatgpt_loc_model = QPushButton("Go to folder")
        self.chatgpt_loc_model.setFixedSize(200, 50)
        self.chatgpt_loc_model.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.testbench_label = QLabel("HDL Testbench Template")
        self.testbench_label.setStyleSheet(BLACK_COLOR)
        self.testbench_label.setFont(small_text_font)


        self.chatgpt_testbench_label = QLabel("ChatGPT message header for\nHDL testbench generation")#\n(only 'ChatGPT message head'\nis currently shown)")
        self.chatgpt_testbench_label.setStyleSheet(BLACK_COLOR)
        self.chatgpt_testbench_label.setFont(small_text_font)
        #self.chatgpt_testbench_label.setFixedSize(200, 50)

        self.msg_testbench_label = QLabel("ChatGPT message elements:\nChatGPT message header,\ntestbench signals, test plan")
        self.msg_testbench_label.setStyleSheet(BLACK_COLOR)
        self.msg_testbench_label.setFont(small_text_font)

        self.generate_testbench = QPushButton("Generate")
        self.generate_testbench.setFixedSize(200, 50)
        self.generate_testbench.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.testbench_bk_checkBox = QCheckBox("Enable backup of previous version (_n)")
        self.testbench_bk_checkBox.setStyleSheet(BLACK_COLOR)

        self.wcfg_checkBox = QCheckBox("Waveform Configuration File")
        self.wcfg_checkBox.setStyleSheet(BLACK_COLOR)
        self.wcfg_checkBox.setChecked(True)

        self.generate_chatgpt_testbench = QPushButton("Generate and Copy")
        self.generate_chatgpt_testbench.setFixedSize(200, 50)
        self.generate_chatgpt_testbench.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.chatgpt_testbench_bk_checkBox = QCheckBox("Enable backup of previous version (_n)")
        self.chatgpt_testbench_bk_checkBox.setStyleSheet(BLACK_COLOR)

        self.delete_bk_testbench = QPushButton("Delete backups")
        self.delete_bk_testbench.setFixedSize(200, 50)
        self.delete_bk_testbench.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.delete_bk_testbench_chatgpt = QPushButton("Delete backups")
        self.delete_bk_testbench_chatgpt.setFixedSize(200, 50)
        self.delete_bk_testbench_chatgpt.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.loc_testbench = QPushButton("Go to folder")
        self.loc_testbench.setFixedSize(200, 50)
        self.loc_testbench.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.chatgpt_loc_testbench = QPushButton("Go to folder")
        self.chatgpt_loc_testbench.setFixedSize(200, 50)
        self.chatgpt_loc_testbench.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.title_VHDL = QPushButton("Edit")
        self.title_VHDL.setFixedSize(200, 50)
        self.title_VHDL.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")

        self.model_VHDL = QPushButton("Edit")
        self.model_VHDL.setFixedSize(200, 50)
        self.model_VHDL.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")


        self.testbench_VHDL = QPushButton("Edit")
        self.testbench_VHDL.setFixedSize(200, 50)
        self.testbench_VHDL.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")


        self.title_Verilog = QPushButton("Edit")
        self.title_Verilog.setFixedSize(200, 50)
        self.title_Verilog.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")
        self.title_Verilog.setVisible(False)


        self.model_Verilog = QPushButton("Edit")
        self.model_Verilog.setFixedSize(200, 50)
        self.model_Verilog.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")
        self.model_Verilog.setVisible(False)


        self.testbench_Verilog = QPushButton("Edit")
        self.testbench_Verilog.setFixedSize(200, 50)
        self.testbench_Verilog.setStyleSheet(
            "QPushButton {background-color: rgb(97, 107, 129); color: white; border-radius: 10px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(72, 80, 98);  color: white; border-radius: 10px; border-style: plain;}")
        self.testbench_Verilog.setVisible(False)

        self.header_title_check = QRadioButton("Preview")
        self.header_title_check.setStyleSheet(BLACK_COLOR)
        self.header_title_check.setChecked(True)
        self.header_model_check = QRadioButton("Preview")
        self.header_model_check.setStyleSheet(BLACK_COLOR)
        self.header_model_check.setFixedSize(200, 50)
        #self.header_model_check.setChecked(True)
        self.header_testbench_check = QRadioButton("Preview")
        self.header_testbench_check.setStyleSheet(BLACK_COLOR)
        self.header_testbench_check.setFixedSize(200, 50)
        #self.header_testbench_check.setChecked(True)
        self.model_check = QRadioButton("Preview")
        self.model_check.setStyleSheet(BLACK_COLOR)
        self.model_check.setChecked(True)

        self.testbench_check = QRadioButton("Preview")
        self.testbench_check.setStyleSheet(BLACK_COLOR)
        self.testbench_check.setChecked(True)
        self.msg_model_check = QRadioButton("Preview")
        self.msg_model_check.setStyleSheet(BLACK_COLOR)
        self.msg_title_check = QRadioButton("Preview")
        self.msg_title_check.setStyleSheet(BLACK_COLOR)
        self.msg_testbench_check = QRadioButton("Preview")
        self.msg_testbench_check.setStyleSheet(BLACK_COLOR)

        self.model_button_group = QButtonGroup()
        self.model_button_group.addButton(self.header_model_check)
        self.model_button_group.addButton(self.msg_model_check)
        self.model_button_group.addButton(self.model_check)

        self.testbench_button_group = QButtonGroup()
        self.testbench_button_group.addButton(self.header_testbench_check)
        self.testbench_button_group.addButton(self.msg_testbench_check)
        self.testbench_button_group.addButton(self.testbench_check)

        self.title_button_group = QButtonGroup()
        self.title_button_group.addButton(self.header_title_check)
        self.title_button_group.addButton(self.msg_title_check)

        self.top_layout = QGridLayout()
        self.arch_action_layout = QVBoxLayout()
        self.btn_layout = QHBoxLayout()

        self.vspacer = QSpacerItem(30, 40)
        self.list_layout = QVBoxLayout()
        self.list_frame = QFrame()
        self.main_frame = QFrame()
        self.input_frame = QFrame()
        self.generator = Generator()
      #  self.project_manager = ProjectManager(self.proj_dir, self)
        self.setup_ui()
        if proj_dir != None:
            self.load_data(proj_dir)



    def setup_ui(self):
        bold_font = QFont()
        bold_font.setBold(True)

        self.top_layout.addWidget(self.gen_label, 0, 0, 1, 1)
        self.top_layout.addWidget(self.chatgpt_info_btn, 0, 1, 1, 1)
        self.arch_action_layout.addLayout(self.top_layout)
        self.main_frame.setFrameShape(QFrame.StyledPanel)
        self.main_frame.setStyleSheet('.QFrame{background-color: rgb(97, 107, 129); border-radius: 5px;}')
        self.title_VHDL.clicked.connect(self.vhdl_header_command)
        self.title_Verilog.clicked.connect(self.verilog_header_command)
        self.model_VHDL.clicked.connect(self.vhdl_model_command)
        self.model_Verilog.clicked.connect(self.verilog_model_command)
        self.testbench_VHDL.clicked.connect(self.vhdl_testbench_command)
        self.testbench_Verilog.clicked.connect(self.verilog_testbench_command)
        self.main_frame.setLayout(self.arch_action_layout)

        self.list_frame.setFrameShape(QFrame.StyledPanel)
        self.list_frame.setStyleSheet('.QFrame{background-color: white; border-radius: 5px;}')
        self.list_frame.setLayout(self.input_layout)

        self.tab_widget = QTabWidget()

        # Create three tabs
        self.HDLModel = QFrame()
        self.HDLModel.setFrameShape(QFrame.StyledPanel)
        self.HDLModel.setStyleSheet(".QFrame{background-color: white; border-radius: 5px;}")
        #self.HDLModel.setContentsMargins(40,40,40,40)


        self.HDLTB = QFrame()
        self.HDLTB.setFrameShape(QFrame.StyledPanel)
        self.HDLTB.setStyleSheet(".QFrame{background-color: white; border-radius: 5px;}")
        #self.HDLTB.setContentsMargins(40, 40, 40, 40)

        self.HDLTitle = QFrame()

        # Add the tabs to the tab widget
        self.tab_widget.addTab(self.HDLModel, "HDL Model")
        self.tab_widget.addTab(self.HDLTB, "HDL Testbench")
        #self.tab_widget.addTab(self.HDLTitle, "Format HDL Model Title")


        # Create layouts for each tab
        self.HDLModelLayout = QVBoxLayout(self.HDLModel)
        self.HDLModel.setLayout(self.HDLModelLayout)
        self.header_msg_model_layout = QGridLayout()
        self.ModelLayout = QGridLayout()
        self.ChatgptModelLayout = QGridLayout()
        
        #self.ModelLayout = QGridLayout(self.HDLModel)
        #self.TBLayout = QGridLayout(self.HDLTB)
        self.HDLTestbenchLayout = QVBoxLayout(self.HDLTB)
        self.HDLTB.setLayout(self.HDLTestbenchLayout)
        self.header_msg_testbench_layout = QGridLayout()
        self.TestbenchLayout = QGridLayout()
        self.ChatgptTestbenchLayout = QGridLayout()

        #self.TitleLayout = QGridLayout(self.HDLTitle)
        self.HDLTitleLayout = QVBoxLayout(self.HDLTitle)
        self.HDLTitle.setLayout(self.HDLTitleLayout)
        self.header_msg_title_layout = QGridLayout()
        self.ChatgptTitleLayout = QGridLayout()

        self.ModelLayout.addWidget(self.model_label, 0, 0)
        self.ModelLayout.addWidget(self.loc_model, 0, 1)
        self.ModelLayout.addWidget(self.model_check, 2, 0)
        self.ModelLayout.addWidget(self.generate_model, 1, 0)
        self.ModelLayout.addWidget(self.model_bk_checkBox, 2, 1)
        self.ModelLayout.addWidget(self.delete_bk_model, 1, 1)
        self.modelFrame.setLayout(self.ModelLayout)
        self.modelFrame.setStyleSheet(
            ".QFrame{background-color: white; border-radius: 5px;}")

        self.header_msg_model_layout.addWidget(self.chatgpt_model_label, 0, 0)
        self.header_msg_model_layout.addWidget(self.header_model_check, 1, 0)
        self.header_msg_model_layout.addWidget(self.model_VHDL, 0, 1)
        self.header_msg_model_layout.addWidget(self.model_Verilog, 0, 1)
        self.headerModelFrame.setLayout(self.header_msg_model_layout)
        self.headerModelFrame.setStyleSheet(
            ".QFrame{background-color: white; border-radius: 5px;}")
        self.headerModelBorderFrame = QFrame()
        self.headerModelBorderFrame.setStyleSheet(
            ".QFrame{background-color: rgb(97, 107, 129); border: 2.5px solid rgb(97, 107, 129);}")
        self.headerModelBorderFrameLayout = QVBoxLayout(self.headerModelBorderFrame)
        self.headerModelBorderFrameLayout.addWidget(self.headerModelFrame)
        self.HDLModelLayout.addWidget(self.headerModelBorderFrame)
        self.HDLModelLayout.addSpacing(MEDIUM_SPACING)

        self.ChatgptModelLayout.addWidget(self.msg_model_label, 0, 0)
        self.ChatgptModelLayout.addWidget(self.chatgpt_loc_model, 0, 1)
        self.ChatgptModelLayout.addWidget(self.msg_model_check, 2, 0)
        self.ChatgptModelLayout.addWidget(self.generate_chatgpt_model, 1, 0)
        self.ChatgptModelLayout.addWidget(self.chatgpt_model_bk_checkBox, 2, 1)
        self.ChatgptModelLayout.addWidget(self.delete_bk_model_chatgpt, 1, 1)
        self.chatgptModelFrame.setLayout(self.ChatgptModelLayout)
        self.chatgptModelFrame.setStyleSheet(
            ".QFrame{background-color: white; border-radius: 5px;}")
        self.modelBorderFrame=QFrame()
        self.modelBorderFrame.setStyleSheet(".QFrame{background-color: rgb(97, 107, 129); border: 2.5px solid rgb(97, 107, 129);}")
        self.modelBorderFrameLayout=QVBoxLayout(self.modelBorderFrame)
        self.modelBorderFrameLayout.addWidget(self.modelFrame)

        self.HDLModelLayout.addWidget(self.modelBorderFrame)
        #self.HDLModelLayout.addWidget(self.modelFrame)
        self.HDLModelLayout.addSpacing(MEDIUM_SPACING)

        self.chatgptModelBorderFrame = QFrame()
        self.chatgptModelBorderFrame.setStyleSheet(
            ".QFrame{background-color: rgb(97, 107, 129); border: 2.5px solid rgb(97, 107, 129);}")
        self.chatgptModelBorderFrameLayout = QVBoxLayout(self.chatgptModelBorderFrame)
        self.chatgptModelBorderFrameLayout.addWidget(self.chatgptModelFrame)
        self.HDLModelLayout.addWidget(self.chatgptModelBorderFrame)

        self.TestbenchLayout.addWidget(self.testbench_label, 0, 0)
        self.TestbenchLayout.addWidget(self.loc_testbench, 0, 1)
        self.TestbenchLayout.addWidget(self.generate_testbench, 1, 0)
        self.TestbenchLayout.addWidget(self.testbench_bk_checkBox, 3, 1)
        self.TestbenchLayout.addWidget(self.testbench_check, 2, 0)
        self.TestbenchLayout.addWidget(self.wcfg_checkBox, 2, 1)
        self.TestbenchLayout.addWidget(self.delete_bk_testbench, 1, 1)
        self.testbenchFrame.setLayout(self.TestbenchLayout)
        self.testbenchFrame.setStyleSheet(
            ".QFrame{background-color: white; border-radius: 5px;}")

        self.header_msg_testbench_layout.addWidget(self.chatgpt_testbench_label, 0, 0)
        self.header_msg_testbench_layout.addWidget(self.header_testbench_check, 1, 0)
        self.header_msg_testbench_layout.addWidget(self.testbench_VHDL, 0, 1)
        self.header_msg_testbench_layout.addWidget(self.testbench_Verilog, 0, 1)
        self.headerTestbenchFrame.setLayout(self.header_msg_testbench_layout)
        self.headerTestbenchFrame.setStyleSheet(
            ".QFrame{background-color: white; border-radius: 5px;}")
        self.headerTestbenchBorderFrame = QFrame()
        self.headerTestbenchBorderFrame.setStyleSheet(
            ".QFrame{background-color: rgb(97, 107, 129); border: 2.5px solid rgb(97, 107, 129);}")
        self.headerTestbenchBorderFrameLayout = QVBoxLayout(self.headerTestbenchBorderFrame)
        self.headerTestbenchBorderFrameLayout.addWidget(self.headerTestbenchFrame)
        self.HDLTestbenchLayout.addWidget(self.headerTestbenchBorderFrame)
        self.HDLTestbenchLayout.addSpacing(MEDIUM_SPACING)

        self.ChatgptTestbenchLayout.addWidget(self.msg_testbench_label, 0, 0)
        self.ChatgptTestbenchLayout.addWidget(self.chatgpt_loc_testbench, 0, 1)
        #self.ChatgptTestbenchLayout.addWidget(self.testbench_VHDL, 4, 0)
        self.ChatgptTestbenchLayout.addWidget(self.generate_chatgpt_testbench, 1, 0)
        #self.ChatgptTestbenchLayout.addWidget(self.testbench_Verilog, 4, 0)
        self.ChatgptTestbenchLayout.addWidget(self.chatgpt_testbench_bk_checkBox, 2, 1)
        self.ChatgptTestbenchLayout.addWidget(self.msg_testbench_check, 2, 0)
        self.ChatgptTestbenchLayout.addWidget(self.delete_bk_testbench_chatgpt, 1, 1)

        self.chatgptTestbenchFrame.setLayout(self.ChatgptTestbenchLayout)
        self.chatgptTestbenchFrame.setStyleSheet(
            ".QFrame{background-color: white; border-radius: 5px;}")
        self.testbenchBorderFrame = QFrame()
        self.testbenchBorderFrame.setStyleSheet(
            ".QFrame{background-color: rgb(97, 107, 129); border: 2.5px solid rgb(97, 107, 129);}")
        self.testbenchBorderFrameLayout = QVBoxLayout(self.testbenchBorderFrame)
        self.testbenchBorderFrameLayout.addWidget(self.testbenchFrame)

        self.HDLTestbenchLayout.addWidget(self.testbenchBorderFrame)
        # self.HDLModelLayout.addWidget(self.modelFrame)
        self.HDLTestbenchLayout.addSpacing(MEDIUM_SPACING)

        self.chatgptTestbenchBorderFrame = QFrame()
        self.chatgptTestbenchBorderFrame.setStyleSheet(
            ".QFrame{background-color: rgb(97, 107, 129); border: 2.5px solid rgb(97, 107, 129);}")
        self.chatgptTestbenchBorderFrameLayout = QVBoxLayout(self.chatgptTestbenchBorderFrame)
        self.chatgptTestbenchBorderFrameLayout.addWidget(self.chatgptTestbenchFrame)
        self.HDLTestbenchLayout.addWidget(self.chatgptTestbenchBorderFrame)

        self.header_msg_title_layout.addWidget(self.chatgpt_title_label, 0, 0)
        self.header_msg_title_layout.addWidget(self.header_title_check, 1, 0)
        self.header_msg_title_layout.addWidget(self.title_VHDL, 0, 1)
        self.header_msg_title_layout.addWidget(self.title_Verilog, 0, 1)
        self.headerTitleFrame.setLayout(self.header_msg_title_layout)
        self.headerTitleFrame.setStyleSheet(
            ".QFrame{background-color: white; border-radius: 5px;}")
        self.headerTitleBorderFrame = QFrame()
        self.headerTitleBorderFrame.setStyleSheet(
            ".QFrame{background-color: rgb(97, 107, 129); border: 2.5px solid rgb(97, 107, 129);}")
        self.headerTitleBorderFrameLayout = QVBoxLayout(self.headerTitleBorderFrame)
        self.headerTitleBorderFrameLayout.addWidget(self.headerTitleFrame)
        self.HDLTitleLayout.addWidget(self.headerTitleBorderFrame)
        self.HDLTitleLayout.addSpacing(MEDIUM_SPACING)

        self.ChatgptTitleLayout.addWidget(self.msg_title_label, 0, 0)
        self.ChatgptTitleLayout.addWidget(self.chatgpt_loc_title, 0, 1)
        # self.ChatgptTitleLayout.addWidget(self.title_VHDL, 4, 0)
        self.ChatgptTitleLayout.addWidget(self.generate_chatgpt_title, 1, 0)
        # self.ChatgptTitleLayout.addWidget(self.title_Verilog, 4, 0)
        self.ChatgptTitleLayout.addWidget(self.chatgpt_title_bk_checkBox, 2, 1)
        self.ChatgptTitleLayout.addWidget(self.msg_title_check, 2, 0)
        self.ChatgptTitleLayout.addWidget(self.delete_bk_title_chatgpt, 1, 1)

        self.chatgptTitleFrame.setLayout(self.ChatgptTitleLayout)
        self.chatgptTitleFrame.setStyleSheet(
            ".QFrame{background-color: white; border-radius: 5px;}")
        self.titleBorderFrame = QFrame()
        self.titleBorderFrame.setStyleSheet(
            ".QFrame{background-color: rgb(97, 107, 129); border: 2.5px solid rgb(97, 107, 129);}")
        self.titleBorderFrameLayout = QVBoxLayout(self.titleBorderFrame)
        self.titleBorderFrameLayout.addWidget(self.titleFrame)

        #self.HDLTitleLayout.addWidget(self.titleBorderFrame)
        # self.HDLModelLayout.addWidget(self.modelFrame)
        #self.HDLTitleLayout.addSpacing(MEDIUM_SPACING)

        self.chatgptTitleBorderFrame = QFrame()
        self.chatgptTitleBorderFrame.setStyleSheet(
            ".QFrame{background-color: rgb(97, 107, 129); border: 2.5px solid rgb(97, 107, 129);}")
        self.chatgptTitleBorderFrameLayout = QVBoxLayout(self.chatgptTitleBorderFrame)
        self.chatgptTitleBorderFrameLayout.addWidget(self.chatgptTitleFrame)
        self.HDLTitleLayout.addWidget(self.chatgptTitleBorderFrame)



        #self.TitleLayout.addWidget(self.header_VHDL, 1,0)
        #self.TitleLayout.addWidget(self.header_Verilog, 1, 0)

        self.input_layout.addWidget(self.tab_widget)
        self.arch_action_layout.addItem(QSpacerItem(0, 5))
        self.arch_action_layout.addWidget(self.list_frame)
        self.arch_action_layout.addItem(QSpacerItem(0, 5))

        self.mainLayout.addWidget(self.main_frame)

        self.setLayout(self.mainLayout)
        #self.generate_model.clicked.connect(self.HDL_model_generate)
        #self.generate_chatgpt_model.clicked.connect(self.chatgpt_model_generate)
        #self.generate_testbench.clicked.connect(self.HDL_testbench_generate)
        #self.generate_chatgpt_testbench.clicked.connect(self.chatgpt_testbench_generate)

    def remove_blank_lines(self, text):
        lines = text.split("\n")  # Split the string into lines
        non_empty_lines = [line for line in lines if line.strip()]  # Remove blank lines
        return "\n".join(non_empty_lines)

    def save_data(self):

        xml_data_path = ProjectManager.get_xml_data_path()

        root = minidom.parse(xml_data_path)
        HDLGen = root.documentElement
        hdlDesign = HDLGen.getElementsByTagName("hdlDesign")

        new_chatgpt = root.createElement('chatgpt')
        commands_node = root.createElement('commands')

        VHDLHeader_node = root.createElement('VHDLHeader')
        self.commands[0] = self.commands[0].replace("\n", "&#10;" )
        VHDLHeader_node.appendChild(root.createTextNode(self.commands[0]))
        commands_node.appendChild(VHDLHeader_node)

        VerilogHeader_node = root.createElement('VerilogHeader')
        self.commands[1] = self.commands[1].replace("\n", "&#10;")
        VerilogHeader_node.appendChild(root.createTextNode(self.commands[1]))
        commands_node.appendChild(VerilogHeader_node)

        VHDLModel_node = root.createElement('VHDLModel')
        self.commands[2] = self.commands[2].replace("\n", "&#10;")
        VHDLModel_node.appendChild(root.createTextNode(self.commands[2]))
        commands_node.appendChild(VHDLModel_node)

        VerilogModel_node = root.createElement('VerilogModel')
        self.commands[3] = self.commands[3].replace("\n", "&#10;")
        VerilogModel_node.appendChild(root.createTextNode(self.commands[3]))
        commands_node.appendChild(VerilogModel_node)

        VHDLTestbench_node = root.createElement('VHDLTestbench')
        self.commands[4] = self.commands[4].replace("\n", "&#10;")
        VHDLTestbench_node.appendChild(root.createTextNode(self.commands[4]))
        commands_node.appendChild(VHDLTestbench_node)

        VerilogTestbench_node = root.createElement('VerilogTestbench')
        self.commands[5] = self.commands[5].replace("\n", "&#10;")
        VerilogTestbench_node.appendChild(root.createTextNode(self.commands[5]))
        commands_node.appendChild(VerilogTestbench_node)

        new_chatgpt.appendChild(commands_node)
        hdlDesign[0].replaceChild(new_chatgpt, hdlDesign[0].getElementsByTagName('chatgpt')[0])

        # converting the doc into a string in xml format
        xml_str = root.toprettyxml()
        xml_str = os.linesep.join([s for s in xml_str.splitlines() if s.strip()])
        # Writing xml file
        with open(xml_data_path, "w") as f:
            f.write(xml_str)
        hdl = False
        self.save_signal.emit(hdl)
        print("Saved ChatGPT commands")

    def load_data(self, proj_dir):
        proj_name = ProjectManager.get_proj_name()
        self.proj_path = os.path.join(ProjectManager.get_proj_dir(), proj_name)

        root = minidom.parse(proj_dir[0])
        HDLGen = root.documentElement
        projectManager = HDLGen.getElementsByTagName("projectManager")
        HDL = projectManager[0].getElementsByTagName("HDL")[0]
        if HDL.hasChildNodes():
            lang_node = HDL.getElementsByTagName('language')[0]
            lang = lang_node.getElementsByTagName('name')[0].firstChild.data
            if lang == "VHDL":
                self.VHDLVisible()
            else:
                self.VerilogVisible()
        hdlDesign = HDLGen.getElementsByTagName("hdlDesign")
        header_node = hdlDesign[0].getElementsByTagName("header")
        if header_node is not None:
            comp_node = header_node[0].getElementsByTagName("compName")[0]
            if comp_node.firstChild.data != "null":
                self.entity_name = comp_node.firstChild.data
        chatgpt = hdlDesign[0].getElementsByTagName('chatgpt')[0]
        if chatgpt.hasChildNodes():
            commands_node = chatgpt.getElementsByTagName('commands')[0]

            VHDLHeader = commands_node.getElementsByTagName('VHDLHeader')[0].firstChild.data
            VerilogHeader = commands_node.getElementsByTagName('VerilogHeader')[0].firstChild.data
            VHDLModel = commands_node.getElementsByTagName('VHDLModel')[0].firstChild.data
            VerilogModel = commands_node.getElementsByTagName('VerilogModel')[0].firstChild.data
            VHDLTestbench = commands_node.getElementsByTagName('VHDLTestbench')[0].firstChild.data
            VerilogTestbench = commands_node.getElementsByTagName('VerilogTestbench')[0].firstChild.data

            self.commands = [VHDLHeader, VerilogHeader, VHDLModel, VerilogModel, VHDLTestbench, VerilogTestbench]

    def chatgpt_help_window(self):
        chatgpt_help_dialog = ChatGPTHelpDialog()
        chatgpt_help_dialog.exec_()

    def vhdl_header_command(self):
        vhdl_header = VHDLHeaderDialog("edit", self.commands[0])
        vhdl_header.exec_()

        if not vhdl_header.cancelled:
            vhdl_header = vhdl_header.get_data()
            self.commands[0] = vhdl_header
        self.save_data()

    def verilog_header_command(self):
        verilog_header = VerilogHeaderDialog("edit", self.commands[1])
        verilog_header.exec_()

        if not verilog_header.cancelled:
            verilog_header = verilog_header.get_data()
            self.commands[1] = verilog_header
        self.save_data()

    def vhdl_model_command(self):
        vhdl_model = VHDLModelDialog("edit", self.commands[2])
        vhdl_model.exec_()

        if not vhdl_model.cancelled:
            vhdl_model = vhdl_model.get_data()
            self.commands[2] = vhdl_model
        self.save_data()

    def verilog_model_command(self):
        verilog_model = VerilogModelDialog("edit", self.commands[3])
        verilog_model.exec_()

        if not verilog_model.cancelled:
            verilog_model = verilog_model.get_data()
            self.commands[3] = verilog_model
        self.save_data()

    def vhdl_testbench_command(self):
        vhdl_testbench = VHDLTestbenchDialog("edit", self.commands[4])
        vhdl_testbench.exec_()

        if not vhdl_testbench.cancelled:
            vhdl_testbench = vhdl_testbench.get_data()
            self.commands[4] = vhdl_testbench
        self.save_data()

    def verilog_testbench_command(self):
        verilog_testbench = VerilogTestbenchDialog("edit", self.commands[5])
        verilog_testbench.exec_()

        if not verilog_testbench.cancelled:
            verilog_testbench = verilog_testbench.get_data()
            self.commands[5] = verilog_testbench
        self.save_data()

    def header_VHDL_file(self):
        self.generator.generate_folders()
        self.generator.create_vhdl_file("4")
        proj_name = ProjectManager.get_proj_name()
        self.proj_path = os.path.join(ProjectManager.get_proj_dir(), proj_name)
        self.entity_name = ProjectManager.proj_name
        chatgpt_vhdl_file_path = os.path.join(self.proj_path, "VHDL", "ChatGPT",
                                              self.entity_name + "_VHDL_header_ChatGPT.txt")
        self.copy_file_contents_to_clipboard(chatgpt_vhdl_file_path)

    def header_Verilog_file(self):
        self.generator.generate_folders()
        self.generator.create_verilog_file("4")
        proj_name = ProjectManager.get_proj_name()
        self.proj_path = os.path.join(ProjectManager.get_proj_dir(), proj_name)
        self.entity_name = ProjectManager.proj_name
        chatgpt_verilog_file_path = os.path.join(self.proj_path, "Verilog", "ChatGPT",
                                                 self.entity_name + "_Verilog_header_ChatGPT.txt")
        self.copy_file_contents_to_clipboard(chatgpt_verilog_file_path)

    def model_VHDL_file(self):
        self.generator.generate_folders()
        self.generator.create_vhdl_file("6")
        proj_name = ProjectManager.get_proj_name()
        self.proj_path = os.path.join(ProjectManager.get_proj_dir(), proj_name)
        self.entity_name = ProjectManager.proj_name
        chatgpt_vhdl_file_path = os.path.join(self.proj_path, "VHDL", "ChatGPT", self.entity_name + "_VHDL_ChatGPT.txt")
        self.copy_file_contents_to_clipboard(chatgpt_vhdl_file_path)

    def model_Verilog_file(self):
        self.generator.generate_folders()
        self.generator.create_verilog_file("6")
        proj_name = ProjectManager.get_proj_name()
        self.proj_path = os.path.join(ProjectManager.get_proj_dir(), proj_name)
        self.entity_name = ProjectManager.proj_name
        chatgpt_verilog_file_path = os.path.join(self.proj_path, "Verilog", "ChatGPT",
                                                 self.entity_name + "_Verilog_ChatGPT.txt")
        self.copy_file_contents_to_clipboard(chatgpt_verilog_file_path)

    def tb_VHDL_file(self):
        self.generator.generate_folders()
        self.generator.create_testbench_file("8")
        proj_name = ProjectManager.get_proj_name()
        self.proj_path = os.path.join(ProjectManager.get_proj_dir(), proj_name)
        self.entity_name = ProjectManager.proj_name
        chatgpt_vhdl_file_path = os.path.join(self.proj_path, "VHDL", "ChatGPT",
                                              self.entity_name + "_VHDL_TB_ChatGPT.txt")
        self.copy_file_contents_to_clipboard(chatgpt_vhdl_file_path)

    def tb_Verilog_file(self):
        self.generator.generate_folders()
        self.generator.create_verilog_testbench_file("8")
        proj_name = ProjectManager.get_proj_name()
        self.proj_path = os.path.join(ProjectManager.get_proj_dir(), proj_name)
        self.entity_name = ProjectManager.proj_name
        chatgpt_verilog_file_path = os.path.join(self.proj_path, "Verilog", "ChatGPT",
                                                 self.entity_name + "_Verilog_TB_ChatGPT.txt")
        self.copy_file_contents_to_clipboard(chatgpt_verilog_file_path)

    def VHDLVisible(self):
        self.model_VHDL.setVisible(True)
        self.title_VHDL.setVisible(True)
        self.testbench_VHDL.setVisible(True)
        self.gen_label.setText("Generate VHDL")

        self.model_Verilog.setVisible(False)
        self.title_Verilog.setVisible(False)
        self.testbench_Verilog.setVisible(False)

    def VerilogVisible(self):
        self.model_Verilog.setVisible(True)
        self.title_Verilog.setVisible(True)
        self.testbench_Verilog.setVisible(True)
        self.gen_label.setText("Generate Verilog")

        self.model_VHDL.setVisible(False)
        self.title_VHDL.setVisible(False)
        self.testbench_VHDL.setVisible(False)

    def copy_file_contents_to_clipboard(self, file_path):
        try:
            with open(file_path, 'r') as file:
                file_contents = file.read()
                pyperclip.copy(file_contents)
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Alert")
                msgBox.setText("File contents copied to clipboard successfully")
                msgBox.exec_()
        except FileNotFoundError:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Alert")
            msgBox.setText("File not found. Press Generate button")
            msgBox.exec_()
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Alert")
            msgBox.setText("An error occurred. Check terminal for details")
            msgBox.exec_()
            print("An error occurred:", str(e))


    def open_model_folder(self):
        if self.model_VHDL.isVisible():
            path = self.proj_path+"/VHDL/model"
            self.open_file_explorer(path)
        elif self.model_Verilog.isVisible():
            path = self.proj_path+"/Verilog/model"
            self.open_file_explorer(path)

    def open_chatgpt_folder(self):
        if self.testbench_VHDL.isVisible():
            path = self.proj_path+"/VHDL/ChatGPT"
            self.open_file_explorer(path)
        elif self.testbench_Verilog.isVisible():
            path = self.proj_path+"/Verilog/ChatGPT"
            self.open_file_explorer(path)

    def open_testbench_folder(self):
        if self.testbench_VHDL.isVisible():
            path = self.proj_path+"/VHDL/testbench"
            self.open_file_explorer(path)
        elif self.testbench_Verilog.isVisible():
            path = self.proj_path+"/Verilog/testbench"
            self.open_file_explorer(path)


