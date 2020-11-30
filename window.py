from PyQt5 import QtWidgets
from serializer import Serializer
from mainForm import Ui_mainForm
from tableModel import TableModel
from johnson import Johnson, DetailItem
from PyQt5.QtGui import QPixmap
import matplotlib
import matplotlib.pyplot as plt
import string
import math
import os
import random as rand
import numpy as np
matplotlib.use('Agg')


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
        self.previous_calculated_flag = False
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
        selected_count = self.ui.machineCount.currentIndex()
        delta_count = selected_count - self.data['machines_count_selected_index']
        previous_selected_value = int(self.data['machines_count_variants'][self.data['machines_count_selected_index']])
        current_selected_value = int(self.data['machines_count_variants'][selected_count])
        self.ui.alterMethodCheckBox.setVisible(True if
                                               int(self.data['machines_count_variants'][selected_count]) > 2 else False)
        if delta_count > 0:
            self.ui.initialQueueTableView.model().add_rows(delta_count, None,
                                                           ['T%s' % str(i + 1) for i in
                                                            range(previous_selected_value, current_selected_value)])
            self.ui.optimizedQueueTableView.model().add_rows(delta_count, None,
                                                           ['T%s' % str(i + 1) for i in
                                                            range(previous_selected_value, current_selected_value)])
        else:
            self.ui.initialQueueTableView.model().remove_last_row_range(abs(delta_count))
            self.ui.optimizedQueueTableView.model().remove_last_row_range(abs(delta_count))
        self.data['machines_count_selected_index'] = selected_count
        self.ui.initialQueueTableView.resizeRowsToContents()

    def load_from_file(self):
        try:
            load_file_data = QtWidgets.QFileDialog.getOpenFileName(self, 'Load file...',
                                                                   os.path.dirname(os.getcwd()))
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
        matrix_data = np.array(self.ui.initialQueueTableView.model().get_data_matrix())
        columns_count = self.data['details_count']
        rows_count = int(self.data['machines_count_variants'][self.data['machines_count_selected_index']])
        self.data['initial_queue'] = matrix_data[:rows_count, :columns_count]
        if self.ui.initialQueueTableView.model().column_count - self.data['details_count']:
            self.ui.initialQueueTableView.model().remove_last_column_range(
                self.ui.initialQueueTableView.model().column_count - self.data['details_count'])


    def save_to_file(self):
        self.update_data()
        try:
            save_file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file...', os.path.dirname(os.getcwd()))[0]
            Serializer.serialize(save_file_path, self.data)
        except OSError:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Во время сохранения файла произошла ошибка')

    def setup_data(self):
        if len(self.data['initial_queue']) == 0:
            vertical_header = []
        else:
            data_row_len = len(self.data['initial_queue'][0])
            vertical_header = [i+1 for i in range(data_row_len)]
        self.ui.detailsCount.blockSignals(True)
        self.ui.detailsCount.setValue(int(self.data['details_count']))
        self.ui.detailsCount.blockSignals(False)
        self.ui.machineCount.blockSignals(True)
        self.ui.machineCount.clear()
        self.ui.machineCount.addItems(self.data['machines_count_variants'])
        self.ui.machineCount.setCurrentIndex(int(self.data['machines_count_selected_index']))
        self.ui.machineCount.blockSignals(False)
        horizontal_header = ['T%s' % str(i + 1) for i in
                                          range(int(self.data['machines_count_variants']
                                                    [self.data['machines_count_selected_index']]))]
        self.ui.initialQueueTableView.setModel(TableModel(self.data['initial_queue'], horizontal_header, vertical_header))
        self.ui.initialQueueTableView.resizeColumnsToContents()
        self.ui.alterMethodCheckBox.setVisible(True if int(self.data['machines_count_variants']
                                                    [self.data['machines_count_selected_index']]) > 2 else False)
        self.ui.optimizedQueueTableView.setModel(TableModel([], horizontal_header, []))

    def calculate(self):
        if self.previous_calculated_flag:
            if QtWidgets.QMessageBox.question(self, 'Внимание', "Полученные ранее результаты будут утеряны. Продолжить",
                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
            horizontal_header = ['T%s' % str(i + 1) for i in
                                 range(int(self.data['machines_count_variants']
                                           [self.data['machines_count_selected_index']]))]
            self.ui.optimizedQueueTableView.setModel(TableModel([], horizontal_header, []))
        self.update_data()
        if self.data['details_count'] < 2:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Недостаточное количество деталей для расчета')
            return
        for i in self.data['initial_queue']:
            if len(list(filter(lambda x: not type(x) is float or x < 0, i))) > 0:
                QtWidgets.QMessageBox.critical(self, 'Error', 'Некоторые значения заданы неверно')
                return
        #try:
        if 1:
            detail_items = DetailItem.create_from_multiple_list(self.data['initial_queue'])
            j = Johnson(detail_items)
            opt = j.optimize(self.ui.alterMethodCheckBox.isChecked())
            orig_params = j.get_original_params()
        #except Exception:
        #    QtWidgets.QMessageBox.critical(self, 'Error', 'Произошла ошибка при вычислениях')
        #    return
        try:
            self.output_result(opt['path'], opt['params'], orig_params)
        except Exception:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Ошибка вывода значений')
            return
        self.previous_calculated_flag = True

    def output_result(self, result_sequence, result_params, orig_params=None):
        for i in result_sequence:
            self.ui.optimizedQueueTableView.model().add_column(i.machines_processing, [i.name])

        self.ui.optimizedQueueTableView.model().add_column([result_params[str(i)]['sum_delay']
                                                            for i in range(len(result_params))], ['DT'])
        self.ui.optimizedQueueTableView.model().add_column([result_params[str(i)]['sum_working']
                                                            for i in range(len(result_params))], ['UT'])
        self.ui.optimizedQueueTableView.resizeColumnsToContents()

        if orig_params:
            self.ui.initialQueueTableView.model().add_column([orig_params[str(i)]['sum_delay']
                                                                for i in range(len(result_params))], ['DT'])
            self.ui.initialQueueTableView.model().add_column([orig_params[str(i)]['sum_working']
                                                                for i in range(len(result_params))], ['UT'])
            self.ui.initialQueueTableView.resizeColumnsToContents()

        file_diagram = self.draw_plot(result_params)
        pixmap = QPixmap(file_diagram)
        self.ui.diagramLabel.setEnabled(True)
        self.ui.diagramLabel.setPixmap(pixmap)
        self.ui.diagramLabel.resize(pixmap.width(), pixmap.height())

    def draw_plot(self, units):
        fig, gnt = plt.subplots()

        y_lim = 100
        x_lim = max([max([i['activity']['starts'] + i['activity']['duration'] for i in units[unit]['tasks']]) for unit in units])

        gnt.set_ylim(0, y_lim)
        gnt.set_xlim(0, x_lim)

        gnt.set_xlabel('Time')
        gnt.set_ylabel('Units')

        gnt.grid(True)

        available_colors = [
            'tab:blue',
            'tab:orange',
            'tab:green',
            'tab:red',
            'tab:purple',
            'tab:brown',
            'tab:pink',
            'tab:gray',
            'tab:olive',
            'tab:cyan',
        ]
        spacing = math.floor(y_lim / len(units))
        position = [(spacing * int(i / spacing), spacing - 2) for i in range(y_lim) if i % spacing == 0]
        y_ticks = [(int(i / spacing) + 0.5) * spacing - 1 for i in range(y_lim - 1) if i % spacing == 0]

        x_step = int(x_lim / 10) if int(x_lim / 10) >= 3 else 1
        x_ticks = [i for i in range(math.ceil(x_lim)) if i % x_step == 0]

        gnt.set_yticks(y_ticks)
        gnt.set_xticks(x_ticks)

        y_labels = []
        iters = 0
        colors_scheme = tuple((available_colors[i % len(available_colors)] for i in range(self.ui.detailsCount.value())))
        for i in units.values():
            barh_data = list([(x['activity']['starts'], x['activity']['duration']) for x in i['tasks']])
            gnt.broken_barh(barh_data, position[iters], facecolors=colors_scheme)
            y_labels.append(str(iters+1))
            iters += 1
        gnt.set_yticklabels(y_labels)

        filename = './plots/' + ''.join([rand.choice(string.ascii_lowercase) for i in range(10)]) + '.png'
        if not os.path.exists(os.path.dirname(filename)):
            os.mkdir(os.path.dirname(filename))
        plt.savefig(filename)
        return filename

