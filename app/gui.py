import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QTableWidget, QTableWidgetItem, QFrame, QGridLayout,
                            QStatusBar, QTabWidget, QLineEdit, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFont
import pyqtgraph as pg
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import logging

class TradingGUI(QMainWindow):
    def __init__(self, config: dict):
        """Initialize the main trading interface"""
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.init_ui()
        self.setup_styles()
        self.setup_timers()

    def init_ui(self):
        """Initialize the user interface"""
        try:
            self.setWindowTitle('NOX-X Professional Trading System')
            self.setGeometry(100, 100, 1600, 900)

            # Create main widget and layout
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QHBoxLayout(main_widget)

            # Create left sidebar
            self.create_left_sidebar(main_layout)

            # Create center panel
            self.create_center_panel(main_layout)

            # Create right sidebar
            self.create_right_sidebar(main_layout)

            # Create status bar
            self.create_status_bar()

        except Exception as e:
            self.logger.error(f"Error initializing UI: {str(e)}")
            raise

    def setup_styles(self):
        """Set up dark theme and professional styling"""
        try:
            # Set dark theme palette
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)

            QApplication.setPalette(palette)

            # Set stylesheet for widgets
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #353535;
                }
                QWidget {
                    background-color: #353535;
                    color: white;
                }
                QPushButton {
                    background-color: #2a82da;
                    border: none;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3292ea;
                }
                QPushButton:pressed {
                    background-color: #1a72ca;
                }
                QTableWidget {
                    gridline-color: #2a2a2a;
                    background-color: #252525;
                    border: 1px solid #2a2a2a;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QHeaderView::section {
                    background-color: #2a2a2a;
                    padding: 5px;
                    border: 1px solid #3a3a3a;
                    font-weight: bold;
                }
                QComboBox {
                    background-color: #252525;
                    border: 1px solid #2a2a2a;
                    border-radius: 3px;
                    padding: 5px;
                }
                QLabel {
                    color: white;
                }
                QLineEdit {
                    background-color: #252525;
                    border: 1px solid #2a2a2a;
                    border-radius: 3px;
                    padding: 5px;
                }
                QProgressBar {
                    border: 1px solid #2a2a2a;
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #2a82da;
                }
            """)

        except Exception as e:
            self.logger.error(f"Error setting up styles: {str(e)}")

    def create_left_sidebar(self, main_layout: QHBoxLayout):
        """Create the left sidebar with controls and settings"""
        try:
            left_sidebar = QFrame()
            left_sidebar.setMaximumWidth(300)
            left_sidebar.setFrameStyle(QFrame.StyledPanel)
            left_layout = QVBoxLayout(left_sidebar)

            # Account Info Section
            account_group = self.create_account_info_group()
            left_layout.addWidget(account_group)

            # Trading Controls
            controls_group = self.create_trading_controls_group()
            left_layout.addWidget(controls_group)

            # Settings
            settings_group = self.create_settings_group()
            left_layout.addWidget(settings_group)

            left_layout.addStretch()
            main_layout.addWidget(left_sidebar)

        except Exception as e:
            self.logger.error(f"Error creating left sidebar: {str(e)}")

    def create_center_panel(self, main_layout: QHBoxLayout):
        """Create the center panel with charts and trading information"""
        try:
            center_panel = QFrame()
            center_layout = QVBoxLayout(center_panel)

            # Chart Area
            chart_group = self.create_chart_group()
            center_layout.addWidget(chart_group)

            # Trading Information Tabs
            info_tabs = self.create_info_tabs()
            center_layout.addWidget(info_tabs)

            main_layout.addWidget(center_panel, stretch=2)

        except Exception as e:
            self.logger.error(f"Error creating center panel: {str(e)}")

    def create_right_sidebar(self, main_layout: QHBoxLayout):
        """Create the right sidebar with signals and performance metrics"""
        try:
            right_sidebar = QFrame()
            right_sidebar.setMaximumWidth(300)
            right_sidebar.setFrameStyle(QFrame.StyledPanel)
            right_layout = QVBoxLayout(right_sidebar)

            # Signals Panel
            signals_group = self.create_signals_group()
            right_layout.addWidget(signals_group)

            # Performance Metrics
            metrics_group = self.create_metrics_group()
            right_layout.addWidget(metrics_group)

            right_layout.addStretch()
            main_layout.addWidget(right_sidebar)

        except Exception as e:
            self.logger.error(f"Error creating right sidebar: {str(e)}")

    def create_account_info_group(self) -> QFrame:
        """Create account information group"""
        try:
            group = QFrame()
            group.setFrameStyle(QFrame.StyledPanel)
            layout = QVBoxLayout(group)

            layout.addWidget(QLabel('Account Information'))
            
            # Account details
            self.balance_label = QLabel('Balance: $0.00')
            self.equity_label = QLabel('Equity: $0.00')
            self.profit_label = QLabel('Profit: $0.00')
            
            layout.addWidget(self.balance_label)
            layout.addWidget(self.equity_label)
            layout.addWidget(self.profit_label)

            return group

        except Exception as e:
            self.logger.error(f"Error creating account info group: {str(e)}")
            return QFrame()

    def create_trading_controls_group(self) -> QFrame:
        """Create trading controls group"""
        try:
            group = QFrame()
            group.setFrameStyle(QFrame.StyledPanel)
            layout = QVBoxLayout(group)

            layout.addWidget(QLabel('Trading Controls'))

            # Symbol selection
            self.symbol_combo = QComboBox()
            self.symbol_combo.addItems(['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD'])
            layout.addWidget(self.symbol_combo)

            # Timeframe selection
            self.timeframe_combo = QComboBox()
            self.timeframe_combo.addItems(['M1', 'M5', 'M15', 'H1', 'H4', 'D1'])
            layout.addWidget(self.timeframe_combo)

            # Trading mode
            self.auto_trading_btn = QPushButton('Enable Auto Trading')
            self.auto_trading_btn.setCheckable(True)
            layout.addWidget(self.auto_trading_btn)

            return group

        except Exception as e:
            self.logger.error(f"Error creating trading controls group: {str(e)}")
            return QFrame()

    def create_settings_group(self) -> QFrame:
        """Create settings group"""
        try:
            group = QFrame()
            group.setFrameStyle(QFrame.StyledPanel)
            layout = QVBoxLayout(group)

            layout.addWidget(QLabel('Settings'))

            # Risk settings
            risk_layout = QGridLayout()
            risk_layout.addWidget(QLabel('Risk %:'), 0, 0)
            self.risk_input = QLineEdit('2.0')
            risk_layout.addWidget(self.risk_input, 0, 1)

            layout.addLayout(risk_layout)

            # AI Model settings
            self.ai_enabled_btn = QPushButton('Enable AI')
            self.ai_enabled_btn.setCheckable(True)
            layout.addWidget(self.ai_enabled_btn)

            return group

        except Exception as e:
            self.logger.error(f"Error creating settings group: {str(e)}")
            return QFrame()

    def create_chart_group(self) -> QFrame:
        """Create chart group with price and indicator charts"""
        try:
            group = QFrame()
            group.setFrameStyle(QFrame.StyledPanel)
            layout = QVBoxLayout(group)

            # Create price chart
            self.price_chart = pg.PlotWidget()
            self.price_chart.setBackground('black')
            self.price_chart.showGrid(x=True, y=True)
            layout.addWidget(self.price_chart)

            # Create indicator charts
            self.indicator_chart = pg.PlotWidget()
            self.indicator_chart.setBackground('black')
            self.indicator_chart.showGrid(x=True, y=True)
            layout.addWidget(self.indicator_chart)

            return group

        except Exception as e:
            self.logger.error(f"Error creating chart group: {str(e)}")
            return QFrame()

    def create_info_tabs(self) -> QTabWidget:
        """Create information tabs"""
        try:
            tabs = QTabWidget()

            # Trades tab
            trades_tab = QWidget()
            trades_layout = QVBoxLayout(trades_tab)
            self.trades_table = QTableWidget()
            self.trades_table.setColumnCount(7)
            self.trades_table.setHorizontalHeaderLabels([
                'Ticket', 'Symbol', 'Type', 'Volume',
                'Open Price', 'Current Price', 'Profit'
            ])
            trades_layout.addWidget(self.trades_table)
            tabs.addTab(trades_tab, 'Open Trades')

            # History tab
            history_tab = QWidget()
            history_layout = QVBoxLayout(history_tab)
            self.history_table = QTableWidget()
            self.history_table.setColumnCount(8)
            self.history_table.setHorizontalHeaderLabels([
                'Ticket', 'Symbol', 'Type', 'Volume',
                'Open Price', 'Close Price', 'Profit', 'Close Time'
            ])
            history_layout.addWidget(self.history_table)
            tabs.addTab(history_tab, 'Trade History')

            # Logs tab
            logs_tab = QWidget()
            logs_layout = QVBoxLayout(logs_tab)
            self.log_table = QTableWidget()
            self.log_table.setColumnCount(4)
            self.log_table.setHorizontalHeaderLabels([
                'Time', 'Level', 'Module', 'Message'
            ])
            logs_layout.addWidget(self.log_table)
            tabs.addTab(logs_tab, 'Logs')

            return tabs

        except Exception as e:
            self.logger.error(f"Error creating info tabs: {str(e)}")
            return QTabWidget()

    def create_signals_group(self) -> QFrame:
        """Create trading signals group"""
        try:
            group = QFrame()
            group.setFrameStyle(QFrame.StyledPanel)
            layout = QVBoxLayout(group)

            layout.addWidget(QLabel('Trading Signals'))

            self.signals_table = QTableWidget()
            self.signals_table.setColumnCount(4)
            self.signals_table.setHorizontalHeaderLabels([
                'Time', 'Symbol', 'Type', 'Confidence'
            ])
            layout.addWidget(self.signals_table)

            return group

        except Exception as e:
            self.logger.error(f"Error creating signals group: {str(e)}")
            return QFrame()

    def create_metrics_group(self) -> QFrame:
        """Create performance metrics group"""
        try:
            group = QFrame()
            group.setFrameStyle(QFrame.StyledPanel)
            layout = QVBoxLayout(group)

            layout.addWidget(QLabel('Performance Metrics'))

            # Add metrics
            self.win_rate_label = QLabel('Win Rate: 0.00%')
            self.profit_factor_label = QLabel('Profit Factor: 0.00')
            self.sharp_ratio_label = QLabel('Sharp Ratio: 0.00')
            
            layout.addWidget(self.win_rate_label)
            layout.addWidget(self.profit_factor_label)
            layout.addWidget(self.sharp_ratio_label)

            # Add AI model performance
            layout.addWidget(QLabel('AI Model Performance'))
            self.ai_accuracy_progress = QProgressBar()
            self.ai_accuracy_progress.setMaximum(100)
            layout.addWidget(self.ai_accuracy_progress)

            return group

        except Exception as e:
            self.logger.error(f"Error creating metrics group: {str(e)}")
            return QFrame()

    def create_status_bar(self):
        """Create status bar"""
        try:
            status_bar = QStatusBar()
            self.setStatusBar(status_bar)

            # Add status indicators
            self.mt5_status_label = QLabel('MT5: Disconnected')
            self.ai_status_label = QLabel('AI: Inactive')
            self.last_update_label = QLabel('Last Update: Never')

            status_bar.addPermanentWidget(self.mt5_status_label)
            status_bar.addPermanentWidget(self.ai_status_label)
            status_bar.addPermanentWidget(self.last_update_label)

        except Exception as e:
            self.logger.error(f"Error creating status bar: {str(e)}")

    def setup_timers(self):
        """Set up update timers"""
        try:
            # Timer for updating market data
            self.market_timer = QTimer()
            self.market_timer.timeout.connect(self.update_market_data)
            self.market_timer.start(1000)  # Update every second

            # Timer for updating account info
            self.account_timer = QTimer()
            self.account_timer.timeout.connect(self.update_account_info)
            self.account_timer.start(5000)  # Update every 5 seconds

        except Exception as e:
            self.logger.error(f"Error setting up timers: {str(e)}")

    def update_market_data(self):
        """Update market data and charts"""
        try:
            # This method will be implemented to update with real data
            pass
        except Exception as e:
            self.logger.error(f"Error updating market data: {str(e)}")

    def update_account_info(self):
        """Update account information"""
        try:
            # This method will be implemented to update with real data
            pass
        except Exception as e:
            self.logger.error(f"Error updating account info: {str(e)}")

    def update_trades_table(self, trades: List[Dict]):
        """Update open trades table"""
        try:
            self.trades_table.setRowCount(len(trades))
            for i, trade in enumerate(trades):
                self.trades_table.setItem(i, 0, QTableWidgetItem(str(trade['ticket'])))
                self.trades_table.setItem(i, 1, QTableWidgetItem(trade['symbol']))
                self.trades_table.setItem(i, 2, QTableWidgetItem(trade['type']))
                self.trades_table.setItem(i, 3, QTableWidgetItem(str(trade['volume'])))
                self.trades_table.setItem(i, 4, QTableWidgetItem(str(trade['open_price'])))
                self.trades_table.setItem(i, 5, QTableWidgetItem(str(trade['current_price'])))
                self.trades_table.setItem(i, 6, QTableWidgetItem(str(trade['profit'])))

        except Exception as e:
            self.logger.error(f"Error updating trades table: {str(e)}")

    def update_signals_table(self, signals: List[Dict]):
        """Update trading signals table"""
        try:
            self.signals_table.setRowCount(len(signals))
            for i, signal in enumerate(signals):
                self.signals_table.setItem(i, 0, QTableWidgetItem(signal['time']))
                self.signals_table.setItem(i, 1, QTableWidgetItem(signal['symbol']))
                self.signals_table.setItem(i, 2, QTableWidgetItem(signal['type']))
                self.signals_table.setItem(i, 3, QTableWidgetItem(f"{signal['confidence']:.2f}"))

        except Exception as e:
            self.logger.error(f"Error updating signals table: {str(e)}")

    def update_performance_metrics(self, metrics: Dict):
        """Update performance metrics display"""
        try:
            self.win_rate_label.setText(f"Win Rate: {metrics['win_rate']:.2f}%")
            self.profit_factor_label.setText(f"Profit Factor: {metrics['profit_factor']:.2f}")
            self.sharp_ratio_label.setText(f"Sharp Ratio: {metrics['sharp_ratio']:.2f}")
            self.ai_accuracy_progress.setValue(int(metrics['ai_accuracy'] * 100))

        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {str(e)}")

    def show_error_message(self, message: str):
        """Display error message in status bar"""
        try:
            self.statusBar().showMessage(f"Error: {message}", 5000)
        except Exception as e:
            self.logger.error(f"Error showing error message: {str(e)}")

    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Clean up resources
            self.market_timer.stop()
            self.account_timer.stop()
            event.accept()
        except Exception as e:
            self.logger.error(f"Error handling close event: {str(e)}")
            event.accept()
