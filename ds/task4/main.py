def anagrams(s, prefix=''):
    if len(s) == 0:
        print(prefix)
    else:
        for i in range(len(s)):
            anagrams(s[:i] + s[i+1:], prefix + s[i])

anagrams('red')
