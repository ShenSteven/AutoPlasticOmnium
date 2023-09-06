#!/usr/bin/env python
# coding: utf-8
"""
@File   : stack.py
@Author : Steven.Shen
@Date   : 9/6/2023
@Desc   : 
"""


class Stack:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def size(self):
        return len(self.items)


def match(i, j):
    opens = '([{'
    closes = ')]}'
    return opens.index(i) == closes.index(j)


def syntaxChecker(string):
    stack = Stack()
    balanced = True
    for i in string:
        if i in '([{':
            stack.push(i)
        elif i in ')]}':
            if stack.is_empty():
                balanced = False
                break
            else:
                j = stack.pop()
                if not match(j, i):
                    balanced = False
                    break
    if not stack.is_empty():
        balanced = False
    return balanced


if __name__ == "__main__":
    pass
    print(syntaxChecker('([{}])'))

