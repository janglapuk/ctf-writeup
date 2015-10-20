# Hackover 2015 CTF: yodigga

----------
## Challenge details
| Contest        | Challenge     | Category  | Points |
|:---------------|:--------------|:----------|-------:|
| Hackover CTF | yodigga  | Crypto | 500  |

*Description*
>Watch out for trolls, they bite.

>`nc yodigga.hackover.h4q.it 1342`

----------

## Write-up
After connecting to the server using `nc`, I faced some prompts who asking me to input the commands.

```
What do you want? flag? source? maoam?
cmd: flag
Not that easy!

cmd: maoam
I wish there were real life adblockers ...

cmd: source
```
and the *censored* server source code appeared (please check on this repo file named `yodigga.py`).

So, we need to analyzing the source code to give a proper command.

### Hint #1
```python
if line.startswith('gimmeflag'):
    if check_magic(line):
        sys.stdout.write(FLAG)
        sys.stdout.write('\n')
```
So, we need a command starts with `gimmeflag`.

### Hint #2
Second interesting code in `check_magic(x)` function is:
```python
def check_magic(x):
    if len(x) < 16384:
        return False
    ...
```
The command length **not less than 16,384** characters.

### Hint #3
Third interesting code in `check_magic(x)` function is:
```python
m1, m2 = x[43:8043], x[8043:16043]
try:
    m1 = base64.b64decode(m1)
    m2 = base64.b64decode(m2)
except ValueError:
    return False
```
We need to get two encoded strings using `base64` at offset **43-8043** and offset **8043-16043**.

### Hint #4
This part of the codes related with **hint #3** above. Still on `check_magic(x)` function:
```python
security1 = secure_hash(m1) == secure_hash(m2)
```
This part is checking the hash of two decoded strings using MD5. So, we need to make two of decoded string identical.

### Hint #5
```python
security2 = x.endswith('yodigga!')
```
Of course, the command must be ended with `yodigga!` string.

### Hint #6
```python
security3 = diffie_hellman(ord(x[23]), ord(x[42]), ord(x[31]))
```
Well, there is a Diffie Hellman (?) function who passing three arguments value with 1 byte size for each arguments.

I don't know what DH algorithm is, so I dig that function to find out what happened with DH function:
```python
P = """
AD107E1E 9123A9D0 D660FAA7 9559C51F A20D64E5 683B9FD1
B54B1597 B61D0A75 E6FA141D F95A56DB AF9A3C40 7BA1DF15
... and many more ...
"""

G = """
AC4032EF 4F2D9AE3 9DF30B5C 8FFDAC50 6CDEBE7B 89998CAF
74866A08 CFE4FFE3 A6824A4E 10B9A6F0 DD921F01 A70C4AFA
... and many more ...
"""

def diffie_hellman(a, b, c):
    return pow(make_int(G), c, make_int(P)) & 0xffff == a * b

def make_int(x):
    return int(x.replace(' ', '').replace('\n', ''), 16)
```
The `diffie_hellman` function returning a boolean value. Our concents is how to make the passed arguments meets `true` condition.

### Hint #7
Back to `check_magic` function:
```python
return security1 and security2 and security3
```
Of course, all conditions need to meets `true` to make sure our command is a good stuff.

## Solution
I needed to craft a command. Referred into **hint #1** and **hint #5**, we needed `gimmeflag` string at the first and `yodigga!` string at the end:
```python
startwith = "gimmeflag"
endwith = "yodigga!"
```

Next, referred into hint #2, I need make the command length **not less than 16,384** characters, including `startwith` and `endwith`:
```python
startwith = "gimmeflag"
endwith = "yodigga!"
command = startwith + "A"*16367 + endwith
```

Next, referred into hint #3, I need insert two `base64` encoded string at offset 43-8043 and offset 8043-16043. To make sure that I have proper encoded string
and avoiding unnecessary padding, I will use `SPB` string to make encoded string `U1BC` have 4 bytes length, so I will repeat `UIBC` string until length reached 16,000 (8043-43)+(16043-8043) for the first encoded string and the second encoded string.
```python
startwith = "gimmeflag"
endwith = "yodigga!"
command = startwith + "A"*34 + "U1BC"*4000 + "A"*335 + endwith # 16000 / len("U1BC") = 4000
```

