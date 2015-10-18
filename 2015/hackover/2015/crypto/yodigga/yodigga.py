#!/usr/bin/env python

import hashlib
import math
import re
import sys
import base64


FLAG = 'hackover15{trolololol}'
SAFETY_RE = 'hack' 'over' r'15\{([^\}]+)\}'
P = """
AD107E1E 9123A9D0 D660FAA7 9559C51F A20D64E5 683B9FD1
B54B1597 B61D0A75 E6FA141D F95A56DB AF9A3C40 7BA1DF15
EB3D688A 309C180E 1DE6B85A 1274A0A6 6D3F8152 AD6AC212
9037C9ED EFDA4DF8 D91E8FEF 55B7394B 7AD5B7D0 B6C12207
C9F98D11 ED34DBF6 C6BA0B2C 8BBC27BE 6A00E0A0 B9C49708
B3BF8A31 70918836 81286130 BC8985DB 1602E714 415D9330
278273C7 DE31EFDC 7310F712 1FD5A074 15987D9A DC0A486D
CDF93ACC 44328387 315D75E1 98C641A4 80CD86A1 B9E587E8
BE60E69C C928B2B9 C52172E4 13042E9B 23F10B0E 16E79763
C9B53DCF 4BA80A29 E3FB73C1 6B8E75B9 7EF363E2 FFA31F71
CF9DE538 4E71B81C 0AC4DFFE 0C10E64F
"""
G = """
AC4032EF 4F2D9AE3 9DF30B5C 8FFDAC50 6CDEBE7B 89998CAF
74866A08 CFE4FFE3 A6824A4E 10B9A6F0 DD921F01 A70C4AFA
AB739D77 00C29F52 C57DB17C 620A8652 BE5E9001 A8D66AD7
C1766910 1999024A F4D02727 5AC1348B B8A762D0 521BC98A
E2471504 22EA1ED4 09939D54 DA7460CD B5F6C6B2 50717CBE
F180EB34 118E98D1 19529A45 D6F83456 6E3025E3 16A330EF
BB77A86F 0C1AB15B 051AE3D4 28C8F8AC B70A8137 150B8EEB
10E183ED D19963DD D9E263E4 770589EF 6AA21E7F 5F2FF381
B539CCE3 409D13CD 566AFBB4 8D6C0191 81E1BCFE 94B30269
EDFE72FE 9B6AA4BD 7B5A0F1C 71CFFF4C 19C418E1 F6EC0179
81BC087F 2A7065B3 84B890D3 191F2BFA
"""


def conditional_escape(x, n):
    if n <= 0:
        n = 42
    cnt = 0
    i = n
    while i != 1:
        if i & 1:
            i = 3*i + 1
        else:
            i = i // 2
        cnt += 1

    if cnt > 1337 + math.sqrt(n):
        return x
    return re.escape(x)


def check_magic(x):
    if len(x) < 16384:
        return False
    m1, m2 = x[43:8043], x[8043:16043]
    try:
        m1 = base64.b64decode(m1)
        m2 = base64.b64decode(m2)
    except ValueError:
        return False
    security1 = secure_hash(m1) == secure_hash(m2)
    security2 = x.endswith('yodigga!')
    security3 = diffie_hellman(ord(x[23]), ord(x[42]), ord(x[31]))
    return security1 and security2 and security3


def secure_hash(msg):
    return hashlib.md5(msg).digest()[:6] + hashlib.sha512(msg).digest()[:6]


def diffie_hellman(a, b, c):
    return pow(make_int(G), c, make_int(P)) & 0xffff == a * b


def make_int(x):
    return int(x.replace(' ', '').replace('\n', ''), 16)


def print_source(regexp, n):
    if not regexp:
        regexp = re.escape(r'SECRET_KEY\=4GwlhWYAm4ysc4/KvwMArjBSAU')
    sys.stdout.write('\n')
    with open(__file__) as f:
        source_code = f.read()
        source_code = re.sub(conditional_escape(regexp, n) + '|' + SAFETY_RE,
                             'hackover15{trolololol}', source_code)
        sys.stdout.write(source_code)
        sys.stdout.write('\n')


def main():
    sys.stdout.write('What do you want? flag? source? maoam?\n')

    while True:
        sys.stdout.write('cmd: ')
        sys.stdout.flush()
        line = sys.stdin.readline().strip()
        if line.startswith('flag'):
            sys.stdout.write('Not that easy!\n')
            continue
        if line.startswith('source'):
            args = line.split()
            if len(args) < 2:
                args.append('')
                args.append('42')
            elif len(args) < 3:
                args.append('42')
            try:
                n = int(args[2])
            except ValueError:
                n = 42
            print_source(args[1], n)
            continue
        if line.startswith('gimmeflag'):
            if check_magic(line):
                sys.stdout.write(FLAG)
                sys.stdout.write('\n')
            continue
        if line.startswith('maoam'):
            sys.stdout.write('I wish there were real life adblockers ...\n')
            continue


if __name__ == '__main__':
    main()
