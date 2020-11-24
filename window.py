from PyQt5 import QtWidgets
from serializer import Serializer
from mainForm import Ui_mainForm
from tableModel import TableModel
from johnson import Johnson, DetailItem


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_mainForm()
        self.ui.setupUi(self)

        self.data = {
            'initial_queue': [],
            'machines_count_variants': ['2', '3'],
            'machines_count_selected_index': 0,
            'details_count': 0
        }
        self.setup_data()
        self.ui.machineCount.currentIndexChanged.connect(self.machine_count_changed)
        self.ui.detailsCount.valueChanged.connect(self.details_count_changed)
        self.ui.startCalculationButton.clicked.connect(self.calculate)
        self.ui.loadButton.clicked.connect(self.load_from_file)
        self.ui.saveButton.clicked.connect(self.save_to_file)

    def details_count_changed(self):
        delta_count = self.ui.detailsCount.value() - self.data['details_count']
        if delta_count > 0:
            self.ui.initialQueueTableView.model().add_columns(abs(delta_count))
        else:
            self.ui.initialQueueTableView.model().remove_last_column_range(abs(delta_count))
        self.data['details_count'] = self.ui.detailsCount.value()
        self.ui.initialQueueTableView.resizeColumnsToContents()

    def machine_count_changed(self):
        selectedCount = self.ui.machineCount.currentIndex()
        delta_count = selectedCount - self.data['machines_count_selected_index']
        previous_selected_value = int(self.data['machines_count_variants'][self.data['machines_count_selected_index']])
        current_selected_value = int(self.data['machines_count_variants'][selectedCount])
        if delta_count > 0:
            self.ui.initialQueueTableView.model().add_rows(delta_count, None,
                                                           ['T%s' % str(i + 1) for i in
                                                            range(previous_selected_value, current_selected_value)])
        else:
            self.ui.initialQueueTableView.model().remove_last_row_range(abs(delta_count))
        self.data['machines_count_selected_index'] = selectedCount
        self.ui.initialQueueTableView.resizeRowsToContents()

    def load_from_file(self):
        try:
            load_file_data = QtWidgets.QFileDialog.getOpenFileName(self, 'Load file...', './')
            if len(load_file_data) == 0:
                QtWidgets.QMessageBox.critical(self, 'Error', 'Файл не выбран')
                return
            else:
                load_file_data_path = load_file_data[0]
                self.data = Serializer.deserialize(load_file_data_path)
                self.setup_data()
        except:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Загрузка невозможна')

    def update_data(self):
        self.data['initial_queue'] = self.ui.initialQueueTableView.model().get_data_matrix()

    def save_to_file(self):
        self.update_data()
        try:
            save_file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file...', './')[0]
            Serializer.serialize(save_file_path, self.data)
        except OSError:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Во время сохранения файла произошла ошибка')

    def setup_data(self):
        if len(self.data['initial_queue']) == 0:
            vertical_header = []
        else:
            data_row_len = len(self.data['initial_queue'][0])
            vertical_header = [i+1 for i in range(data_row_len)]
        self.ui.machineCount.setCurrentIndex(self.data['machines_count_selected_index'])
        self.ui.detailsCount.setValue(int(self.data['details_count']))
        self.ui.machineCount.addItems(self.data['machines_count_variants'])
        self.ui.machineCount.setCurrentIndex(int(self.data['machines_count_selected_index']))
        horizontal_header = ['T%s' % str(i + 1) for i in
                                          range(int(self.data['machines_count_variants']
                                                    [self.data['machines_count_selected_index']]))]
        self.ui.initialQueueTableView.setModel(TableModel(self.data['initial_queue'], horizontal_header, vertical_header))

    def calculate(self):
        self.update_data()
        detail_items = DetailItem.create_from_multiple_list(self.data['initial_queue'])
        j = Johnson(detail_items)
        optimized_list = j.optimize()
        pass

