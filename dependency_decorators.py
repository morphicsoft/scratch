import importlib


class PropDict:

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


def import_class(class_path):
    module_path = '.'.join(class_path.split('.')[:-1])
    mod = importlib.import_module(module_path)
    klass = getattr(mod, class_path.split('.')[-1])
    return klass


class inputs:

    def __init__(self, **kwargs):
        self._input_dependencies = kwargs

    def __call__(self, C):

        inputs_dict = {k: import_class(v) for k, v in self._input_dependencies.items()}
        inputs = PropDict(**inputs_dict)
        setattr(C, 'input', inputs)
        return C


class outputs:
    def __init__(self, **kwargs):
        self._output_dependencies = kwargs

    def __call__(self, C):
        outputs_dict = {k: import_class(v) for k, v in self._output_dependencies.items()}
        outputs = PropDict(**outputs_dict)
        setattr(C, 'output', outputs)
        return C


@inputs(Foo='test_classes.Foo', Bar='test_classes.Bar')
@outputs(Baz='test_classes.Baz')
class C:

    def do_stuff(self):
        print("C")
        print(C.input.Foo)
        print(C.input.Bar)
        print(C.output.Baz)

        try:
            print(C.output.Foo)
        except AttributeError:
            print("There isn't an output model named Foo!")


@inputs(Foo='test_classes.Foo')
@outputs(Bar='test_classes.Bar')
class D:

    def do_stuff(self):
        print("C")
        print(self.input.Foo)
        print(self.output.Bar)

        try:
            print(self.output.Foo)
        except AttributeError:
            print("There isn't an output model named Foo!")


if __name__ == '__main__':
    c = C()
    c.do_stuff()

    d = D()
    d.do_stuff()

    print(D.input.Foo is C.input.Foo)
    print(D.output.Bar is C.input.Bar)
