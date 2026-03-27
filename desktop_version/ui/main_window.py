import os
import sys

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QToolButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QMessageBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
    QPropertyAnimation,
    QEasingCurve,
    QSize,
)
from PyQt5.QtGui import QFont, QColor, QCursor
from core.api_client import ApiClient, RESOURCE_TYPE_MAP
from ui.detail_dialog import DetailDialog
from typing import Dict, Any, List

# 导入 resource_path
from core.utils import resource_path


class SearchThread(QThread):
    """后台搜索线程"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(
        self,
        api_client: ApiClient,
        search_type: str,
        keyword: str = "",
        sub_type: str = "quark",
    ):
        super().__init__()
        self.api_client = api_client
        self.search_type = search_type
        self.keyword = keyword
        self.sub_type = sub_type

    def run(self):
        try:
            result: Dict[str, Any] = {}

            if self.search_type == "短剧搜索":
                result = self.api_client.search_drama(self.keyword, "短剧搜索")
            elif self.search_type == "百度短剧":
                result = self.api_client.search_drama(self.keyword, "百度短剧")
            elif self.search_type == "聚合资源搜索":
                result = self.api_client.search_aggregate(self.keyword, self.sub_type)
            elif self.search_type == "每日影视资源":
                result = self.api_client.get_daily_resources()
            elif self.search_type == "短剧热度榜":
                result = self.api_client.get_drama_rank()
            elif self.search_type == "夸克热搜":
                result = self.api_client.get_quark_hot("短剧")

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class ModernButton(QPushButton):
    """现代化按钮控件"""

    def __init__(self, text="", icon="", parent=None, button_type="primary"):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # 设置字体
        font = QFont("Microsoft YaHei", 15, QFont.Bold)
        self.setFont(font)

        # 根据类型设置样式
        self.apply_style()

        # 添加阴影效果
        self.add_shadow()

    def apply_style(self):
        """应用样式"""
        styles = {
            "primary": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 30px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #7c8ff0, stop:1 #8b5fb8);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5a6fd6, stop:1 #6548a0);
                }
                QPushButton:disabled {
                    background: rgba(255, 255, 255, 0.1);
                    color: rgba(255, 255, 255, 0.3);
                }
            """,
            "success": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2ecc71, stop:1 #27ae60);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 30px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #58d68d, stop:1 #2ecc71);
                }
            """,
            "secondary": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #34495e, stop:1 #2c3e50);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 30px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4a6074, stop:1 #3d5266);
                }
            """,
        }
        self.setStyleSheet(styles.get(self.button_type, styles["primary"]))

    def add_shadow(self):
        """添加阴影效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(102, 126, 234, 150))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class ModernComboBox(QComboBox):
    """现代化下拉框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # 设置字体
        font = QFont("Microsoft YaHei", 14)
        self.setFont(font)

        # 设置样式
        self.setStyleSheet(
            """
            QComboBox {
                background-color: rgba(255, 255, 255, 0.08);
                border: 2px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 10px 15px;
                color: #FFFFFF;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 2px solid rgba(102, 126, 234, 0.6);
                background-color: rgba(255, 255, 255, 0.12);
            }
            QComboBox:on {
                border: 2px solid #667eea;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #667eea;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e3a5f;
                border: 2px solid #667eea;
                border-radius: 8px;
                selection-background-color: #667eea;
                selection-color: white;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                height: 35px;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: rgba(102, 126, 234, 0.3);
            }
        """
        )


