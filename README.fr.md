[English](./README.md) | **Français**
# WireTurtle3D
Graphismes 3D en fil de fer réalisés uniquement avec `turtle` et `numpy`.

## Utilisation
Voir l'[exemple](./examples/showcase.py) et les docstrings.

Exemple d'une configuration minimale pour une animation simple :
```python
### examples/minimal_fr.py

from wireturtle3d import Scene, Object, Renderer, Camera, v, Cube

# Crée une scène avec des objets
my_scene = Scene({
    # Chaque scène doit contenir au moins une caméra
    "camera":Camera(
        width=1200,height=900, # Définir les dimensions de l'écran 
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

renderer = Renderer(my_scene) # Passe la scène à un moteur de rendu.

# Crée une animation en utilisant le moteur_rendu
@renderer.animation
def my_animation(context): # Pendant l'exécution, un objet de classe AnimContext sera passé à la fonction, servant de raccourci pour accéder aux objets de la scène et à des variables utiles.
    context["cube"].add(rotation=v[0,100,0]*context.dt) # Fait tourner le cube autour de l'axe Y (lacet). dt garantit que l'animation s'exécute indépendamment des FPS. Remarque : importez v et utilisez-le avant les listes comme montré pour pouvoir effectuer des opérations telles que la multiplication ou l'addition.

renderer.start() # Lance le programme.
```

## Installation

### Avec UV (recommandé)
```bash
uv pip install git+https://github.com/hmstr7/WireTurtle3D.git
```
> Remarque : il est préférable d'installer les paquets dans un environnement virtuel ; vous pouvez en créer un avec `uv venv`

### Avec pip
```bash
pip install git+https://github.com/hmstr7/WireTurtle3D.git
```