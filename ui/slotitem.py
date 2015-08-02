# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

from PyQt5.QtCore import QSize, Qt, QFile, QRectF, QRect
from PyQt5.QtGui import (QBrush, QColor, QFont, QLinearGradient, QPainter,
                         QPainterPath, QPalette, QPen, QTransform, QPolygonF)
from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QLabel,
                             QSizePolicy, QSpinBox, QWidget, QHBoxLayout, QVBoxLayout,
                             QGraphicsScene, QGraphicsView, QStyleOption, QStyle)

from .slotitem_parser import PathBuilder
from math import sin, cos, pi

ns = {'p' : "http://schemas.microsoft.com/winfx/2006/xaml/presentation",
      'ed': "http://schemas.microsoft.com/expression/2010/drawing"}

PRE_P = r"{http://schemas.microsoft.com/winfx/2006/xaml/presentation}"
PRE_ED = r"{http://schemas.microsoft.com/expression/2010/drawing}"

class IconBox(QWidget):
    def __init__(self, icon, parent=None):
        super(IconBox, self).__init__(parent)
        self.setMinimumSize(QSize(50, 50))
        self.icon = icon

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(30, 30))
        self.setMaximumSize(QSize(30, 30))


    def paintEvent(self, event):
        (w, h) = (self.width(), self.height())
        (bw, bh) = self.icon.boundingRect()

        # alignment to center
        ratio_w = float(w) / float(bw)
        ratio_h = float(h) / float(bh)
        if  ratio_h < ratio_w:
            new_bw = w / ratio_h
            brect = QRectF(-(new_bw - bw)/2, 0, new_bw, bh)
        else:
            new_bh = h / ratio_w
            brect = QRectF(0, -(new_bh - bh)/2, bw, new_bh)

        self.icon.setSceneRect(brect)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        self.icon.render(painter)

        # for apply stylesheet
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, p, self)


class SlotIcon(QGraphicsScene):
    builder = PathBuilder()
    def __init__(self, elms, grid=None):
        super(SlotIcon, self).__init__()
        self.grid = grid

        for elm in elms:
            if elm.tag == PRE_P + 'Path':
                self.create_path(elm)
            elif elm.tag == PRE_P + 'Ellipse':
                self.create_ellipse(elm)
            elif elm.tag == PRE_ED + 'Arc':
                self.create_arc(elm)
            elif elm.tag == PRE_ED + 'RegularPolygon':
                self.create_regular_polygon(elm)

    def boundingRect(self):
        brect = self.itemsBoundingRect()
        (bw, bh) = (brect.width(), brect.height())
        if self.grid is not None and 'Margin' in self.grid.attrib:
            m = float(self.grid.attrib['Margin'])
            bw += m*2
            bh += m*2
        return (bw, bh)

    def _margin(self, elm):
        if 'Margin' in elm.attrib:
            margin = [float(f) for f in elm.attrib['Margin'].split(',')]
            if len(margin) == 1:
                return margin * 4
            return margin
        return None

    def _elm_wh(self, elm):
        w = h = None
        if 'Width' in elm.attrib:
            w = float(elm.attrib['Width'])
        elif self.grid is not None and 'Width' in self.grid.attrib:
            w = float(self.grid.attrib['Width'])

        if 'Height' in elm.attrib:
            h = float(elm.attrib['Height'])
        elif self.grid is not None and 'Height' in self.grid.attrib:
            h = float(self.grid.attrib['Height'])

        return (w, h)

    def _set_penbrush(self, pathitem, elm):
        if 'Fill' in elm.attrib:
            pathitem.setBrush(QBrush(QColor(elm.attrib['Fill'])))

        if 'Stroke' in elm.attrib:
            pen = QPen(QColor(elm.attrib['Stroke']))
            pen.setJoinStyle(Qt.MiterJoin)
            if 'StrokeThickness' in elm.attrib:
                pen.setWidthF(float(elm.attrib['StrokeThickness']))
            pathitem.setPen(pen)

    def create_arc(self, elm):
        # FIXME
        path = QPainterPath()
        (w, h) = self._elm_wh(elm)
        path.addEllipse(0.0, 0.0, w, h)

        thickness = 1
        if 'ArcThickness' in elm.attrib:
            thickness = float(elm.attrib['ArcThickness'])
            path.translate(thickness/2, thickness/2)

        pathitem = self.addPath(path)

        pen = QPen()
        if 'Fill' in elm.attrib:
            pen.setColor(QColor(elm.attrib['Fill']))
        pen.setWidthF(thickness)
        pen.setCapStyle(Qt.FlatCap)
        pathitem.setPen(pen)

        return path

    def create_ellipse(self, elm):
        path = QPainterPath()
        path.addEllipse(0, 0,
                        float(elm.attrib['Width']),
                        float(elm.attrib['Height']))
        pathitem = self.addPath(path, QPen(Qt.NoPen))

        self._set_penbrush(pathitem, elm)

        margin = self._margin(elm)
        if margin:
            pathitem.setPos(margin[0], margin[1])

        return path

    def regular_polygon_path(self, elm):
        height = float(elm.attrib['Height'])
        width = float(elm.attrib['Width'])
        count = int(elm.attrib['PointCount'])
        path = QPainterPath()
        (x,y) = (0.0, height/2.0)
        path.moveTo(x,y)
        angle = pi/180.0 * 360.0 / count
        for _ in range(count-1):
            (x, y) = (x*cos(angle) - y*sin(angle),
                      x*sin(angle) + y*cos(angle))
            path.lineTo(x,y)
        path.closeSubpath()

        path.translate(width/2.0, height/2.0)
        return path

    def create_path(self, elm):
        data = elm.attrib['Data']
        path = self.builder.parse(data)
        rect = path.boundingRect()
        path.translate(-rect.x(), -rect.y())
        pathitem = self.addPath(path, QPen(Qt.NoPen))

        self._set_penbrush(pathitem, elm)

        margin = self._margin(elm)
        if margin:
            pathitem.moveBy(margin[0], margin[1])

        if 'VerticalAlignment' in elm.attrib and \
           'Center' == elm.attrib['VerticalAlignment']:
            #FIXME
            gh = float(self.grid.attrib['Height'])
            pathitem.moveBy(0, gh/2 - rect.height()/2)
            pathitem.moveBy(-margin[2], -margin[3])

        (w,h) = self._elm_wh(elm)
        if w is not None and h is not None:
            trans = pathitem.transform()
            trans = trans.scale(float(w) / float(rect.width()),
                                float(h) / float(rect.height()))
            pathitem.setTransform(trans)
        return path

    def create_regular_polygon(self, elm):
        path = self.regular_polygon_path(elm)
        pathitem = self.addPath(path, QPen(Qt.NoPen))

        self._set_penbrush(pathitem, elm)

        margin = self._margin(elm)
        if margin:
            pathitem.setPos(margin[0], margin[1])

        return path