class ModernLineEdit(QLineEdit):
    """现代化输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置字体
        font = QFont("Microsoft YaHei", 14)
        self.setFont(font)

        # 设置样式
        self.setStyleSheet(
            """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                padding: 12px 18px;
                color: #FFFFFF;
                font-size: 14px;
                selection-background-color: #667eea;
            }
            QLineEdit:hover {
                border: 2px solid rgba(102, 126, 234, 0.5);
                background-color: rgba(255, 255, 255, 0.08);
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background-color: rgba(255, 255, 255, 0.1);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.4);
            }
        """
        )


class MainWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.api_client = ApiClient()

        self.current_type = "短剧搜索"
        self.current_sub_type = "quark"
        self.current_results: List[Dict] = []

        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🎬 短剧 / 影视资源 · 聚合搜索")
        self.resize(1400, 900)

        # # 设置窗口图标
        # self.setWindowIcon(
        #     self.style().standardIcon(self.style().SP_FileDialogContentsView)
        # )
        # 根据操作系统选择图标文件
        if sys.platform == "win32":
            icon_name = "API.ico"
        elif sys.platform == "darwin":  # macOS
            icon_name = "API.icns"
        else:  # Linux 等
            icon_name = "API.png"

        # 获取图标路径
        icon_path = resource_path(f"resources/icons/{icon_name}")

        # 设置窗口图标
        if os.path.exists(icon_path):
            from PyQt5.QtGui import QIcon

            self.setWindowIcon(QIcon(icon_path))
        else:
            # 如果找不到图标，打印警告（可选）
            print(f"⚠️ 主窗口：图标文件未找到: {icon_path}")

        # 中央部件
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)

        # 标题区域
        self.setup_title(main_layout)

        # 搜索控制区
        self.setup_search_controls(main_layout)

        # 状态提示
        self.setup_status_label(main_layout)

        # 结果表格
        self.setup_results_table(main_layout)

        # 底部信息
        self.setup_footer(main_layout)

        # 状态栏
        self.statusBar().showMessage("✨ 准备就绪")

        # 应用入场动画
        self.apply_entrance_animation()

    def setup_title(self, parent_layout: QVBoxLayout):
        """设置标题区域"""
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setSpacing(10)

        # 主标题
        title_label = QLabel("🎬 短剧 / 影视资源 · 聚合搜索")
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet(
            """
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #FFFFFF;
                padding: 10px;
            }
        """
        )
        title_label.setAlignment(Qt.AlignCenter)

        # 副标题
        subtitle_label = QLabel(
            "基于酷乐 API 聚合资源搜索接口 · 支持多种网盘与磁力链接"
        )
        subtitle_label.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                color: rgba(255, 255, 255, 0.6);
                padding: 5px;
            }
        """
        )
        subtitle_label.setAlignment(Qt.AlignCenter)

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        parent_layout.addWidget(title_frame)

    def setup_search_controls(self, parent_layout: QVBoxLayout):
        """设置搜索控制区"""
        control_frame = QFrame()
        control_frame.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 0.03);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
            }
        """
        )

        control_layout = QHBoxLayout(control_frame)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(25, 20, 25, 20)

        # 功能类型选择
        type_label = QLabel("功能类型:")
        type_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-weight: bold;")
        self.type_combo = ModernComboBox()
        self.type_combo.addItems(
            [
                "短剧搜索",
                "百度短剧",
                "聚合资源搜索",
                "每日影视资源",
                "短剧热度榜",
                "夸克热搜",
            ]
        )
        self.type_combo.currentTextChanged.connect(self.on_type_changed)

        # 子类型选择（聚合资源专用）
        self.sub_type_label = QLabel("资源类型:")
        self.sub_type_label.setStyleSheet(
            "color: rgba(255, 255, 255, 0.8); font-weight: bold;"
        )
        self.sub_type_combo = ModernComboBox()
        self.sub_type_combo.addItems(list(RESOURCE_TYPE_MAP.keys()))
        self.sub_type_combo.currentTextChanged.connect(self.on_sub_type_changed)
        self.sub_type_label.hide()
        self.sub_type_combo.hide()

        # 搜索输入框
        self.search_input = ModernLineEdit()
        self.search_input.setPlaceholderText(
            "🔍 请输入关键词（多个关键词可用空格分隔）"
        )
        self.search_input.returnPressed.connect(self.start_search)

        # 搜索按钮
        self.search_btn = ModernButton("🔍  开始搜索", button_type="primary")
        self.search_btn.clicked.connect(self.start_search)

        # 加载按钮（榜单类专用）
        self.load_btn = ModernButton("📥  加载数据", button_type="success")
        self.load_btn.clicked.connect(self.start_search)
        self.load_btn.hide()

        # 添加到布局
        control_layout.addWidget(type_label)
        control_layout.addWidget(self.type_combo)
        control_layout.addWidget(self.sub_type_label)
        control_layout.addWidget(self.sub_type_combo)
        control_layout.addWidget(self.search_input, 1)
        control_layout.addWidget(self.search_btn)
        control_layout.addWidget(self.load_btn)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(102, 126, 234, 100))
        shadow.setOffset(0, 5)
        control_frame.setGraphicsEffect(shadow)

        parent_layout.addWidget(control_frame)

    def setup_status_label(self, parent_layout: QVBoxLayout):
        """设置状态提示标签"""
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.hide()
        parent_layout.addWidget(self.status_label)

    def setup_results_table(self, parent_layout: QVBoxLayout):
        """设置结果表格"""
        table_frame = QFrame()
        table_frame.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 0.03);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
        """
        )

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(10, 10, 10, 10)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["名称", "更新时间", "热度/来源", "操作"])

        # 设置表头样式
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        # ==================== 关键修改：增加操作列宽度 ====================
        header.resizeSection(3, 150)  # 从 120 改为 150，确保按钮有足够空间显示

        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self.show_detail)

        # 设置行高
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.verticalHeader().setVisible(False)

        table_layout.addWidget(self.table)
        parent_layout.addWidget(table_frame, 1)

    def setup_footer(self, parent_layout: QVBoxLayout):
        """设置底部信息"""
        footer_label = QLabel("已适配酷乐聚合资源搜索接口所有网盘类型与磁力/电驴链接")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet(
            """
            QLabel {
                color: rgba(255, 255, 255, 0.4);
                font-size: 12px;
                padding: 10px;
            }
        """
        )
        parent_layout.addWidget(footer_label)

    def apply_entrance_animation(self):
        """应用入场动画"""
        # 窗口透明度动画
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def on_type_changed(self, text: str):
        """功能类型改变"""
        self.current_type = text
        self.clear_results()

        # 判断是否为榜单类
        is_rank = text in ("每日影视资源", "短剧热度榜", "夸克热搜")

        # 切换UI（带淡入淡出效果）
        self.search_input.setVisible(not is_rank)
        self.search_btn.setVisible(not is_rank)
        self.load_btn.setVisible(is_rank)

        # 显示/隐藏子类型选择
        if text == "聚合资源搜索":
            self.sub_type_label.show()
            self.sub_type_combo.show()
        else:
            self.sub_type_label.hide()
            self.sub_type_combo.hide()

    def on_sub_type_changed(self, text: str):
        """子类型改变"""
        self.current_sub_type = RESOURCE_TYPE_MAP.get(text, "quark")

    def start_search(self):
        """开始搜索"""
        keyword = self.search_input.text().strip()

        # 验证输入
        if self.current_type not in ("每日影视资源", "短剧热度榜", "夸克热搜"):
            if not keyword:
                QMessageBox.warning(self, "提示", "⚠️ 请输入搜索关键词")
                return

        # 显示加载状态
        self.show_loading_status()

        # 创建搜索线程
        self.search_thread = SearchThread(
            self.api_client, self.current_type, keyword, self.current_sub_type
        )
        self.search_thread.finished.connect(self.handle_search_result)
        self.search_thread.error.connect(self.handle_search_error)
        self.search_thread.start()

        # 禁用按钮
        self.search_btn.setEnabled(False)
        self.load_btn.setEnabled(False)

    def show_loading_status(self):
        """显示加载状态"""
        self.status_label.setText("⏳ 正在获取数据，请稍候...")
        self.status_label.setStyleSheet(
            """
            QLabel {
                padding: 15px 25px;
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f39c12, stop:1 #e67e22);
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """
        )
        self.status_label.show()

    def handle_search_result(self, result: Dict[str, Any]):
        """处理搜索结果"""
        # 恢复按钮状态
        self.search_btn.setEnabled(True)
        self.load_btn.setEnabled(True)

        code = result.get("code", 500)

        if code == 200:
            data = result.get("data", [])
            count = result.get("count", len(data))

            # 显示成功状态
            self.status_label.setText(f"✅ 成功获取 {count} 条结果")
            self.status_label.setStyleSheet(
                """
                QLabel {
                    padding: 15px 25px;
                    border-radius: 10px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2ecc71, stop:1 #27ae60);
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
            """
            )
            self.status_label.show()

            # 更新表格
            self.update_table(data)

            # 保存到数据管理器
            self.save_results(data)

        else:
            msg = result.get("msg", "未知错误")
            self.status_label.setText(f"❌ 失败: {msg}")
            self.status_label.setStyleSheet(
                """
                QLabel {
                    padding: 15px 25px;
                    border-radius: 10px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #e74c3c, stop:1 #c0392b);
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
            """
            )
            self.status_label.show()

    def handle_search_error(self, error_msg: str):
        """处理搜索错误"""
        self.search_btn.setEnabled(True)
        self.load_btn.setEnabled(True)

        self.status_label.setText(f"❌ 错误: {error_msg}")
        self.status_label.setStyleSheet(
            """
            QLabel {
                padding: 15px 25px;
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """
        )
        self.status_label.show()

    def update_table(self, data: List[Dict]):
        """更新表格内容"""
        self.current_results = data
        self.table.setRowCount(len(data))

        for row, item in enumerate(data):
            # 名称列
            name = (
                item.get("name")
                or item.get("content_title")
                or item.get("title", "未知")
            )
            name_item = QTableWidgetItem(name)
            name_item.setForeground(QColor(255, 255, 255))
            # self.table.setItem(row, 0, name_item)
            # # ==================== 设置表格项字体 ====================
            # font = QFont("Microsoft YaHei", 12)  # 设置表格字体为 12px
            # name_item.setFont(font)
            self.table.setItem(row, 0, name_item)

            # 时间列
            time_str = item.get("addtime", "")
            time_item = QTableWidgetItem(time_str)
            time_item.setForeground(QColor(200, 200, 200))
            # time_item.setFont(font)  # 设置字体
            self.table.setItem(row, 1, time_item)

            # 热度/来源列
            hot_or_source = (
                item.get("hot") or item.get("source") or item.get("hots", "")
            )
            hot_item = QTableWidgetItem(str(hot_or_source))
            hot_item.setForeground(QColor(102, 126, 234))
            # hot_item.setFont(font)  # 设置字体
            self.table.setItem(row, 2, hot_item)

            # 操作按钮
            viewlink = item.get("viewlink") or item.get("url") or item.get("link", "")
            if viewlink:
                # btn = ModernButton("🔗 打开链接", button_type="success")
                # btn.setCursor(QCursor(Qt.PointingHandCursor))
                # btn.clicked.connect(lambda checked, link=viewlink: self.open_link(link))
                # self.table.setCellWidget(row, 3, btn)
                # # ==================== 直接使用 QPushButton，并设置字体和样式 ====================
                # # 1. 直接使用 QPushButton，不使用 ModernButton
                # btn = QPushButton("🔗 打开链接")
                # # 2. 明确设置字体（关键！）
                # btn_font = QFont("Microsoft YaHei", 11, QFont.Bold)
                # btn_font.setStyleHint(QFont.SansSerif)
                # btn.setFont(btn_font)
                # # 3. 在样式表中指定字体（关键！）
                # btn.setStyleSheet(
                #     """
                #     QPushButton {
                #         background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                #             stop:0 #2ecc71, stop:1 #27ae60);
                #         color: white;
                #         border: none;
                #         border-radius: 6px;
                #         padding: 6px 12px;
                #         font-weight: bold;
                #         font-family: "Microsoft YaHei", "SimHei", sans-serif;  /* 关键！ */
                #         font-size: 11px;
                #     }
                #     QPushButton:hover {
                #         background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                #             stop:0 #58d68d, stop:1 #2ecc71);
                #     }
                # """
                # )
                # # 4. 设置固定大小（关键！）
                # btn.setFixedSize(120, 40)
                # # 5. 设置光标
                # btn.setCursor(QCursor(Qt.PointingHandCursor))
                # # 6. 绑定事件
                # btn.clicked.connect(lambda checked, link=viewlink: self.open_link(link))
                # ===================== 直接使用 QToolButton，并设置字体和样式 =====================
                btn = QToolButton()
                btn.setText("🔗 打开链接 ")
                btn_font = QFont("Microsoft YaHei", 12, QFont.Bold)
                btn.setFont(btn_font)
                btn.setStyleSheet(
                    """
                    QToolButton {
                        background-color: #2ecc71;
                        color: white;
                        border: 2px solid #27ae60;
                        border-radius: 5px;
                        padding: 4px 8px;          /* 减小左右内边距：从 10px 改为 8px */
                        font-weight: bold;
                        font-family: "Microsoft YaHei", sans-serif;
                    }
                    QToolButton:hover {
                        background-color: #58d68d;
                        border: 2px solid #2ecc71;
                    }
                    QToolButton:pressed {
                        background-color: #27ae60;
                    }
                """
                )
                btn.setCursor(QCursor(Qt.PointingHandCursor))
                btn.clicked.connect(lambda checked, link=viewlink: self.open_link(link))
                self.table.setCellWidget(row, 3, btn)
            else:
                no_link_item = QTableWidgetItem("-")
                no_link_item.setForeground(QColor(150, 150, 150))
                self.table.setItem(row, 3, no_link_item)

    def open_link(self, link: str):
        """打开链接"""
        from PyQt5.QtGui import QDesktopServices
        from PyQt5.QtCore import QUrl

        QDesktopServices.openUrl(QUrl(link))

    def show_detail(self, index):
        """显示详情"""
        if not self.current_results:
            return

        row = index.row()
        if 0 <= row < len(self.current_results):
            data = self.current_results[row]
            link = data.get("viewlink") or data.get("url") or data.get("link", "")

            dialog = DetailDialog(data, link, self)
            dialog.exec_()

    def clear_results(self):
        """清空结果"""
        self.table.setRowCount(0)
        self.status_label.hide()

    def save_results(self, data: List[Dict]):
        """保存结果到数据管理器"""
        if hasattr(self.data_manager, "cache_results"):
            key = f"{self.current_type}_{self.search_input.text()}_{self.current_sub_type}"
            self.data_manager.cache_results(key, data)
