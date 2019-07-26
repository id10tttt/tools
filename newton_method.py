#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 函数： f(x) 
# 导： f'(x)
# 点 (xn, f(xn)), 切线：y - f(xn) = f'(xn)(x - xn)
# y = f(xn) + f'(xn)(x - xn)
# 于x 轴的交点 xn+1
# xn+1，即f(xn) + f'(xn)(x - xn) = 0的值
# -> f(xn) + f'(xn)(xn+1 - xn) = 0
# -> xn+1 = xn - f(xn) / f'(xn)

# a 即 求开方的值
# eg. f(x) = x ** 2 - a, f'(x) = 2x
# xn+1 = xn - (xn ** 2 - a) / 2 * xn
#      = 1/2 * (xn + a / xn )

# 任意次方的开方
# xn+1 = xn - (xn ** k -a) / (k * (xn ** (k - 1))
#      = ((k - 1) / k) * xn + a / (k * (xn **(k - 1)))

def newton_method(xn_value, loop_time, a_value):
    for _ in range(loop_time):
        xn_value = 1/2 * (xn_value + a_value / xn_value)
        print(xn_value)

def newton_method_power(xn_value, loop_time, a_value, power_value=2):
    for _ in range(loop_time):
        xn_value = ((power_value - 1) / power_value) * xn_value + a_value / (power_value * (xn_value ** (power_value - 1)))
        print(xn_value)

if __name__ == '__main__':
    a = 3
    newton_method(1, 5, a)
    import math
    print('real: {}\n'.format(math.sqrt(a)))

    newton_method_power(1, 5, a, 3)
    print('real: {}\n'.format(math.pow(a, 1/3)))
