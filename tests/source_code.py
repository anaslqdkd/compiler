a = [5, 7] * 2
print(a, a[3])
b = [1, "a"] + [2, "b"]
print(b, b[2])
str = "hello"
print(str, str[1])
u = 10
tab = [1, 2, u]
print(tab, tab[2])
s = 1
t = 2

def f():
    if s < t:
        c = a[0] * a[1]
        d = 1 + 2 * 3
        e = c + d
        return e
x = f()
print(x)