#!/usr/bin/python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: FAFOL

import base64
import json
import os
import sys
import zlib
from typing import Sequence

os.system('')

CHARACTERS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ:'
SIGNALMAP = {
    ':': {'name': 'rail-signal', 'type': 'item'}
}
for char in CHARACTERS:
    if char not in SIGNALMAP:
        SIGNALMAP[char] = {'name': f'signal-{char}', 'type': 'virtual'}
COLORS = {
    '\033[31m': 'red',
    '\033[32m': 'green',
    '\033[33m': 'yellow',
    '\033[34m': 'blue',
    '\033[35m': 'pink',
    '\033[36m': 'cyan',
    '\033[37m': 'white',
    '\033[0m': 'reset'
}
for code, color in COLORS.items():
    SIGNALMAP[color] = {'name': f'signal-{color}', 'type': 'virtual'}
CURRENT_COLOR = 'White'
COLOR_COMMAND = ''


def chunks(lst: Sequence, n: int) -> Sequence:
    """Yield successive n-sized chunks from lst.

    Args:
        lst (Sequence): a sequence to chunk up
        n (int): the size of chunk to generate

    Returns:
        Sequence: An n-sized chunk of the input sequence
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def encode_bp(data: dict) -> str:
    """
    Generate a Factorio blueprint exchange string per https://wiki.factorio.com/Blueprint_string_format

    Args:
        data (dict): A Factorio blueprint

    Returns:
        str: A Factorio exchange string
    """
    json_str = json.dumps(
        data,
        separators=(',', ':'),
        ensure_ascii=False
    ).encode('utf8')
    compressed = zlib.compress(json_str, 9)
    encoded = base64.b64encode(compressed)
    return '0' + encoded.decode()


def clean_text(text: str) -> str:
    """
    Strip off ANSI color codes from text

    Args:
        text (str): Text to strip

    Returns:
        str: Text without ANSI codes
    """
    for code, color in COLORS.items():
        text = text.replace(code, '')
    return text


def make_bp(text: str, signals: dict) -> dict:
    """
    Make a dictionary representing a Factorio blueprint, with one or more combinators containing the signals

    Args:
        text (str): The text the signals represent
        signals (dict): The signals

    Returns:
        dict: A Factorio blueprint
    """
    text = clean_text(text)
    data = {
        'blueprint': {
            'item': 'blueprint',
            'label': text.replace('\n', ' -- '),
            'description': text,
            'version': 281479274823680,
            'icons': [
                {
                    'index': 1,
                    'signal': {
                        'name': 'constant-combinator',
                        'type': 'item'
                    }
                }
            ],
            'entities': [

            ]
        }
    }
    entity_number = 1
    for signal_chunk in chunks(list(signals.keys()), 20):
        data['blueprint']['entities'].append(
            {
                'direction': 4,
                'entity_number': entity_number,
                'name': 'constant-combinator',
                'position': {'x': entity_number-1, 'y': 0},
                'control_behavior': {
                    'filters': [

                    ]
                }
            }
        )
        for idx, signal in enumerate(signal_chunk):
            value = signals[signal]
            data['blueprint']['entities'][-1]['control_behavior']['filters'].append(
                {
                    'count': value,
                    'index': idx+1,
                    'signal': {
                        'name': SIGNALMAP[signal]['name'],
                        'type': SIGNALMAP[signal]['type']
                    }
                }
            )
        entity_number += 1
    return data


if __name__ == '__main__':
    signals = {}
    with open(sys.argv[1], encoding='utf-8') as f:
        text = f.read().replace('\\033', '\033')
        lines = text.split('\n')
        if len(lines) > 2:
            print(f'The number of lines shall be <=2! Not {len(lines)}')
            sys.exit(-300)

        if any(map(lambda x:len(clean_text(x))-16,lines)):
            print('The number of characters shall be <=16!')
            #sys.exit(-400)

        print(text)

        for lidx, line in enumerate(lines):
            cidx = 0
            for char in line:
                # handle color
                if char == '\033':
                    COLOR_COMMAND = char
                    print(f'Line {lidx}, char {cidx}: Starting color!')
                    continue
                elif COLOR_COMMAND != '':
                    COLOR_COMMAND += char
                    if char != 'm':
                        continue
                    if COLORS[COLOR_COMMAND] == 'reset':
                        print(f'\t Stopping {CURRENT_COLOR}{COLOR_COMMAND}')
                        CURRENT_COLOR = 'white'
                        COLOR_COMMAND = ''
                    else:
                        print(
                            f'\tChanging from {CURRENT_COLOR} {COLOR_COMMAND}to {COLORS[COLOR_COMMAND]}')
                        CURRENT_COLOR = COLORS[COLOR_COMMAND]
                        COLOR_COMMAND = ''
                else:
                    # handle text character
                    char = char.upper()
                    if char == ' ':
                        cidx += 1
                        continue
                    if char not in CHARACTERS:
                        if char not in '\n':
                            print(f'Bad char, skipping: "{char}"')
                        continue
                    if CURRENT_COLOR != 'white' and CURRENT_COLOR not in signals:
                        signals[CURRENT_COLOR] = 0
                    if char not in signals:
                        signals[char] = 0
                    newidx = (2**cidx) << lidx * 16
                    print(
                        f'Line {lidx}, char {cidx}: Placing a {char} at {newidx}')
                    signals[char] += newidx
                    if CURRENT_COLOR != 'white':
                        signals[CURRENT_COLOR] += newidx
                    cidx += 1

        '''for signal, value in signals.items():
            print(f'{signal}:{value}')'''
        bp = make_bp(text, signals)
        print(encode_bp(bp))
