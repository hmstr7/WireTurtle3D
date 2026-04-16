from wireturtle3d import Scene, Object, Renderer, Camera, v, Cube
from wireturtle3d import AnimContext

# Create a scene with objects
my_scene: Scene = Scene({
    # Each scene must contain at least one camera
    "camera":Camera(
        width=1200,height=900, # Define screen dimensions 
        location=[0.,0.,0.],
        rotation=[0.,0.,0.]
    ),
    "cube":Object(
        location=[0.,0.,-5.],
        rotation=[0.,0.,0.], 
        scale=[1.,1.,1.],
        mesh=Cube(1.)
    )
})

renderer: Renderer = Renderer(my_scene) # Pass the scene to a renderer.

# Create an animation using renderer
@renderer.animation
def my_animation(context: AnimContext) -> None: # During runtime, an AnimContext object will be passed to the function serving as a shortcut access to the scene objects and useful variables.
    context["cube"].add(rotation=v[0,100,0] * context.dt) # Rotate cube around Y axis (yaw). dt ensures that the animation runs independently of FPS. Note: import v and add it before lists like shown in order to be able to perform operations such as multiplying.

renderer.start() # Run the program.