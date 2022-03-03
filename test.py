# 描述器
class CheckInt:

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if isinstance(value, int):
            instance.__dict__[self.name] = value
        else:
            raise AttributeError('please input an int.')


# 类似函数的形式
class A:
    score = CheckInt('score')
    age = CheckInt('age')

    def __init__(self, name, score, age):
        self.name = name  # 普通属性
        self.score = score
        self.age = age


a = A('Bob', 90, 30)
setattr(a, 'vers', 80)
print(a.vers)

# a = A('Bob', '90', 30)

# 装饰器函数
def check(func):
    def inner():
        print("装饰器函数")
        func()
        print("装饰完")

    return inner


@check
def get_married():
    print('我要当新娘啦')


get_married()


# 装饰器类
class MakeUp:
    def __init__(self, func):
        self.f = func

    def __call__(self, *args, **kwargs):
        print("化妆")
        self.f()
        print("化妆完了")


@MakeUp
def get_married2():
    print('我要当新娘啦')


get_married2()
