import os
import webbrowser
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLabel, QProgressBar, QMessageBox,
                             QSplitter, QTextEdit, QTabWidget, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

from core.api_client import ApiClient
from core.data_manager import DataManager
from core.utils import resource_path
from ui.detail_dialog import DetailDialog


class SearchThread(QThread):
    """搜索线程"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword
        self.api_client = ApiClient()

    def run(self):
        try:
            result = self.api_client.search_drama(self.keyword)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.api_client = ApiClient()
        self.search_thread = None
        self.current_dramas = []  # 存储当前搜索结果

        self.init_ui()
        self.setup_connections()
        self.set_window_icon()

    def set_window_icon(self):
        """设置窗口图标"""
        # 根据平台选择图标文件
        if sys.platform == "win32":
            # icon_path = resource_path("resources/icons/app.ico")
            icon_path = resource_path("resources/icons/API.ico")
        elif sys.platform == "darwin":
            # icon_path = resource_path("resources/icons/app.icns")
            icon_path = resource_path("resources/icons/API.icns")
        else:  # Linux和其他Unix系统
            # icon_path = resource_path("resources/icons/app.png")
            icon_path = resource_path("resources/icons/API.png")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("短剧搜索 - 桌面版 （API：https://api.kuleu.com/）")
        self.setGeometry(50, 100, 1600, 900)  # 窗口位置和大小，位置(50,100)，大小(1600x900)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 搜索区域
        search_group = self.create_search_group()
        main_layout.addWidget(search_group)

        # 结果区域
        self.results_table = self.create_results_table()
        main_layout.addWidget(self.results_table)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.statusBar().addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)

    def create_search_group(self):
        """创建搜索区域"""
        group = QGroupBox("搜索设置")
        layout = QHBoxLayout()

        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("请输入短剧名称")
        self.search_input.setMinimumHeight(35)
        self.search_input.returnPressed.connect(self.on_search)

        # 搜索按钮 - 带图标
        self.search_button = QPushButton(" 搜索")
        self.search_button.setMinimumHeight(35)
        self.search_button.setMinimumWidth(100)
        self.set_button_icon(self.search_button, "search.png")

        # 清空按钮 - 带图标
        self.clear_button = QPushButton(" 清空")
        self.clear_button.setMinimumHeight(35)
        self.clear_button.setMinimumWidth(80)
        self.set_button_icon(self.clear_button, "clear.png")

        layout.addWidget(self.search_input, 1)
        layout.addWidget(self.search_button)
        layout.addWidget(self.clear_button)

        group.setLayout(layout)
        return group

    def set_button_icon(self, button, icon_name):
        """为按钮设置图标"""
        icon_path = resource_path(f"resources/icons/{icon_name}")
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
        else:
            # 如果图标文件不存在，使用Qt内置图标
            if icon_name == "search.png":
                button.setIcon(self.style().standardIcon(
                    self.style().SP_FileDialogContentsView
                ))
            elif icon_name == "clear.png":
                button.setIcon(self.style().standardIcon(
                    self.style().SP_DialogCancelButton
                ))

    def create_results_table(self):
        """创建结果表格"""
        table = QTableWidget()
        # table.setColumnCount(4)
        table_columns_count = 4
        table.setColumnCount(table_columns_count)
        table.setHorizontalHeaderLabels(["短剧名称", "更新时间", "网盘链接", "操作"])

        # 设置表格属性
        # # table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        # table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        # table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        for i in range(table_columns_count):
            table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 设置表格样式
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                selection-background-color: #e6f3ff;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #e6f3ff;
            }
        """)

        return table

    def setup_connections(self):
        """设置信号连接"""
        self.search_button.clicked.connect(self.on_search)
        self.clear_button.clicked.connect(self.on_clear)

        # 新增：连接表格双击信号
        self.results_table.doubleClicked.connect(self.on_table_double_click)

    def on_table_double_click(self, index):
        """处理表格双击事件"""
        row = index.row()
        if 0 <= row < len(self.current_dramas):
            drama_data = self.current_dramas[row]
            # 显示详情对话框
            detail_dialog = DetailDialog(drama_data, self)
            detail_dialog.exec_()

    def on_search(self):
        """处理搜索事件"""
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "输入错误", "请输入搜索关键词")
            return

        # 禁用搜索按钮
        self.search_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"正在搜索: {keyword}")

        # 在新线程中执行搜索
        self.search_thread = SearchThread(keyword)
        self.search_thread.finished.connect(self.on_search_finished)
        self.search_thread.error.connect(self.on_search_error)
        self.search_thread.start()

    def on_search_finished(self, result):
        """搜索完成处理"""
        self.search_button.setEnabled(True)
        self.progress_bar.setVisible(False)

        if result.get("code") == 200:
            dramas = result.get("data", [])
            self.current_dramas = dramas  # 保存当前搜索结果
            self.display_results(dramas)
            self.status_label.setText(f"搜索完成，找到 {len(dramas)} 个结果")
        else:
            error_msg = result.get("msg", "搜索失败")
            QMessageBox.critical(self, "搜索错误", error_msg)
            self.status_label.setText("搜索失败")

    def on_search_error(self, error_msg):
        """搜索错误处理"""
        self.search_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "网络错误", f"搜索过程中发生错误:\n{error_msg}")
        self.status_label.setText("搜索错误")

    def display_results(self, dramas):
        """显示搜索结果"""
        self.results_table.setRowCount(0)  # 清空表格

        for row, drama in enumerate(dramas):
            self.results_table.insertRow(row)

            # 短剧名称
            name_item = QTableWidgetItem(drama.get("name", ""))
            name_item.setToolTip(drama.get("name", ""))  # 添加提示
            self.results_table.setItem(row, 0, name_item)

            # 更新时间
            time_item = QTableWidgetItem(drama.get("addtime", ""))
            self.results_table.setItem(row, 1, time_item)

            # 网盘链接
            link_item = QTableWidgetItem(drama.get("viewlink", ""))
            link_item.setToolTip(drama.get("viewlink", ""))  # 添加提示
            self.results_table.setItem(row, 2, link_item)

            # 操作按钮 - 带图标
            open_button = QPushButton(" 打开链接")
            self.set_button_icon(open_button, "link.png")
            open_button.clicked.connect(lambda checked, link=drama.get("viewlink"):
                                        self.open_link(link))
            self.results_table.setCellWidget(row, 3, open_button)

    def open_link(self, link):
        """打开链接"""
        if link:
            try:
                webbrowser.open(link)
                self.status_label.setText("正在打开链接...")
            except Exception as e:
                QMessageBox.warning(self, "打开失败", f"无法打开链接:\n{str(e)}")

    def on_clear(self):
        """清空搜索和结果"""
        self.search_input.clear()
        self.results_table.setRowCount(0)
        self.current_dramas = []  # 清空当前搜索结果
        self.status_label.setText("就绪")
