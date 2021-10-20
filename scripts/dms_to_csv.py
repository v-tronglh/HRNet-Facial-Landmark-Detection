import argparse
import csv
import cv2
import os
import sys
from pathlib import Path
from typing import List, Optional, cast

from tqdm import tqdm

sys.path.append(os.getcwd())

from vx.instance import Box, Instance, PointBase  # noqa: E402
from vx.label import Label  # noqa: E402

from utils.common import open_file  # noqa: E402

FACE = 'face'
CHIN = 'cam'
NOSTRIL = 'lomui'
RIGHT_EYEBROW = 'longmayphai'
LEFT_EYEBROW = 'longmaytrai'
RIGHT_EYE_CENTER = 'tammatphai'
LEFT_EYE_CENTER = 'tammattrai'
RIGHT_EYE = 'matphai'
LEFT_EYE = 'mattrai'
INNER_LIP_BORDER = 'moitrong'
OUTER_LIP_BORDER = 'moingoai'
NASAL_BRIDGE = 'songmui'
SKIP = 'skip'
NUM_JOINTS = 68
FACE_SIZE = 200.0

face_parts = [
    CHIN,
    LEFT_EYEBROW,
    RIGHT_EYEBROW,
    NASAL_BRIDGE,
    NOSTRIL,
    LEFT_EYE,
    RIGHT_EYE,
    OUTER_LIP_BORDER,
    INNER_LIP_BORDER,
]


def subpath(root: os.PathLike, dirname: os.PathLike) -> str:
    root = Path(root).resolve()
    dirname = Path(dirname).resolve()
    sub_parts: List[str] = []

    while str(root) != str(dirname) and len(root.parts) < len(dirname.parts):
        sub_parts.insert(0, dirname.name)
        dirname = dirname.parent

    return '/'.join(sub_parts)


def find_instance_by_label(instances: List[Instance], label: str) -> Optional[Instance]:
    res = None

    for instance in instances:
        if instance.label == label:  # type: ignore
            res = instance
            break

    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dirname')
    parser.add_argument('outdir')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--xml-pattern', nargs='*')
    group.add_argument('--file')
    parser.add_argument('--train-ratio', type=float, default=0.8)
    parser.add_argument('--val-ratio-in-train', type=float, default=0.2)
    args = parser.parse_args()

    dirname = Path(args.dirname)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.xml_pattern:
        xml_files = [xml_file for xml_pattern in args.xml_pattern for xml_file in dirname.glob(xml_pattern)]
    else:
        with open(args.file, newline='') as f:
            csv_reader = csv.reader(f)
            next(csv_reader)

            xml_files = [xml_file for row in csv_reader for xml_file in Path(row[4]).glob('*.xml')]

    train_split = xml_files[:round(args.train_ratio * len(xml_files))]
    test_split = xml_files[round(args.train_ratio * len(xml_files)):]
    val_split = train_split[- round(args.val_ratio_in_train * len(train_split)):]
    train_split = train_split[:- round(args.val_ratio_in_train * len(train_split))]

    split_mapping = {
        'train': train_split,
        'val': val_split,
        'test': test_split,
    }

    for split_name, split in split_mapping.items():
        print(f'Processing {split_name}...')
        outfile = str(outdir.joinpath(f'{split_name}.csv'))

        with open_file(outfile, mode='w', newline='') as f:
            csv_writer = csv.writer(f)

            # Header
            row = [
                'image_name',
                'scale',
                'center_w',
                'center_h',
            ]

            for i in range(NUM_JOINTS):
                for c in ['x', 'y']:
                    row.append(f'original_{i}_{c}')

            csv_writer.writerow(row)

            # Rows
            for xml_file in tqdm(split):
                try:
                    label = Label.fromfile(xml_file)
                    im_dir = xml_file.with_name('images')

                    for frame in label.frames:
                        if find_instance_by_label(frame.instances, SKIP):
                            continue

                        im_file = im_dir.joinpath(frame.name)

                        # image_name
                        image_name = subpath(xml_file.parent.parent, im_file)
                        image_name = '/'.join(['images', image_name])

                        if ',' in image_name or ' ' in image_name:
                            raise RuntimeError(f'There is a comma or space in {image_name}.')

                        # scale, center
                        face = cast(Box, find_instance_by_label(frame.instances, FACE))

                        if face:
                            scale = (face.ybr - face.ytl + 1) / FACE_SIZE
                            center_w = (face.xtl + face.xbr) / 2
                            center_h = (face.ytl + face.ybr) / 2
                        else:
                            raise RuntimeError(f'No {FACE} found in {xml_file}, frame #{frame.id}.')

                        row = [
                            image_name,
                            str(scale),
                            str(center_w),
                            str(center_h),
                        ]

                        for face_part in face_parts:
                            face_part_inst = cast(PointBase, find_instance_by_label(frame.instances, face_part))

                            if face_part_inst:
                                for point in face_part_inst.points:
                                    row.append(str(point[0]))
                                    row.append(str(point[1]))
                            else:
                                raise RuntimeError(f'No {face_part} found in {xml_file}, frame #{frame.id}.')

                        if len(row) == 4 + NUM_JOINTS * 2:
                            csv_writer.writerow(row)

                            out_im_file = outdir.joinpath(image_name)
                            out_im_file.parent.mkdir(parents=True, exist_ok=True)

                            image = cv2.imread(str(im_file))
                            cv2.imwrite(str(out_im_file), image)
                except Exception as e:
                    print(e)
