# -*- coding: utf-8 -*-

import re

class ParseError(Exception):
    """Path data parse error."""
    def __init__(self, msg, data):
        self.msg = msg
        self.data = data

    def __str__(self):
        return '{0}: {1}'.format(self.msg, self.data)

def num_parser(data):
    nump = r'^ *(-?[0-9]+\.[0-9]*|-?\.[0-9]+|-?[0-9]+)'
    m = re.match(nump, data)
    if m is None:
        raise ParseError('num_parser', data)
    return (float(m.group(1)), data[len(m.group(0)):])

def cmd_parser(data):
    p = r'^ *([a-zA-Z])'
    m = re.match(p, data)
    if m is None:
        raise ParseError('cmd_parser', data)
    return (m.group(1), data[len(m.group(0)):])

def point_parser(data):
    nump = r'(-?[0-9]+\.[0-9]*|-?\.[0-9]+|-?[0-9]+)'
    p = r'^ *{nump}\s*,?\s*{nump}'.format(nump=nump)
    m = re.match(p, data)
    if m is None:
        raise ParseError('point_parser', data)
    return ((float(m.group(1)),float(m.group(2))) , data[len(m.group(0)):])

from PyQt5.QtGui import (QBrush, QColor, QFont, QLinearGradient, QPainter,
        QPainterPath, QPalette, QPen)

class PathBuilder(object):
    def __init__(self):
        super(PathBuilder, self).__init__()

    def cmd_m(self, path, data):
        pos = path.currentPosition()
        ((x,y), data) = point_parser(data)
        path.moveTo(pos.x() + x, pos.y() + y)
        return data

    def cmd_M(self, path, data):
        ((x,y), data) = point_parser(data)
        path.moveTo(x, y)
        return data

    def cmd_l(self, path, data):
        pos = path.currentPosition()
        ((x,y), data) = point_parser(data)
        path.lineTo(pos.x() + x, pos.y() + y)
        return data

    def cmd_L(self, path, data):
        ((x,y), data) = point_parser(data)
        path.lineTo(x,y)
        return data

    def cmd_h(self, path, data):
        pos = path.currentPosition()
        (x, data) = num_parser(data)
        path.lineTo(x, pos.y())
        return data

    def cmd_v(self, path, data):
        pos = path.currentPosition()
        (y, data) = num_parser(data)
        path.lineTo(pos.x(), y)
        return data

    def cmd_c(self, path, data):
        ((cx1, cy1), data) = point_parser(data)
        ((cx2, cy2), data) = point_parser(data)
        ((ex, ey), data) = point_parser(data)
        path.cubicTo(cx1,cy1, cx2,cy2, ex,ey)
        self.last_cp = ((cx2,cy2), (ex,ey))
        return data

    def cmd_q(self, path, data):
        ((cx, cy), data) = point_parser(data)
        ((ex, ey), data) = point_parser(data)
        path.quadTo(cx,cy, ex,ey)
        self.last_cp = ((cx,cy), (ex,ey))
        return data

    def cmd_s(self, path, data):
        if not self.last_cp:
            ((cx,cy), (ex, ey)) = self.last_cp
            (cx1, cy1)  = (ex - cx, ey - cy)
        else:
            pos = path.currentPosition()
            (cx1, cy1) = (pos.x(), pos.y())

        ((cx2, cy2), data) = point_parser(data)
        ((ex, ey), data) = point_parser(data)
        path.cubicTo(cx1,cy1, cx2,cy2, ex,ey)
        self.last_cp = ((cx2,cy2), (ex,ey))
        return data

    def cmd_t(self, path, data):
        if not self.last_cp:
            ((cx,cy), (ex, ey)) = self.last_cp
            (cx1, cy1)  = (ex - cx, ey - cy)
        else:
            pos = path.currentPosition()
            (cx1, cy1) = (pos.x(), pos.y())

        ((ex, ey), data) = point_parser(data)
        path.cubicTo(cx1,cy1, ex,ey)
        self.last_cp = ((cx1,cy1), (ex,ey))
        return data


    def cmd_z(self, path, data):
        path.closeSubpath()
        return data

    def parse(self, data):
        data = data.replace('\r\n', ' ')

        cmds = { 'm': self.cmd_m,
                 'M': self.cmd_M,
                 'l': self.cmd_l,
                 'L': self.cmd_L,
                 'h': self.cmd_h,
                 'H': self.cmd_h,
                 'v': self.cmd_v,
                 'V': self.cmd_v,
                 'c': self.cmd_c,
                 'C': self.cmd_c,
                 'q': self.cmd_q,
                 'Q': self.cmd_q,
                 's': self.cmd_s,
                 'S': self.cmd_s,
                 't': self.cmd_t,
                 'T': self.cmd_t,
                 'z': self.cmd_z,
                 'Z': self.cmd_z,
        }

        path = QPainterPath()
        last_parser = None
        last_cp = None # (controlpoint, endpoint) of last Bezier curve

        cmd = ''

        while(True):
            while(last_parser is not None):
                try:
                    if cmd == 'm':
                        data = self.cmd_l(path,data)
                    elif cmd == 'M':
                        data = self.cmd_L(path,data)
                    else:
                        data = last_parser(path, data)
                except ParseError:
                    break

            # end of data?
            if re.match(r'\s*$', data):
                return path

            (cmd, data) = cmd_parser(data)
            if not cmd in cmds:
                raise ParseError('unkonw command: ' + cmd, data)
            data = cmds[cmd](path, data)
            if cmd.lower() != 'z':
                last_parser = cmds[cmd]

            if not cmd.lower() in ['c','q','s','t']:
                last_cp = None

def test():
    assert(('t', 'est') == cmd_parser('  test'))
    assert(('t', 'est') == cmd_parser('test'))
    try:
        cmd_parser('1.23')
        assert(False)
    except ParseError as e:
        assert(e.msg == 'cmd_parser')

    assert(( (1.0, 2.0), '') == point_parser('1.0 2.0'))
    assert(( (1.0, 2.0), '') == point_parser(' 1.0,2.0'))
    assert(( (1.0, 2.0), '') == point_parser('1.0 , 2.0'))
    try:
        point_parser('M1.0 , 2.0')
        assert(False)
    except ParseError as e:
        assert(e.msg == 'point_parser')

    assert(( (0.3, 0.3), '') == point_parser('.3.3'))
    assert(( (2.0, 0.3), '') == point_parser('2..3'))
    assert(( (2.0, 0.3), '') == point_parser('2.,.3'))
    assert(( (20.0, 30.0), '') == point_parser('20,30'))
    assert(( (-0.3, -0.3), '') == point_parser('-.3-.3'))
    assert(( (-2.0, -0.3), '') == point_parser('-2.-.3'))
    assert(( (-20.0, -30.0), '') == point_parser('-20,-30'))
    try:
        point_parser('2...3')
        assert(False)
    except ParseError as e:
        assert(e.msg == 'point_parser')

    assert((2.0, 'test') == num_parser('2.test'))
    assert((-2.0, 'test') == num_parser('-2.test'))
    assert((2.0, 'test') == num_parser(' 2.0test'))
    assert((2.0, ' test') == num_parser(' 2.0 test'))
    assert((20, ' test') == num_parser(' 20 test'))

if __name__ == '__main__':
    test()
