import bpy

class VIEW3D_PT_hop_result(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "checker"
    bl_label = "ObjectChecker"

    def draw(self,context):
        self.layout.operator("object.integrity_checker")
        for line in context.scene.objects_checker.split("\n"):
            self.layout.label(text = line)
        self.layout.operator("object.data_checker")
        for line in context.scene.unused_data_checker.split("\n"):
                    self.layout.label(text = line)


def format_list(names):
    if len(names) == 0 :
        return "none"
    return " , ".join(names)

def is_scale_uniform(scale):
    return max(scale) - min(scale) < 0.0001
def is_scale_applied(scale):
    return max(abs(scale.x -1) , abs(scale.y - 1) , abs(scale.z-1)) < 0.0001
def is_rotate_applied(rotation):
    return max(abs(rotation.x - 0) , abs(rotation.y - 0) , abs(rotation.z - 0)) < 0.0001
def is_ascii_name(name):
    return name.isascii()

def is_ngon_included(mesh):
        return any(len(p.vertices) >= 5 for p in mesh.polygons)
        
class OBJECT_OT_integrity_checker(bpy.types.Operator):
    bl_idname = "object.integrity_checker"
    bl_label = "IntegrityChecker"
    bl_description = "Inspect the selected object"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls,context):
        return len(context.selected_objects)  > 0

    def execute(self,context):
        scale_not_uniform = []
        scale_not_applied = []
        rotation_not_applied = []
        non_ascii_name = []
        included_ngon = []

        for o in context.selected_objects:
            if not is_scale_uniform(o.scale):
                scale_not_uniform.append(o.name)
            if not is_scale_applied(o.scale):
                scale_not_applied.append(o.name)
            if not is_rotate_applied(o.rotation_euler):
                rotation_not_applied.append(o.name)
            if not is_ascii_name(o.name):
                non_ascii_name.append(o.name)
            if o.type == "MESH" and is_ngon_included(o.data):
                included_ngon.append(o.name)



        items = [
            ("scale not uniform" , scale_not_uniform),
            ("scale not applied" , scale_not_applied),
            ("rotation not applied" , rotation_not_applied),
            ("non ascii name" , non_ascii_name),
            ("included Ngon" , included_ngon),
            ]

        lines = []
        total = 0
        for label , names in items:
            lines.append(label + " : " + format_list(names))
            total += len(names)
        result_text = "\n".join(lines)

        context.scene.objects_checker = result_text

        if total == 0 :
            self.report({"INFO"}, "No issues found")
            return {"FINISHED"}
        
        self.report({"WARNING"},str(total) + " issue(s) found")
        return {"FINISHED"}

class OBJECT_OT_unused_data_checker(bpy.types.Operator):
    bl_idname = "object.data_checker"
    bl_label =  "Unused data checker"
    bl_description = "I'll check if there is any unused data"
    bl_options = {"REGISTER"}

    def execute(self,context):
        data_types = [
                ("mesh" , bpy.data.meshes),
                ("material" , bpy.data.materials),
                ("image" , bpy.data.images)
            ]
        items = []
    
        for label, collection in data_types :
            names = [d.name for d in collection if d.users == 0 ]
            items.append((label,names))

        lines = []
        total = 0
        for label , names in items:
            lines.append(label + " : " + format_list(names))
            total += len(names)
        result_text = "\n".join(lines)
        
        context.scene.unused_data_checker = result_text

        if total == 0 :
            self.report({"INFO"}, "No issues found")
            return {"FINISHED"}
                
        self.report({"WARNING"},str(total) + " issue(s) found")
        return {"FINISHED"}
        


def register():
    bpy.utils.register_class(OBJECT_OT_integrity_checker)
    bpy.utils.register_class(OBJECT_OT_unused_data_checker)
    bpy.utils.register_class(VIEW3D_PT_hop_result)
    bpy.types.Scene.objects_checker = bpy.props.StringProperty(
        name = "Check Result",
        default = "Not checked yet",
    )
    bpy.types.Scene.unused_data_checker = bpy.props.StringProperty(
        name = "Unused Data Check Result",
        default = "Not Checked yet",
    )

def unregister():
    del bpy.types.Scene.unused_data_checker
    del bpy.types.Scene.objects_checker
    bpy.utils.unregister_class(VIEW3D_PT_hop_result)
    bpy.utils.unregister_class(OBJECT_OT_unused_data_checker)
    bpy.utils.unregister_class(OBJECT_OT_integrity_checker)

register()