Referred into hint #6, I needed to pass three arguments (1 byte) at offset 23 as `a` argument, offset 42 as `b` argument, and offset 31 as `c` argument. Of course I need to place those arguments at proper offset. The argument values still don't know, we will find out later.
```python
startwith = "gimmeflag"
endwith = "yodigga!"
arg_a = '\0' # offset 23
arg_b = '\0' # offset 42
arg_c = '\0' # offset 31
command = startwith + "A"*14 + arg_a + "A"*7 + arg_c + "A"*10 + arg_b + "U1BC"*4000 + "A"*335 + endwith # 16000 / len("U1BC") = 4000
```

I close to the party. But, I need to make sure `diffie_hellman` function returning `true` condition. So, I need to find out what are the proper argument values. I need to write small tool written in Python to simulate `diffie_hellman` return value:
```python
import math

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

def make_int(x):
    return int(x.replace(' ', '').replace('\n', ''), 16)

def diffie_hellman(c):
    return pow(make_int(G), c, make_int(P)) & 0xffff

for i in xrange(255+1):
	dh = diffie_hellman(i)
	print 'Value: %d' % i + ' = ' + str(dh) + ' | Multiplier: %f' % math.sqrt(dh)

# the condition is:
# 1. pow() function is integer return value, max 65535
# 2. 'a' and 'b' arguments are 1 byte, mean 255 for the number
# so, we need to find out what is square root of 'dh' and the return is integer (no decimal places)
# to place that sqrt's value into 'a' and 'b'
```

After executing the script, I got the output like this:
```
~/hackover/yodigga$ python dh_check.py
Value: 0 = 1 | Multiplier: 1.000000
Value: 1 = 11258 | Multiplier: 106.103723
Value: 2 = 42245 | Multiplier: 205.535885
Value: 3 = 26700 | Multiplier: 163.401346
Value: 4 = 11583 | Multiplier: 107.624347
Value: 5 = 51454 | Multiplier: 226.834742
Value: 6 = 47641 | Multiplier: 218.268184
Value: 7 = 60316 | Multiplier: 245.593160
Value: 8 = 60608 | Multiplier: 246.186921
Value: 9 = 59819 | Multiplier: 244.579231
Value: 10 = 16416 | Multiplier: 128.124939
Value: 11 = 15608 | Multiplier: 124.931981
Value: 12 = 41236 | Multiplier: 203.066492
Value: 13 = 32845 | Multiplier: 181.231896
Value: 14 = 44436 | Multiplier: 210.798482
Value: 15 = 36068 | Multiplier: 189.915771
Value: 16 = 36656 | Multiplier: 191.457567
Value: 17 = 3532 | Multiplier: 59.430632
... and more ...
... and more ...
... and more ...
Value: 250 = 47834 | Multiplier: 218.709853
Value: 251 = 55839 | Multiplier: 236.302772
Value: 252 = 57636 | Multiplier: 240.074988
Value: 253 = 62608 | Multiplier: 250.215907
Value: 254 = 19387 | Multiplier: 139.237208
Value: 255 = 43720 | Multiplier: 209.09328
```
There's no sqrt-ed value have an integer, except value **0**. Finnaly, I got the proper values for `a`, `b`, and `c` arguments.

Let's modify the command again:
```python
startwith = "gimmeflag"
endwith = "yodigga!"
arg_a = '\1' # offset 23
arg_b = '\1' # offset 42
arg_c = '\0' # offset 31
command = startwith + "A"*14 + arg_a + "A"*7 + arg_c + "A"*10 + arg_b + "U1BC"*4000 + "A"*335 + endwith # 16000 / len("U1BC") = 4000
```

## Execution
The challenge is using `nc` tool to communicating with their server. But, `nc` have input length limitation up to 1024 characters.
I cannot send my very-very long command. Don't worry, there is [pwntools](https://github.com/Gallopsled/pwntools) to help our problem.

With using Python, just fire up `python` as interactive shell and make a simple code:
```python
>>> from pwn import *
>>> r = remote('yodigga.hackover.h4q.it', 1342)
[*] Opening connection to yodigga.hackover.h4q.it on port 1342:
[*] Opening connection to yodigga.hackover.h4q.it on port 1342: Trying 46.101.139.76
[+] Opening connection to yodigga.hackover.h4q.it on port 1342: Done
>>> startwith = "gimmeflag"
>>> endwith = "yodigga!"
>>> arg_a = '\1'
>>> arg_b = '\1'
>>> arg_c = '\0'
>>> command = startwith + "A"*14 + arg_a + "A"*7 + arg_c + "A"*10 + arg_b + "U1BC"*4000 + "A"*335 + endwith
>>> r.send(command + '\n')
>>> r.interactive()
hackover15{noNeedToBreakDHright?}
```

## Conclusion
Flag is `hackover15{noNeedToBreakDHright?}`
