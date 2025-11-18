# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'editor.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QFrame, QGraphicsView, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QMenuBar,
    QPushButton, QScrollArea, QSizePolicy, QSpinBox,
    QSplitter, QStackedWidget, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_LevelEditor(object):
    def setupUi(self, LevelEditor):
        if not LevelEditor.objectName():
            LevelEditor.setObjectName(u"LevelEditor")
        LevelEditor.resize(1280, 800)
        self.action_load_json = QAction(LevelEditor)
        self.action_load_json.setObjectName(u"action_load_json")
        self.action_save_json = QAction(LevelEditor)
        self.action_save_json.setObjectName(u"action_save_json")
        self.centralwidget = QWidget(LevelEditor)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.toolbox_container = QWidget(self.splitter)
        self.toolbox_container.setObjectName(u"toolbox_container")
        self.toolbox_container.setMinimumSize(QSize(400, 0))
        self.toolbox_container.setMaximumSize(QSize(400, 16777215))
        self.verticalLayout = QVBoxLayout(self.toolbox_container)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(self.toolbox_container)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_2.addWidget(self.label_5)

        self.combo_zone_selector = QComboBox(self.groupBox)
        self.combo_zone_selector.setObjectName(u"combo_zone_selector")

        self.verticalLayout_2.addWidget(self.combo_zone_selector)

        self.line = QFrame(self.groupBox)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        self.list_objects = QListWidget(self.groupBox)
        self.list_objects.setObjectName(u"list_objects")

        self.verticalLayout_2.addWidget(self.list_objects)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btn_add_object = QPushButton(self.groupBox)
        self.btn_add_object.setObjectName(u"btn_add_object")

        self.horizontalLayout_3.addWidget(self.btn_add_object)

        self.btn_delete_object = QPushButton(self.groupBox)
        self.btn_delete_object.setObjectName(u"btn_delete_object")

        self.horizontalLayout_3.addWidget(self.btn_delete_object)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addWidget(self.groupBox)

        self.scrollArea = QScrollArea(self.toolbox_container)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, -190, 378, 705))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.properties_box = QGroupBox(self.scrollAreaWidgetContents)
        self.properties_box.setObjectName(u"properties_box")
        self.formLayout = QFormLayout(self.properties_box)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.properties_box)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.prop_id = QLineEdit(self.properties_box)
        self.prop_id.setObjectName(u"prop_id")
        self.prop_id.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.prop_id)

        self.label_6 = QLabel(self.properties_box)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.prop_type = QComboBox(self.properties_box)
        self.prop_type.addItem("")
        self.prop_type.addItem("")
        self.prop_type.setObjectName(u"prop_type")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.prop_type)

        self.label_7 = QLabel(self.properties_box)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.prop_x = QSpinBox(self.properties_box)
        self.prop_x.setObjectName(u"prop_x")
        self.prop_x.setMaximum(9999)

        self.horizontalLayout_4.addWidget(self.prop_x)

        self.prop_y = QSpinBox(self.properties_box)
        self.prop_y.setObjectName(u"prop_y")
        self.prop_y.setMaximum(9999)

        self.horizontalLayout_4.addWidget(self.prop_y)


        self.formLayout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_4)

        self.label_2 = QLabel(self.properties_box)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.prop_image_path_combo = QComboBox(self.properties_box)
        self.prop_image_path_combo.setObjectName(u"prop_image_path_combo")
        self.prop_image_path_combo.setEditable(True)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.prop_image_path_combo)

        self.label_12 = QLabel(self.properties_box)
        self.label_12.setObjectName(u"label_12")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.prop_image_preview = QLabel(self.properties_box)
        self.prop_image_preview.setObjectName(u"prop_image_preview")
        self.prop_image_preview.setMinimumSize(QSize(0, 100))
        self.prop_image_preview.setStyleSheet(u"background-color: rgb(22, 22, 22);\n"
"border: 1px solid gray;")
        self.prop_image_preview.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.prop_image_preview)

        self.label_8 = QLabel(self.properties_box)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.prop_resize_factor = QDoubleSpinBox(self.properties_box)
        self.prop_resize_factor.setObjectName(u"prop_resize_factor")
        self.prop_resize_factor.setSingleStep(0.100000000000000)
        self.prop_resize_factor.setValue(4.000000000000000)

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.prop_resize_factor)

        self.label_9 = QLabel(self.properties_box)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.prop_is_passable = QCheckBox(self.properties_box)
        self.prop_is_passable.setObjectName(u"prop_is_passable")

        self.horizontalLayout_7.addWidget(self.prop_is_passable)

        self.prop_starts_hidden = QCheckBox(self.properties_box)
        self.prop_starts_hidden.setObjectName(u"prop_starts_hidden")

        self.horizontalLayout_7.addWidget(self.prop_starts_hidden)


        self.formLayout.setLayout(6, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_7)

        self.label_10 = QLabel(self.properties_box)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.prop_hitbox_dx = QSpinBox(self.properties_box)
        self.prop_hitbox_dx.setObjectName(u"prop_hitbox_dx")
        self.prop_hitbox_dx.setMinimum(-999)
        self.prop_hitbox_dx.setMaximum(999)

        self.horizontalLayout_6.addWidget(self.prop_hitbox_dx)

        self.prop_hitbox_dy = QSpinBox(self.properties_box)
        self.prop_hitbox_dy.setObjectName(u"prop_hitbox_dy")
        self.prop_hitbox_dy.setMinimum(-999)
        self.prop_hitbox_dy.setMaximum(999)

        self.horizontalLayout_6.addWidget(self.prop_hitbox_dy)

        self.prop_hitbox_dw = QSpinBox(self.properties_box)
        self.prop_hitbox_dw.setObjectName(u"prop_hitbox_dw")
        self.prop_hitbox_dw.setMinimum(-999)
        self.prop_hitbox_dw.setMaximum(999)

        self.horizontalLayout_6.addWidget(self.prop_hitbox_dw)

        self.prop_hitbox_dh = QSpinBox(self.properties_box)
        self.prop_hitbox_dh.setObjectName(u"prop_hitbox_dh")
        self.prop_hitbox_dh.setMinimum(-999)
        self.prop_hitbox_dh.setMaximum(999)

        self.horizontalLayout_6.addWidget(self.prop_hitbox_dh)


        self.formLayout.setLayout(7, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_6)


        self.verticalLayout_4.addWidget(self.properties_box)

        self.group_animation = QGroupBox(self.scrollAreaWidgetContents)
        self.group_animation.setObjectName(u"group_animation")
        self.verticalLayout_5 = QVBoxLayout(self.group_animation)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.prop_anim_list = QListWidget(self.group_animation)
        self.prop_anim_list.setObjectName(u"prop_anim_list")

        self.verticalLayout_5.addWidget(self.prop_anim_list)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.btn_anim_add = QPushButton(self.group_animation)
        self.btn_anim_add.setObjectName(u"btn_anim_add")

        self.horizontalLayout_9.addWidget(self.btn_anim_add)

        self.btn_anim_remove = QPushButton(self.group_animation)
        self.btn_anim_remove.setObjectName(u"btn_anim_remove")

        self.horizontalLayout_9.addWidget(self.btn_anim_remove)


        self.verticalLayout_5.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_13 = QLabel(self.group_animation)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_10.addWidget(self.label_13)

        self.prop_anim_speed = QDoubleSpinBox(self.group_animation)
        self.prop_anim_speed.setObjectName(u"prop_anim_speed")
        self.prop_anim_speed.setDecimals(3)
        self.prop_anim_speed.setSingleStep(0.010000000000000)
        self.prop_anim_speed.setValue(0.100000000000000)

        self.horizontalLayout_10.addWidget(self.prop_anim_speed)


        self.verticalLayout_5.addLayout(self.horizontalLayout_10)


        self.verticalLayout_4.addWidget(self.group_animation)

        self.group_interaction = QGroupBox(self.scrollAreaWidgetContents)
        self.group_interaction.setObjectName(u"group_interaction")
        self.formLayout_2 = QFormLayout(self.group_interaction)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_3 = QLabel(self.group_interaction)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.prop_interaction_type = QComboBox(self.group_interaction)
        self.prop_interaction_type.addItem("")
        self.prop_interaction_type.addItem("")
        self.prop_interaction_type.addItem("")
        self.prop_interaction_type.addItem("")
        self.prop_interaction_type.setObjectName(u"prop_interaction_type")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.prop_interaction_type)

        self.label_11 = QLabel(self.group_interaction)
        self.label_11.setObjectName(u"label_11")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.prop_flash_image_path_combo = QComboBox(self.group_interaction)
        self.prop_flash_image_path_combo.setObjectName(u"prop_flash_image_path_combo")
        self.prop_flash_image_path_combo.setEditable(True)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.prop_flash_image_path_combo)

        self.label_4 = QLabel(self.group_interaction)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.prop_interaction_data_stack = QStackedWidget(self.group_interaction)
        self.prop_interaction_data_stack.setObjectName(u"prop_interaction_data_stack")
        self.stack_page_note = QWidget()
        self.stack_page_note.setObjectName(u"stack_page_note")
        self.verticalLayout_3 = QVBoxLayout(self.stack_page_note)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.data_note_text = QTextEdit(self.stack_page_note)
        self.data_note_text.setObjectName(u"data_note_text")

        self.verticalLayout_3.addWidget(self.data_note_text)

        self.prop_interaction_data_stack.addWidget(self.stack_page_note)
        self.stack_page_image = QWidget()
        self.stack_page_image.setObjectName(u"stack_page_image")
        self.horizontalLayout_2 = QHBoxLayout(self.stack_page_image)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.data_image_path_combo = QComboBox(self.stack_page_image)
        self.data_image_path_combo.setObjectName(u"data_image_path_combo")
        self.data_image_path_combo.setEditable(True)

        self.horizontalLayout_2.addWidget(self.data_image_path_combo)

        self.prop_interaction_data_stack.addWidget(self.stack_page_image)
        self.stack_page_door = QWidget()
        self.stack_page_door.setObjectName(u"stack_page_door")
        self.prop_interaction_data_stack.addWidget(self.stack_page_door)

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.prop_interaction_data_stack)


        self.verticalLayout_4.addWidget(self.group_interaction)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.splitter.addWidget(self.toolbox_container)
        self.canvas_view = QGraphicsView(self.splitter)
        self.canvas_view.setObjectName(u"canvas_view")
        self.splitter.addWidget(self.canvas_view)

        self.horizontalLayout.addWidget(self.splitter)

        LevelEditor.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(LevelEditor)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1280, 21))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        LevelEditor.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(LevelEditor)
        self.statusbar.setObjectName(u"statusbar")
        LevelEditor.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menuArchivo.addAction(self.action_load_json)
        self.menuArchivo.addAction(self.action_save_json)

        self.retranslateUi(LevelEditor)

        self.prop_interaction_data_stack.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(LevelEditor)
    # setupUi

    def retranslateUi(self, LevelEditor):
        LevelEditor.setWindowTitle(QCoreApplication.translate("LevelEditor", u"Editor de Niveles de Oakhill", None))
        self.action_load_json.setText(QCoreApplication.translate("LevelEditor", u"Cargar JSON", None))
        self.action_save_json.setText(QCoreApplication.translate("LevelEditor", u"Guardar JSON", None))
        self.groupBox.setTitle(QCoreApplication.translate("LevelEditor", u"Objetos de la Zona", None))
        self.label_5.setText(QCoreApplication.translate("LevelEditor", u"Seleccionar Zona:", None))
        self.btn_add_object.setText(QCoreApplication.translate("LevelEditor", u"+ A\u00f1adir Objeto", None))
        self.btn_delete_object.setText(QCoreApplication.translate("LevelEditor", u"- Borrar Objeto", None))
        self.properties_box.setTitle(QCoreApplication.translate("LevelEditor", u"Propiedades", None))
        self.label.setText(QCoreApplication.translate("LevelEditor", u"ID:", None))
        self.label_6.setText(QCoreApplication.translate("LevelEditor", u"Tipo Objeto:", None))
        self.prop_type.setItemText(0, QCoreApplication.translate("LevelEditor", u"Obstacle", None))
        self.prop_type.setItemText(1, QCoreApplication.translate("LevelEditor", u"Interactable", None))

        self.label_7.setText(QCoreApplication.translate("LevelEditor", u"Posici\u00f3n (X, Y):", None))
        self.label_2.setText(QCoreApplication.translate("LevelEditor", u"Image Path:", None))
        self.label_12.setText(QCoreApplication.translate("LevelEditor", u"Preview:", None))
        self.prop_image_preview.setText("")
        self.label_8.setText(QCoreApplication.translate("LevelEditor", u"Resize Factor:", None))
        self.label_9.setText(QCoreApplication.translate("LevelEditor", u"Opciones:", None))
        self.prop_is_passable.setText(QCoreApplication.translate("LevelEditor", u"Es Pasable", None))
        self.prop_starts_hidden.setText(QCoreApplication.translate("LevelEditor", u"Empezar Oculto", None))
        self.label_10.setText(QCoreApplication.translate("LevelEditor", u"Hitbox Offset:", None))
        self.group_animation.setTitle(QCoreApplication.translate("LevelEditor", u"Animaci\u00f3n (Opcional)", None))
        self.btn_anim_add.setText(QCoreApplication.translate("LevelEditor", u"+", None))
        self.btn_anim_remove.setText(QCoreApplication.translate("LevelEditor", u"-", None))
        self.label_13.setText(QCoreApplication.translate("LevelEditor", u"Velocidad (Anim Speed):", None))
        self.group_interaction.setTitle(QCoreApplication.translate("LevelEditor", u"Interacci\u00f3n (Solo para Interactables)", None))
        self.label_3.setText(QCoreApplication.translate("LevelEditor", u"Tipo Interacci\u00f3n:", None))
        self.prop_interaction_type.setItemText(0, QCoreApplication.translate("LevelEditor", u"None", None))
        self.prop_interaction_type.setItemText(1, QCoreApplication.translate("LevelEditor", u"Note", None))
        self.prop_interaction_type.setItemText(2, QCoreApplication.translate("LevelEditor", u"Image", None))
        self.prop_interaction_type.setItemText(3, QCoreApplication.translate("LevelEditor", u"Door", None))

        self.label_11.setText(QCoreApplication.translate("LevelEditor", u"Flash Image:", None))
        self.label_4.setText(QCoreApplication.translate("LevelEditor", u"Datos Interacci\u00f3n:", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("LevelEditor", u"Archivo", None))
    # retranslateUi

