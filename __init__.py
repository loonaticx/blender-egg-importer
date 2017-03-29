bl_info = {
    "name": "Import Panda3D .egg models",
    "author": "rdb",
    "version": (0, 1),
    "blender": (2, 74, 0), # Needed for normals_split_custom_set
    "location": "File > Import > Panda3D (.egg)",
    "description": "",
    "warning": "",
    "category": "Import-Export",
}

if "bpy" in locals():
    import imp
    imp.reload(eggparser)
    imp.reload(importer)
else:
    from . import eggparser
    from . import importer

import io, zlib
import os.path
import zlib
import bpy, bpy.types
from bpy import props
from bpy_extras.io_utils import ImportHelper


class IMPORT_OT_egg(bpy.types.Operator, ImportHelper):
    """Import .egg Operator"""
    bl_idname = "import_scene.egg"
    bl_label = "Import .egg"
    bl_description = "Import a Panda3D .egg file"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".egg"
    filter_glob = props.StringProperty(default="*.egg;*.egg.pz;*.egg.gz", options={'HIDDEN'})

    directory = props.StringProperty(name="Directory", options={'HIDDEN'})
    files = bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN'})

    def execute(self, context):
        context = importer.EggContext()
        context.info = lambda msg: self.report({'INFO'}, msg)
        context.warn = lambda msg: self.report({'WARNING'}, msg)
        context.error = lambda msg: self.report({'ERROR'}, msg)
        context.search_dir = self.directory
        roots = []

        for file in self.files:
            path = os.path.join(self.directory, file.name)

            if path.endswith('.pz') or path.endswith('.gz'):
                data = zlib.decompress(open(path, 'rb').read(), 32 + 15).decode('utf-8')
            else:
                data = open(path, 'r').read()

            fp = io.StringIO(data)
            root = importer.EggGroupNode()
            eggparser.parse_egg(fp, root, context)
            fp.close()
            roots.append(root)

        for root in roots:
            root.build_tree(context)
        context.assign_vertex_groups()
        context.final_report()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator(IMPORT_OT_egg.bl_idname, text="Panda3D (.egg)")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()