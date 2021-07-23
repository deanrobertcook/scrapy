
class TestClass:

    def __init__(self, name):
        self.name = name

    def inst_method(self):
        print(f"Here we have the instance method on {self.name}")

    @classmethod
    def some_method(cls):
        inst = cls("test")
        inst.inst_method()


TestClass.some_method()
