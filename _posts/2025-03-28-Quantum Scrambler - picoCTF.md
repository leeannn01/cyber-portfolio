---
title: "Quantum Scrambler – picoCTF Walkthrough"
date: 2025-03-28 00:30:00 +0800
categories: [CTF, Python Reversing]
tags: [picoCTF, reverse engineering, string manipulation, eval, recursion]
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

### Dissecting the Source

When I opened quantum_scrambler.py, I saw that it defines a scramble() function, which constructs a deeply nested list-like structure. It takes characters from a flag and wraps them in multiple layers of lists, sometimes combining them with other characters or other wrapped structures.


### Step 1: Spotting the Hex

The script was full of strings like '0x70', '0x69', etc.

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

## Building unscramble.py