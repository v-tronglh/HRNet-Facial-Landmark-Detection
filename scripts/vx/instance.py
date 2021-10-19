from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import List

from .attrib import Attrib
from .base import Element


class Instance(Element):
    tag = ''


class PointBase(Instance):
    tag = ''

    def __init__(
        self,
        label: str,
        occluded: int,
        source: str,
        points: List[List[float]],
        z_order: int,
        attribs: List[Attrib],
    ):
        super(PointBase, self).__init__()
        self.label = label
        self.occluded = occluded
        self.source = source
        self.points = points
        self.z_order = z_order
        self.attribs = attribs

    @classmethod
    def parse(cls, instance: ET.Element) -> PointBase:
        label = instance.attrib['label']
        occluded = int(instance.attrib['occluded'])
        source = instance.attrib['source']
        points = [[float(p) for p in point.split(',')] for point in instance.attrib['points'].split(';')]
        z_order = int(instance.attrib['z_order'])
        attribs = [Attrib.parse(attrib) for attrib in instance]
        return cls(label, occluded, source, points, z_order, attribs)

    @property
    def xml(self) -> ET.Element:
        attrib = {
            'label': self.label,
            'occluded': str(self.occluded),
            'source': self.source,
            'points': ';'.join([','.join([str(p) for p in point]) for point in self.points]),
            'z_order': str(self.z_order),
        }
        ele = ET.Element(self.tag, attrib)
        ele.extend([attrib.xml for attrib in self.attribs])
        return ele


class Polyline(PointBase):
    tag = 'polyline'


class Polygon(PointBase):
    tag = 'polygon'


class Points(PointBase):
    tag = 'points'


class Box(Instance):
    tag = 'box'

    def __init__(
        self,
        label: str,
        occluded: int,
        source: str,
        xtl: float,
        ytl: float,
        xbr: float,
        ybr: float,
        z_order: int,
        attribs: List[Attrib],
    ):
        super(Box, self).__init__()
        self.label = label
        self.occluded = occluded
        self.source = source
        self.xtl = xtl
        self.ytl = ytl
        self.xbr = xbr
        self.ybr = ybr
        self.z_order = z_order
        self.attribs = attribs

    @classmethod
    def parse(cls, instance: ET.Element) -> Instance:
        label = instance.attrib['label']
        occluded = int(instance.attrib['occluded'])
        source = instance.attrib['source']
        xtl = float(instance.attrib['xtl'])
        ytl = float(instance.attrib['ytl'])
        xbr = float(instance.attrib['xbr'])
        ybr = float(instance.attrib['ybr'])
        z_order = int(instance.attrib['z_order'])
        attribs = [Attrib.parse(attrib) for attrib in instance]
        return cls(label, occluded, source, xtl, ytl, xbr, ybr, z_order, attribs)

    @property
    def xml(self) -> ET.Element:
        attrib = {
            'label': self.label,
            'occluded': str(self.occluded),
            'source': self.source,
            'xtl': str(self.xtl),
            'ytl': str(self.ytl),
            'xbr': str(self.xbr),
            'ybr': str(self.ybr),
            'z_order': str(self.z_order),
        }
        ele = ET.Element(self.tag, attrib)
        ele.extend([attrib.xml for attrib in self.attribs])
        return ele
