import pytest


@pytest.fixture(scope='session')
def pathclass():
    from paquo.classes import QuPathPathClass
    yield QuPathPathClass("MyClass")


def test_pathclass_creation():
    from paquo.classes import QuPathPathClass

    with pytest.raises(TypeError):
        QuPathPathClass.from_java("abc")

    pc = QuPathPathClass("MyClass", color=None)
    assert pc.parent is None
    assert pc.name == pc.id == "MyClass"
    assert pc.is_valid
    assert "MyClass" in repr(pc)


def test_deny_name_none_creation():
    from paquo.classes import QuPathPathClass
    with pytest.raises(NotImplementedError):
        # noinspection PyTypeChecker
        QuPathPathClass(None, parent=None)

    pc = QuPathPathClass("MyClass")
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        QuPathPathClass(None, parent=pc)


def test_incorrect_parent_type():
    from paquo.classes import QuPathPathClass
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        QuPathPathClass("new class", parent="parent_class")


def test_incorrect_class_name():
    from paquo.classes import QuPathPathClass
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        QuPathPathClass(1)
    with pytest.raises(ValueError):
        QuPathPathClass("my::class")


def test_pathclass_equality(pathclass):
    from paquo.classes import QuPathPathClass
    other = QuPathPathClass("MyClass2")
    same = QuPathPathClass("MyClass")
    assert pathclass == pathclass
    assert pathclass != other
    assert pathclass == same
    assert pathclass != 123


def test_pathclass_creation_with_parent(pathclass):
    from paquo.classes import QuPathPathClass
    pc = QuPathPathClass("MyChild", parent=pathclass)
    assert pc.parent == pathclass
    assert pc.name == "MyChild"
    assert pc.id == "MyClass: MyChild"

    assert pc.origin == pathclass
    assert pc.is_derived_from(pathclass)
    assert not pc.is_ancestor_of(pathclass)
    assert not pathclass.is_derived_from(pc)
    assert pathclass.is_ancestor_of(pc)
    assert pc.is_derived_class
    assert not pathclass.is_derived_class


def test_pathclass_colors():
    from paquo.classes import QuPathPathClass
    pc = QuPathPathClass("MyNew", color=None)
    my_class_color = (49, 139, 153)  # based on string MyNew
    assert pc.color.to_rgb() == my_class_color

    pc = QuPathPathClass("MyNew2", color=(1, 2, 3))
    assert pc.color.to_rgb() == (1, 2, 3)

    pc.color = "#ff0000"
    assert pc.color.to_rgb() == (255, 0, 0)


def test_pathclass_none_colors():
    from paquo.classes import QuPathPathClass
    pc = QuPathPathClass("MyNew")
    pc.color = None
    assert pc.color is None
