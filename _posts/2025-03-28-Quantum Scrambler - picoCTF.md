---
title: "Quantum Scrambler – picoCTF Walkthrough"
date: 2025-03-28 00:30:00 +0800
categories: [CTF, Python Reversing]
tags: [reverse engineering, string manipulation, eval, recursion]
permalink: /quantum-scrambler/
---

# Challenge: Quantum Scrambler (picoCTF)

### **Description**:  
> We invented a new cypher that uses "quantum entanglement" to encode the flag. Do you have what it takes to decode it?

### **Hints**:
> 1. Run `eval` on the cypher to interpret it as a Python object  
> 2. Print the outer list one object per line  
> 3. Feed in a known plaintext through the scrambler


## Observation once connected

When I connected to the VM running the challenge, I got something like this:
```
[[‘0x70’, ‘0x69’],
[‘0x63’, [], ‘0x6f’],
[‘0x43’, [[‘0x70’, ‘0x69’]], ‘0x54’],
…
]
```
This looked very weird at first — some kind of **nested Python list** where every value was either a hexadecimal character, a list, or both. Definitely not your average cipher.

## Thought Process

### Step 1: Spotting the Hex

The output was full of strings like '0x70', '0x69', etc.

I knew immediately these were ASCII codes in hexadecimal. For example:

```python
chr(int('0x70', 16)) == 'p'
```
This means that the flag characters are hidden inside this tree, in hex form.

### Step 2: Realising it's a Tree
```python
['0x70', '0x69']
['0x63', [], '0x6f']
['0x46', [[...], [...]], '0x7b']
```
This made me realize: each element is a node in a tree, and the leaf nodes are hex values.

### Step 3: Saving the Output
When I ran the challenge and saw that huge nested structure dumped into the terminal, I copied the full output and saved it locally:
```bash
nano output.txt
# (Paste everything from the challenge)
```
This gave me a static file to experiment on locally.

### Step 4: Evaluating the Structure
The hint mentioned to use eval() - so I did:
```python
with open("output.txt") as f:
    data = eval(f.read())
```

I then printed the first few lines to confirm:
```python
for item in data[:5]:
    print(item)
```

This confirmed that the structure was exactly what I saw on the server: deeply nested lists containing hex strings and more lists.

### Step 5: Understanding the Scramble
Before jumping into reversing the actual flag, I wanted to understand what the scrambler was doing. So, I modified the get_flag() function in quantum_scrambler.py to return a simple test string like "abcde"

```python
def get_flag():
    test = "abcde"
    hex_flag = []
    for c in test:
        hex_flag.append([str(hex(ord(c)))])
    return hex_flag
```

This produced:
```python
[['0x61'], ['0x62'], ['0x63'], ['0x64'], ['0x65']]
```

After running the scrmabler() function on it, I observed the following:
```python
[['0x61', '0x62'], ['0x63', [], '0x64'], ['0x65', [['0x61', '0x62']]]]
```
- The list shrinks as elements are merged.
- Earlier items absorb later ones.
- The scrambler appends a breadcrumb slice (A[:i-2]) into the current item.
- The final result is a tree-like object with nested structures.

## Dissecting quantum_scrambler.py
The key logic in the scrambler was:
```python
def scramble(L):
    A = L
    i = 2
    while (i < len(A)):
        A[i-2] += A.pop(i-1)
        A[i-1].append(A[:i-2])
        i += 1
```
What This Does:
- **Merge** A[i-2] += A.pop(i-1) -- combines two elements, shrinking the list
- **Track**: A[i-1].append(A[:i-2]) -- logs a reference to the previous structure
- The result is a deeply nested list that contains all transformation history

## Building unscramble.py - Reversing the Process
Knowing how the scramble worked, I wrote the reverse logic to:
1. Walk backwards from the end of the list.
2. Pop off the "breadcrumb" log.
3. Reconstruct the original values from the merged item.
4. Insert the split pieces back in

Here is my unscramble.py:
```python
import sys

def unscramble(L):
    A = L
    i = len(A) - 1
    while i >= 2:
        prefix = A[i-1].pop()
        n = len(A[i-1])
        original = A[i-2][-n:]
        A[i-2] = A[i-2][:-n]
        A.insert(i-1, original)
        i -= 1
    return A

def main(file):
    scrambled_flag = eval(open(file, 'r').read())
    flag_hex = unscramble(scrambled_flag)
    for c in flag_hex:
        print(chr(int(c[0], 16)), end='')

if __name__ == '__main__':
    main(sys.argv[1])
```

### Output
Running the script:
```bash
python3 unscramble.py output.txt
```

Returned:
```
picoCTF{python_is_weirdaa2ca6fc}
```

## Lessons Learned:
- How to analyse recursive list manipulation in Python
- Feeding a unknown plaintext is a powerful strategy to understand a black-box logic
- Reverse engineering does not require reverse encryption - sometimes it is just smart data transformation
- Strucure carries more meaning than it first appears

## Hint Reflection
    "Run eval on cypher..."
    - Essential for treating the object as Python

    "Print the outerlist one object per line..."
    - Helped visually understand the tree structure

    "Feed in a unknown plaintext..."
    - Cruicial for revealing how scrambling actually works

## Files
[Download unscramble.py](https://github.com/leeannn01/cyber-portfolio/blob/main/projects/ctf-challenges/picoCTF/quantum-scrambler/unscramble.py)
[Download ouput.txt](https://github.com/leeannn01/cyber-portfolio/blob/main/projects/ctf-challenges/picoCTF/quantum-scrambler/output.txt)

# Summary
The Quantum Scrambler challenge was about decoding structure, not cryptography. With a clear test input, a careful read of the scramble logic, and a methodical reversal, I was able to extract the flag cleanly. This one sharpened my skills in Python, recursion, and debugging by dissection.