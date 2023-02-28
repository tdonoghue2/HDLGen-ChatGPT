import os
import sys
from xml.dom import minidom
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import qtawesome as qta

sys.path.append("../..")
from ProjectManager.project_manager import ProjectManager
from HDLDesigner.Package.package_dialog import PackageDialog
from Generator.generator import Generator

BLACK_COLOR = "color: black"
WHITE_COLOR = "color: white"
ICONS_DIR = "../../Resources/icons/"
class Package(QWidget):

    def __init__(self):
        super().__init__()

        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        bold_font = QFont()
        bold_font.setBold(True)

        self.all_signals = []
        self.all_signals_names = []
        self.arrays = []
        self.arrays_names = []

        self.port_heading_layout = QHBoxLayout()
        self.package_action_layout = QVBoxLayout()
        self.package_list_layout = QVBoxLayout()
        self.package_list_title_layout = QHBoxLayout()

        self.mainLayout = QVBoxLayout()

        self.package_label = QLabel("mainPackage.vhd")
        self.package_label.setFont(title_font)
        self.package_label.setStyleSheet(WHITE_COLOR)

        self.add_btn = QPushButton("Add type")
        self.add_btn.setFixedSize(80, 25)
        self.add_btn.setStyleSheet(
            "QPushButton {background-color: white; color: black; border-radius: 8px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(250, 250, 250);  color: black; border-radius: 8px; border-style: plain;}")

        self.save_signal_btn = QPushButton("Save")
        self.save_signal_btn.setFixedSize(60, 30)
        self.save_signal_btn.setStyleSheet(
            "QPushButton {background-color: white; color: black; border-radius: 8px; border-style: plain; }"
            " QPushButton:pressed { background-color: rgb(250, 250, 250);  color: black; border-radius: 8px; border-style: plain;}")

        # Port list layout widgets
        self.name_label = QLabel("Name")
        self.name_label.setFont(bold_font)
        self.depth_label = QLabel("Depth")
        self.depth_label.setFont(bold_font)
        self.width_label = QLabel("Width")
        self.width_label.setFont(bold_font)
        self.type_label = QLabel("Type")
        self.type_label.setFont(bold_font)

        self.list_div = QFrame()
        self.list_div.setStyleSheet('.QFrame{background-color: rgb(97, 107, 129);}')
        self.list_div.setFixedHeight(1)

        self.package_table = QTableWidget()

        self.package_list_frame = QFrame()
        self.package_action_frame = QFrame()
        self.generator = Generator()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):

        # Port List section
        self.port_heading_layout.addWidget(self.package_label, alignment=Qt.AlignLeft)
        self.port_heading_layout.addWidget(self.add_btn, alignment=Qt.AlignRight)
        self.add_btn.clicked.connect(self.add_package)

        #self.name_label.setFixedWidth(50)
        #self.depth_label.setFixedWidth(40)
        #self.width_label.setFixedWidth(40)
        #self.type_label.setFixedWidth(100)

        self.package_list_title_layout.addWidget(self.name_label, alignment=Qt.AlignLeft)
        self.package_list_title_layout.addWidget(self.depth_label, alignment=Qt.AlignRight)
        self.package_list_title_layout.addWidget(self.width_label, alignment=Qt.AlignCenter)
        self.package_list_title_layout.addWidget(self.type_label, alignment=Qt.AlignCenter)
        self.package_list_title_layout.addSpacerItem(QSpacerItem(60, 1))
        self.package_list_title_layout.addSpacerItem(QSpacerItem(60, 1))

        self.package_list_layout.setAlignment(Qt.AlignTop)
        self.package_list_layout.addLayout(self.package_list_title_layout)
        self.package_list_layout.addWidget(self.list_div)

        self.package_table.setColumnCount(6)
        self.package_table.setShowGrid(False)
        self.package_table.setColumnWidth(0, 110)
        self.package_table.setColumnWidth(1, 10)
        self.package_table.setColumnWidth(2, 10)
        self.package_table.setColumnWidth(3, 100)
        self.package_table.setColumnWidth(4, 10)
        self.package_table.setColumnWidth(5, 10)
        self.package_table.horizontalScrollMode()
        self.package_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.package_table.horizontalScrollBar().hide()
        header = self.package_table.horizontalHeader()
        header.hide()
        header = self.package_table.verticalHeader()
        header.hide()
        self.package_table.setFrameStyle(QFrame.NoFrame)
        self.package_list_layout.addWidget(self.package_table)

        self.package_list_frame.setFrameShape(QFrame.StyledPanel)
        self.package_list_frame.setStyleSheet('.QFrame{background-color: white; border-radius: 5px;}')
        self.package_list_frame.setFixedSize(420, 300)  # 380, 295)
        self.package_list_frame.setLayout(self.package_list_layout)

        self.package_action_layout.addLayout(self.port_heading_layout)
        self.package_action_layout.addSpacerItem(QSpacerItem(0, 5))
        self.package_action_layout.addWidget(self.package_list_frame, alignment=Qt.AlignCenter)
        self.package_action_layout.addSpacerItem(QSpacerItem(0, 5))
        self.package_action_layout.addWidget(self.save_signal_btn, alignment=Qt.AlignRight)

        self.save_signal_btn.clicked.connect(self.save_signals)

        self.package_action_frame.setFrameShape(QFrame.StyledPanel)
        self.package_action_frame.setStyleSheet('.QFrame{background-color: rgb(97, 107, 129); border-radius: 5px;}')
        self.package_action_frame.setFixedSize(500, 400)  # 400, 400
        self.package_action_frame.setLayout(self.package_action_layout)

        self.mainLayout.addWidget(self.package_action_frame, alignment=Qt.AlignCenter)

        self.setLayout(self.mainLayout)


    def add_package(self):
        add_pack = PackageDialog("add")
        add_pack.exec_()
        if not add_pack.cancelled:
            print("adding package")
            array_data = add_pack.get_data()
            self.arrays.append(array_data)
            self.arrays_names.append((array_data[0]))
            delete_btn = QPushButton()
            delete_btn.setIcon(qta.icon("mdi.delete"))
            delete_btn.setFixedSize(35, 22)
            delete_btn.clicked.connect(self.delete_clicked)

            edit_btn = QPushButton()
            edit_btn.setIcon(qta.icon("mdi.pencil"))
            edit_btn.setFixedSize(35, 22)
            edit_btn.clicked.connect(self.edit_package)

            row_position = self.package_table.rowCount()
            self.package_table.insertRow(row_position)
            self.package_table.setRowHeight(row_position, 4)

            self.package_table.setItem(row_position, 0, QTableWidgetItem(array_data[0]))
            self.package_table.setItem(row_position, 1, QTableWidgetItem(array_data[1]))
            self.package_table.setItem(row_position, 2, QTableWidgetItem(array_data[2]))
            self.package_table.setItem(row_position, 3, QTableWidgetItem(array_data[3]))
            self.package_table.setCellWidget(row_position, 4, edit_btn)
            self.package_table.setCellWidget(row_position, 5, delete_btn)

    def edit_package(self):
        button = self.sender()
        if button:
            row = self.package_table.indexAt(button.pos()).row()
            add_pack = PackageDialog("edit", self.arrays[row])
            add_pack.exec_()

            if not add_pack.cancelled:
                array_data = add_pack.get_data()
                self.package_table.removeRow(row)
                self.arrays.pop(row)
                self.arrays_names.pop(row)

                delete_btn = QPushButton()
                delete_btn.setIcon(qta.icon("mdi.delete"))
                delete_btn.setFixedSize(35, 22)
                delete_btn.clicked.connect(self.delete_clicked)

                edit_btn = QPushButton()
                edit_btn.setIcon(qta.icon("mdi.pencil"))
                edit_btn.setFixedSize(35, 22)
                edit_btn.clicked.connect(self.edit_package)

                self.arrays.insert(row, array_data)
                self.arrays_names.insert(row, array_data[0])
                self.package_table.insertRow(row)
                self.package_table.setRowHeight(row, 5)

                self.package_table.setItem(row, 0, QTableWidgetItem(array_data[0]))
                self.package_table.setItem(row, 1, QTableWidgetItem(array_data[1]))
                self.package_table.setItem(row, 2, QTableWidgetItem(array_data[2]))
                self.package_table.setItem(row, 3, QTableWidgetItem(array_data[3]))
                self.package_table.setCellWidget(row, 4, edit_btn)
                self.package_table.setCellWidget(row, 5, delete_btn)

    def delete_clicked(self):
        button = self.sender()
        if button:
            row = self.package_table.indexAt(button.pos()).row()
            self.package_table.removeRow(row)
            self.arrays.pop(row)
            self.arrays_names.pop(row)

    def save_signals(self):
        mainPackageDir = os.getcwd() + "\HDLDesigner\Package\mainPackage.hdlgen"

        root = minidom.parse(mainPackageDir)
        HDLGen = root.documentElement
        hdlDesign = HDLGen.getElementsByTagName("hdlDesign")
        mainPackage = root.createElement("mainPackage")
        print(self.arrays)
        for array in self.arrays:
            array_node = root.createElement('array')

            name_node = root.createElement('name')
            name_node.appendChild(root.createTextNode(array[0]))
            array_node.appendChild(name_node)

            depth_node = root.createElement('depth')
            depth_node.appendChild(root.createTextNode(array[1]))
            array_node.appendChild(depth_node)

            width_node = root.createElement('width')
            width_node.appendChild(root.createTextNode(array[2]))
            array_node.appendChild(width_node)
            mainPackage.appendChild(array_node)

            sigType_node = root.createElement('signalType')
            sigType_node.appendChild(root.createTextNode(array[3]))
            array_node.appendChild(sigType_node)
            mainPackage.appendChild(array_node)
        hdlDesign[0].replaceChild(mainPackage, hdlDesign[0].getElementsByTagName('mainPackage')[0])

        # converting the doc into a string in xml format
        xml_str = root.toprettyxml()
        xml_str = os.linesep.join([s for s in xml_str.splitlines() if s.strip()])
        # Writing xml file
        with open(mainPackageDir, "w") as f:
            f.write(xml_str)
        self.generator.generate_mainPackage()

    def load_data(self):
        mainPackageDir = os.getcwd() + "\HDLDesigner\Package\mainPackage.hdlgen"
        root = minidom.parse(mainPackageDir)
        HDLGen = root.documentElement
        hdlDesign = HDLGen.getElementsByTagName("hdlDesign")
        mainPackage = hdlDesign[0].getElementsByTagName("mainPackage")

        array_nodes = mainPackage[0].getElementsByTagName('array')

        for i in range(0, len(array_nodes)):
            name = array_nodes[i].getElementsByTagName('name')[0].firstChild.data
            depth = array_nodes[i].getElementsByTagName('depth')[0].firstChild.data
            width = array_nodes[i].getElementsByTagName('width')[0].firstChild.data
            sigType = array_nodes[i].getElementsByTagName('signalType')[0].firstChild.data
            self.arrays_names.append(name)

            loaded_array_data = [
                name,
                depth,
                width,
                sigType
            ]

            delete_btn = QPushButton()
            delete_btn.setIcon(qta.icon("mdi.delete"))
            delete_btn.setFixedSize(35, 22)
            delete_btn.clicked.connect(self.delete_clicked)

            edit_btn = QPushButton()
            edit_btn.setIcon(qta.icon("mdi.pencil"))
            edit_btn.setFixedSize(35, 22)
            edit_btn.clicked.connect(self.edit_package)

            self.package_table.insertRow(i)
            self.package_table.setRowHeight(i, 5)

            self.package_table.setItem(i, 0, QTableWidgetItem(loaded_array_data[0]))
            self.package_table.setItem(i, 1, QTableWidgetItem(loaded_array_data[1]))
            self.package_table.setItem(i, 2, QTableWidgetItem(loaded_array_data[2]))
            self.package_table.setItem(i, 3, QTableWidgetItem(loaded_array_data[3]))
            self.package_table.setCellWidget(i, 4, edit_btn)
            self.package_table.setCellWidget(i, 5, delete_btn)
            self.arrays.append(loaded_array_data)