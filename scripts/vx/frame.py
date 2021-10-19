from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import List, Type, cast

from .base import Element
from .instance import Box, Instance, Points, Polygon, Polyline


class Frame(Element):
    tag = 'image'
    supported_instances: List[Type[Instance]] = [
        Polygon,
        Polyline,
        Points,
        Box,
    ]

    def __init__(self, height: int, id_: int, name: str, width: int, instances: List[Instance]):
        super(Frame, self).__init__()
        self.height = height
        self.id = id_
        self.name = name
        self.width = width
        self.instances = instances

    @classmethod
    def parse(cls, frame: ET.Element) -> Frame:
        if frame.tag != cls.tag:
            raise RuntimeError(f'Incompatitable tag, {cls.tag} required, {frame.tag} found.')

        height = int(frame.attrib['height'])
        id_ = int(frame.attrib['id'])
        name = frame.attrib['name']
        width = int(frame.attrib['width'])
        instances = []

        for instance in frame:
            for supported_instance in cls.supported_instances:
                if instance.tag == supported_instance.tag:
                    instances.append(cast(Instance, supported_instance.parse(instance)))

        return cls(height, id_, name, width, instances)

    @property
    def xml(self) -> ET.Element:
        attrib = {
            'height': str(self.height),
            'id': str(self.id),
            'name': self.name,
            'width': str(self.width),
        }
        ele = ET.Element(self.tag, attrib)
        ele.extend([instance.xml for instance in self.instances])
        return ele
