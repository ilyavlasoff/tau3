from PyQt5 import QtCore
from PyQt5.QtCore import *
import numpy as np


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data, horizontal_header, vertical_header):
        super(TableModel, self).__init__()
        self.data_matrix = data
        self.row_count = max(len(data), len(horizontal_header))
        self.column_count = len(vertical_header) if len(data) == 0 else max(len(horizontal_header), len(data[0]))
        for i in range(len(self.data_matrix)):
            self.data_matrix[i] += [0 for _ in range(len(self.data_matrix[i]), self.column_count)]
        self.data_matrix += [[0 for _ in range(self.column_count)] for _ in range(len(self.data_matrix), self.row_count)]

        vertical_header += [str(i) for i in range(len(vertical_header), self.column_count)]
        horizontal_header += [str(i) for i in range(len(horizontal_header), self.row_count)]
        self.vertical_header = vertical_header
        self.horizontal_header = horizontal_header

    def setData(self, index, value, role: int = ...) -> bool:
        if not index.isValid():
            return False
        if role == QtCore.Qt.EditRole:
            try:
                self.data_matrix[index.row()][index.column()] = float(value)
            except ValueError:
                self.data_matrix[index.row()][index.column()] = 0
            self.dataChanged.emit(index, index, (QtCore.Qt.EditRole,))
        else:
            return False
        return True

    def data(self, index, role):
        if role == Qt.DisplayRole:
            try:
                return round(self.data_matrix[index.row()][index.column()], 2)
            except TypeError:
                return self.data_matrix[index.row()][index.column()]

    def rowCount(self, index) -> int:
        return self.row_count

    def columnCount(self, index) -> int:
        return self.column_count

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return QVariant(self.vertical_header[section])
            if orientation == Qt.Vertical:
                return QVariant(self.horizontal_header[section])
        return

    def add_columns(self, quantity=0, cols=None, header=None):
        if cols is None:
            cols = []

        for i in range(len(cols)):
            if len(cols[i]) < self.row_count:
                cols[i] += [0 for _ in range(len(cols[i]), self.row_count)]
            elif len(cols[i]) > self.row_count:
                self.data_matrix += [[] for _ in range(self.row_count, len(cols[i]))]
                self.row_count = len(cols[i])
        if quantity > len(cols):
            cols.append([0 for _ in range(self.row_count)])
        for i in range(len(cols)):
            for j in range(self.row_count):
                try:
                    self.data_matrix[j].append(float(cols[i][j]))
                except ValueError:
                    self.data_matrix[j].append(cols[i][j])
        if header is None:
            header = []
        header += [str(self.column_count + i + 1) for i in range(len(header), len(cols))]
        self.vertical_header += header
        self.column_count += len(cols)
        self.layoutChanged.emit()
        return self

    def add_column(self, col=None, header=None):
        if col is None:
            col = []
        self.add_columns(1, [col], header)

    def add_row(self, row=None, header=None):
        if row is None:
            row = []
        self.add_rows(1, [row], header)

    def add_rows(self, quantity, rows=None, header=None):
        if rows is None:
            rows = []
        if quantity > len(rows):
            rows += [[float(0) for _ in range(self.column_count)] for _ in range(quantity - len(rows))]
        for row in rows:
            row += [float(0) for _ in range(len(row), self.column_count)]
            for i in range(len(row)):
                try:
                    row[i] = float(row[i])
                except ValueError:
                    row[i] = float(0)
            self.data_matrix.append(row)
        self.row_count += quantity
        if header is None:
            header = []
        header += [str(self.row_count + i + 1) for i in range(len(header), len(rows))]
        self.horizontal_header += header
        self.layoutChanged.emit()
        return self

    def remove_last_row(self, quantity=1):
        for i in range(quantity):
            self.remove_row(len(self.data_matrix)-1)

    def remove_row(self, row):
        if row >= len(self.data_matrix) or row < 0:
            raise Exception('No such index')
        del self.data_matrix[row]
        self.row_count -= 1
        self.layoutChanged.emit()

    def remove_last_row_range(self, quantity):
        if quantity <= 0:
            raise Exception('Starts index must go beyond zero')
        self.data_matrix = self.data_matrix[:-quantity]
        self.row_count -= quantity
        self.layoutChanged.emit()

    def remove_row_range(self, starts, ends):
        if starts > ends:
            raise Exception('Start index must be less than end')
        if ends < len(self.data_matrix):
            raise Exception('End index exceeds data matrix length')
        if starts < 0:
            raise Exception('Starts index must go beyond zero')
        self.data_matrix = self.data_matrix[:starts][ends:]
        self.rowCount -= abs(ends - starts)
        self.layoutChanged.emit()

    def remove_last_column(self):
        self.remove_column(len(self.data_matrix)-1)

    def remove_last_column_range(self, count):
        if count <=0:
            raise Exception('Incorrect range count')
        for i in range(len(self.data_matrix)):
            self.data_matrix[i] = self.data_matrix[i][:-count]
        self.column_count -= count
        self.layoutChanged.emit()

    def remove_column(self, col):
        for i in range(len(self.data_matrix)):
            del self.data_matrix[i][col]
        self.column_count -= 1
        self.layoutChanged.emit()

    def flags(self, index: QModelIndex):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def set_data(self, index, value, role):
        try:
            self.data_matrix[index.row()][index.column()] = float(value)
        except ValueError:
            self.data_matrix[index.row()][index.column()] = value
        return True

    def clear(self):
        for i in range(len(self.data_matrix)):
            self.data_matrix[i].clear()
        self.data_matrix.clear()
        self.row_count = 0
        self.column_count = 0
        self.horizontal_header.clear()
        self.vertical_header.clear()
        self.layoutChanged.emit()

    def get_data_matrix(self):
        return np.array(self.data_matrix, dtype=object)