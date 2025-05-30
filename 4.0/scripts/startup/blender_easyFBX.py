#  BSD License
#  -----------
#  
#  Copyright (c) 2022 Thomas Iché (peeweek.net) All rights reserved.
# 
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice, this
#    list of conditions and the following disclaimer in the documentation and/or
#    other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#  ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

bl_info = {
    "name": "Easy FBX Exporter",
    "category": "3D View",
    "blender": (2, 80, 0),
    "author": "Thomas Iché",
    "description": "Simplest FBX Mesh Export Tool",
    "version": (0, 2, 0),    
    }

import bpy
import os
import bmesh
from bpy.props import EnumProperty, BoolProperty, StringProperty, FloatProperty, IntProperty


def select(object):
    object.select_set(state=True)
    for obj in object.children:
        obj.hide_set(False)
        select(obj)

def exportObject(object):
    filename = f"{object.name}.fbx"
    
    folder = bpy.path.abspath(bpy.context.scene.exportFolder)
    
    path = os.path.join(folder,filename)
    print(path)
    
    exportTextures = bpy.context.scene.exportTextures
    print(exportTextures)
    bpy.ops.object.select_all(action='DESELECT')    
    select(object)
    
    print(f"Exporting Object {object.name} as file {path}")
    
    # TODO : Add more options to control export
    bpy.ops.export_scene.fbx(
    filepath=path,
     check_existing=True,
      filter_glob='*.fbx',
       use_selection=True,
        use_active_collection=False,
         global_scale=1.0,
          apply_unit_scale=False,
           apply_scale_options='FBX_SCALE_NONE',
            use_space_transform=True,
             bake_space_transform=True,
             object_types={'CAMERA', 'EMPTY', 'LIGHT', 'MESH'}, 
             use_mesh_modifiers=True, 
             use_mesh_modifiers_render=True, 
             mesh_smooth_type='OFF', 
             use_subsurf=True, 
             use_mesh_edges=False, 
             use_tspace=False, 
             use_custom_props=False, 
             add_leaf_bones=True, 
             primary_bone_axis='Y', 
             secondary_bone_axis='X', 
             use_armature_deform_only=False, 
             armature_nodetype='NULL', bake_anim=True, 
             bake_anim_use_all_bones=True, 
             bake_anim_use_nla_strips=True, 
             bake_anim_use_all_actions=True, 
             bake_anim_force_startend_keying=True, 
             bake_anim_step=1.0, 
             bake_anim_simplify_factor=1.0, 
             path_mode='COPY', 
             embed_textures=exportTextures, 
             batch_mode='OFF', 
             use_batch_own_dir=True, 
             use_metadata=True, 
             axis_forward='-Z', 
             axis_up='Y')      

class EasyFBXExportUIPanel(bpy.types.Panel):
    """EasyFBXExportUIPanel"""
    bl_label = "Easy FBX Exporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "FBX"


    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='FILE_3D')

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column(align=True)
        col.label(text='Export Folder :')
        col.prop(context.scene, 'exportFolder', text="")
        
        box = layout.box()
        col = box.column(align=True)
        col.label(text='Export From Collection:')
        col.prop(context.scene, 'exportCollection', text="")
        
        box = layout.box()
        col = box.column(align=True)
        
        col.label(text='Filter Options:')        
        col.prop(context.scene, 'exportSelected', text="Selected")
        
        row = col.row(align=True)
        row.prop(context.scene, 'exportInclude', text="Include")
        row.prop(context.scene, 'exportIncludeStr', text="")
        
        row = col.row(align=True)
        row.prop(context.scene, 'exportExclude', text="Exclude")
        row.prop(context.scene, 'exportExcludeStr', text="")
        
        box = layout.box()
        col = box.column(align=True)
        col.prop(context.scene, 'exportTextures', text="Export Textures") 
        
        box = layout.box()
        col = box.column(align=True)
        col.prop(context.scene, 'exportOverwrite', text="Overwrite files")  
        col.operator("ezfbx.export", text="Export", icon="RENDER_RESULT")

class EasyFBXExport(bpy.types.Operator):
    """Export based on options"""
    bl_idname = "ezfbx.export"
    bl_label = "set normal"
    bl_options = {"UNDO"}


    def execute(self, context):
        
        # Preliminary Checks
        
        # If  we export to the same folder as the blend file, make sure we're already saved
        if context.scene.exportFolder.startswith("//") :
            if not bpy.data.is_saved :
                self.report({'WARNING'}, "Save your blend file first in order to export in the same folder")
                return {'FINISHED'}
        else:
            # Check if folder exists
            hasfolder = os.access(context.scene.exportFolder, os.W_OK)
             
            if hasfolder is False:            
                self.report({'WARNING'}, "Select a valid export folder")
                return {'FINISHED'}
            
        if context.scene.exportCollection is None:
            self.report({'WARNING'}, "Select a valid collection")
            return {'FINISHED'}
        
        # backup selection
        selection = bpy.context.selected_objects
        
        collection = bpy.context.scene.exportCollection.all_objects
        only_selected = bpy.context.scene.exportSelected
        filter_include = bpy.context.scene.exportInclude
        filter_include_str = bpy.context.scene.exportIncludeStr
        filter_exclude = bpy.context.scene.exportExclude
        filter_exclude_str = bpy.context.scene.exportExcludeStr
        
        
        print("export collection")        
        for object in collection:
            
            # Only Top level Objects (each as FBX)
            if object.parent is None:
                
                # Filter Selected
                if only_selected and not (object in selection):
                    print(f"Excluding {name} : not in selection")
                    continue
                
                name = object.name
                
                # Filter Include String
                if filter_include and not (filter_include_str in name):
                    print(f"Excluding {name} : does not include '{filter_include_str}'")
                    continue
                
                # Filter Out Exclude String
                if filter_exclude and (filter_exclude_str in name):
                    print(f"Excluding {name} : excluded because contains '{filter_include_str}'")
                    continue
                
                exportObject(object)
        
        
        # restore selection
        print("restore selection")
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select_set(state=True)
            
        return {'FINISHED'}        

      

# All classes defined here should be registered

classes = (
    EasyFBXExportUIPanel,
    EasyFBXExport,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.exportFolder = bpy.props.StringProperty (name = "exportFolder",default = "//", description = "destination folder",subtype = 'DIR_PATH')
    bpy.types.Scene.exportCollection = bpy.props.PointerProperty (name = "exportCollection",  type=bpy.types.Collection, description = "Export Collection")
    bpy.types.Scene.exportSelected = bpy.props.BoolProperty (name = "exportSelected", default = False, description = "exportSelected")
    bpy.types.Scene.exportOverwrite = bpy.props.BoolProperty (name = "exportOverwrite", default = True, description = "exportOverwrite")
    bpy.types.Scene.exportTextures = bpy.props.BoolProperty (name = "exportTextures", default = True, description = "exportTextures")
    
    bpy.types.Scene.exportInclude = bpy.props.BoolProperty (name = "exportInclude", default = False, description = "exportInclude")
    bpy.types.Scene.exportIncludeStr = bpy.props.StringProperty (name = "exportIncludeStr", default = "ST_", description = "exportIncludeStr")
    
    bpy.types.Scene.exportExclude = bpy.props.BoolProperty (name = "exportExclude", default = False, description = "exportExclude")
    bpy.types.Scene.exportExcludeStr = bpy.props.StringProperty (name = "exportExcludeStr", default = ".Hi", description = "exportExcludeStr")    
        
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    
if __name__ == "__main__":
    register()