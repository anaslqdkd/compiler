def fn(n):
    if n == 0:
        print(10)
        return 1
    else:
        print(1)
        a = fn(n-1)
        return a
fn(10)
