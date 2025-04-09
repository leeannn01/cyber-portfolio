import sys

def unscramble(L):
    A = L
    i = len(A) - 1
    while i >= 2:
        prefix = A[i-1].pop()  # Remove the appended slice
        
        n = len(A[i-1])        # Number of elements that were merged
        original = A[i-2][-n:] # Extract original merged part
        A[i-2] = A[i-2][:-n]   # Remove merged part from i-2

        A.insert(i-1, original)  # Re-insert as separate element

        i -= 1
    return A

def main(file):
  scrambled_flag = eval(open(file, 'r').read())
  flag_hex = unscramble(scrambled_flag)
  for c in flag_hex:
    print(chr(int(c[0], 16)), end='')

if __name__ == '__main__':
  main(sys.argv[1])