# Don't call before QApplication() initialized.
def create_sloticontable():
    table = {}
    file = QFile(':/ui/Generic.SlotItemIcon.xaml')
    file.open(QFile.ReadOnly)
    text = str(file.readAll(), encoding='utf8')
    tree = ET.fromstring(text)
    triggers = tree.findall(r'.//p:Trigger', namespaces=ns)

    for trg in triggers:
        if (not 'Property' in trg.attrib and \
           'Type' == trg.attrib['Property']) or \
           not 'Value' in trg.attrib:
            continue

        name = trg.attrib['Value']

        viewbox = trg.find('p:Setter/p:Setter.Value/p:ControlTemplate/p:Viewbox',namespaces=ns)
        if viewbox is not None:
            grid = viewbox.find('p:Grid', namespaces=ns)
            if grid is not None:
                table[name] = SlotIcon([elm for elm in grid], grid)
        else:
            path_elm = trg.find('p:Setter/p:Setter.Value/p:ControlTemplate/p:Path',namespaces=ns)
            if path_elm is not None:
                table[name] = SlotIcon([path_elm])

    try:
        path = tree.find(r'.//p:Path', namespaces=ns)
        path.attrib['Fill'] = 'gray'
        unknown_icon = SlotIcon([path])
        table['unknown'] = unknown_icon
    except Exception as e:
        print(e)

    return table

# for test
class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.box = QVBoxLayout()
        self.setLayout(self.box)

        table = create_sloticontable()
        self.hbox = None

        try:
            for (i,k) in  enumerate(list(table)):
                if i%5 == 0:
                    self.hbox = QHBoxLayout()
                    self.box.addLayout(self.hbox)
                self.hbox.addWidget(IconBox(table[k],self))
        except None as e:
            print(e)

def main():
    import sys
    app = QApplication(sys.argv)

    widget = MainWidget()
    widget.show()

    ret = app.exec_()
    sys.exit(ret)

if __name__ == '__main__':
    main()
