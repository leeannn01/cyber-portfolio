---
title: "PIE TIMES - picoCTF Walkthrough"
date: 2025-03-27 21:30:00 +0800
categories: [CTF]
tags: [PIE,ELF,nm]
permalink: /pie-times/
---

# Challenge: PIE TIMES (picoCTF)

The *PIE TIMES* challenge was a great intro to how binaries behave under **PIE (Position Independent Executable)** mode. I didn’t craft an exploit for this challenge—instead, I focused on learning how to **use `nm`**, understand symbol offsets, and reason about address space layout under PIE.

## Reading the C Code
Here’s the source code provided in the challenge:

```c
#include <stdio.h>
#include <stdlib.h>

void win() {
    system("/bin/sh");
}

void vuln() {
    char buf[64];
    gets(buf);
}

int main() {
    vuln();
    return 0;
}
```

As someone without exploit knowledge, this code give some strong hints:
1.	win() function:
- It runs system("/bin/sh"), which gives a shell.
- But it is never called anywhere in the program.
- That’s the key: the challenge wants us to trigger win() indirectly.

2. gets(buf) in vuln():
- gets() is unsafe. It doesn’t check buffer size.
- The buffer is only 64 bytes, so a long input can overflow the stack.
- Classic setup for a buffer overflow → likely the intended attack vector.

3. main() calls vuln():
- This just sets up the vulnerable environment.

So overall, the structure of the code strongly suggests that the goal is to:
- Overflow the buffer in vuln()
- Overwrite the return address
- Redirect execution to win()

The fact that win() exists but is never used is the biggest red flag—and a core CTF trope.

## What is PIE?

When a binary is complied with PIE enabled, it is **loaded at a random base address in memeory** everytime it runs. This makes static analysis or hardcoded expoloits harder.

Instead of using fixed function addresses, we need to:
- Identify symbol **offsets**
- Get a l**eaked runtime address** (e.g. of main())
- Use these to calculate the real address of other functions like (win())

## Learning nm
I used `nm` to inspect the binary and location the **main** and **win** function offsets.

#### Usage:
```bash
nm binary | grep 'T'
```
This lists symbols in the binary with their **offsets** (if PIE is *enabled*) or **absolute address** (if PIE is *disabled*)

#### Sample Output:
```
00000470 T win
00000490 T main
000004b0 T vuln
```
These are the offsets from the base address in memory when PIE is ***enabled***.

### nm Output Symbols - What do they mean?
The letter in the middle tells you the symbol's type and location:

So T main means that the symbol main is located in the global text section.

## Calculating the Runtime Address
Once the offsets of main and win has been obtained, I used the runtime memory leak to calculate their actual address during program execution.

Let's say the remote server prints:
```
The address of main() is: 0x56556000
```

Knowing the **main** has an **offset** of **0x490** (from nm), I computed the **base address** as follows:
```text
base_address = leaked_main_address - main_offset
             = 0x56556000 - 0x490
             = 0x56555b70
```

Then, using the win offset (0x470), I computed its **runtime address**.
```text
win_address = base_address + win_offset
            = 0x56555b70 + 0x470
            = 0x565560e0
```
This method is cruicial for any explotation involving PIE binaries.

# Lessons Learned
- `nm` is essential for understandind symbol tables and offets in ELF binaries.
- PIE randomiser loads address - so always treat offsets and runtime addresses seperately. 
-Leakinig one known address (linke(main)) allows you to reconstruct the others.
- Understanding nm output helps in CTFs, reverse engineering and exploit dev.
- Reading the C code helps map out the vulnerabilityl and the intended exploit path.

## Hint Reflection
    Hint: Can you figure out what changed between the address you found locally and in the server ouput?

Answer: The base address changed, due to PIE. All offsets stay the same, but the runtime address depends on where the binary was loaded.

## Summary
This challenge was not about exploitation for me - it was baout developing confidence in tools like nm, interpreting C code patterns and learning how PIE impacts runtime memory layout. This knowledge sets the foundation for more advanced binary exploitation.