import pathlib
import collections.abc as collections_abc
from typing import Union, Iterable, Tuple, Optional, Iterator, Collection, List, Dict

from paquo._base import QuPathBase
from paquo.classes import QuPathPathClass
from paquo.images import QuPathProjectImageEntry
from paquo.java import ImageServerProvider, BufferedImage, DefaultProjectImageEntry, \
    ProjectIO, File, Projects, String, ServerTools, DefaultProject


class _ProjectImageEntriesProxy(collections_abc.Collection):
    """iterable container holding image entries"""
    # todo: decide if this should be a mapping or not...
    #   maybe with key id? to simplify re-association

    def __init__(self, project: DefaultProject):
        if not isinstance(project, DefaultProject):
            raise TypeError('requires DefaultProject instance')
        self._project = project

    def __len__(self) -> int:
        return int(self._project.size())

    def __iter__(self) -> Iterator[QuPathProjectImageEntry]:
        return iter(map(QuPathProjectImageEntry, self._project.getImageList()))

    def __contains__(self, __x: object) -> bool:
        if not isinstance(__x, DefaultProjectImageEntry):
            return False
        # this would need to compare via unique image ids as in
        # Project.getEntry
        raise NotImplementedError("todo")

    def __repr__(self):
        return f"<ImageEntries({repr([entry.image_name for entry in self])})>"


class QuPathProject(QuPathBase):

    def __init__(self, path: Union[str, pathlib.Path]):
        """load or create a new qupath project"""
        path = pathlib.Path(path)
        if path.is_file():
            project = ProjectIO.loadProject(File(str(path)), BufferedImage)
        else:
            project = Projects.createProject(File(str(path)), BufferedImage)

        super().__init__(project)
        self._image_entries_proxy = _ProjectImageEntriesProxy(project)

    @property
    def images(self) -> Collection[QuPathProjectImageEntry]:
        """project images"""
        return self._image_entries_proxy

    def add_image(self, filename: str) -> QuPathProjectImageEntry:
        """add an image to the project

        todo: expose copying/moving/re-association etc...

        Parameters
        ----------
        filename:
            filename pointing to the image file

        """
        # first get a server builder
        img_path = pathlib.Path(filename).absolute()
        support = ImageServerProvider.getPreferredUriImageSupport(
            BufferedImage,
            String(str(img_path))
        )
        if not support:
            raise Exception("unsupported file")
        server_builders = list(support.getBuilders())
        if not server_builders:
            raise Exception("unsupported file")
        server_builder = server_builders[0]
        entry = self.java_object.addImage(server_builder)

        # all of this happens in qupath.lib.gui.commands.ProjectImportImagesCommand
        server = server_builder.build()
        entry.setImageName(ServerTools.getDisplayableImageName(server))
        # basically getThumbnailRGB(server, None) without the resize...
        thumbnail = server.getDefaultThumbnail(server.nZSlices() // 2, 0)
        entry.setThumbnail(thumbnail)

        return QuPathProjectImageEntry(entry)

    @property
    def uri(self) -> str:
        """the uri identifying the project location"""
        return str(self.java_object.getURI().toString())

    @property
    def uri_previous(self) -> Optional[str]:
        """previous uri. potentially useful for re-associating"""
        uri = self.java_object.getPreviousURI()
        if uri is None:
            return None
        return str(uri.toString())

    @property
    def path_classes(self) -> Tuple[QuPathPathClass]:
        """return path_classes stored in the project"""
        return tuple(map(QuPathPathClass, self.java_object.getPathClasses()))

    @path_classes.setter
    def path_classes(self, path_classes: Iterable[QuPathPathClass]):
        """to add path_classes reassign all path_classes here"""
        pcs = [pc.java_object for pc in path_classes]
        self.java_object.setPathClasses(pcs)

    @property
    def path(self) -> pathlib.Path:
        """the path to the project root"""
        return pathlib.Path(str(self.java_object.getPath()))

    def save(self) -> None:
        """flush changes in the project to disk

        (writes path_classes and project data)
        """
        self.java_object.syncChanges()

    @property
    def name(self) -> str:
        """project name"""
        return self.java_object.getName()

    def __repr__(self) -> str:
        name = self.java_object.getNameFromURI(self.java_object.getURI())
        return f'<QuPathProject "{name}">'

    @property
    def timestamp_creation(self) -> int:
        """system time at creation in milliseconds"""
        return int(self.java_object.getCreationTimestamp())

    @property
    def timestamp_modification(self) -> int:
        """system time at modification in milliseconds"""
        return int(self.java_object.getModificationTimestamp())

    @property
    def version(self) -> str:
        """the project version. should be identical to the qupath version"""
        # note: only available when building project while the gui
        #   is active? ...
        return str(self.java_object.getVersion())

    @classmethod
    def from_settings(
            cls,
            project_path: pathlib.Path,
            image_paths: List[pathlib.Path],
            path_classes: Optional[List[Dict]] = None,
            image_metadata: Optional[Dict] = None,
            *,
            save: bool = True
    ):
        """create a project from settings"""
        if project_path.exists():
            raise ValueError("project_path exists already")
        project_path.mkdir(parents=True)

        # create empty project
        proj = QuPathProject(project_path)

        # set required path classes
        if path_classes:
            proj.path_classes = [
                QuPathPathClass.create(**class_dict) for class_dict in path_classes
            ]

        # append images from paths
        for image in image_paths:
            entry = proj.add_image(image)
            if image_metadata:
                entry.metadata.update(image_metadata)

        if save:
            # store the project
            proj.save()

        return proj
