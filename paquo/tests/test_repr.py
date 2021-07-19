import tempfile

import pytest
import shapely.geometry


@pytest.fixture(scope='function')
def new_project(tmp_path):
    from paquo.projects import QuPathProject
    yield QuPathProject(tmp_path / "paquo-project", mode='x')


@pytest.fixture(scope='module')
def image_entry(svs_small):
    from paquo.projects import QuPathProject
    with tempfile.TemporaryDirectory(prefix='paquo-') as tmpdir:
        qp = QuPathProject(tmpdir, mode='x')
        entry = qp.add_image(svs_small)
        yield entry


def test_repr_helper_fallback():
    from paquo._repr import repr_html, repr_svg
    obj_without_ipynb_repr = "a"
    assert repr(obj_without_ipynb_repr) == repr_html(obj_without_ipynb_repr)
    assert repr(obj_without_ipynb_repr) == repr_svg(obj_without_ipynb_repr)


def test_ipython_repr(new_project):
    assert new_project._repr_html_()


def test_pathobject_repr():
    from paquo._repr import repr_html
    from paquo.pathobjects import QuPathPathAnnotationObject
    p = QuPathPathAnnotationObject.from_shapely(
        roi=shapely.geometry.Point(1, 2)
    )
    assert repr_html(p)


def test_color_repr():
    from paquo._repr import repr_html
    from paquo.colors import QuPathColor
    c = QuPathColor.from_hex("#123456")
    assert repr_html(c)


def test_hierarchy_repr(image_entry):
    from paquo._repr import repr_html
    assert repr_html(image_entry.hierarchy)


def test_image_repr(image_entry, monkeypatch):
    from paquo._repr import repr_html
    assert repr_html(image_entry)
    assert repr_html(image_entry, compact=True)
