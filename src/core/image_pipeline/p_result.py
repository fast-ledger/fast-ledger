import numpy as np


# fmt: off
class P_Result():
    
    def __init__(self, **kwds):
        self.image = kwds.get('image')
        self.id = kwds.get('id')
        self.label_name = kwds.get('label_name')

    def __call__(self, images: list[np.ndarray], ids: list[str], label_names: list[str]):
        return [P_Result(image=image, id=ids[i], label_name=label_names[i]) for i, image in enumerate(images)]
    
    def __repr__(self):
        image = self.image
        id = self.id
        label_name = self.label_name
        space = 15
        return f"""{'image:': <{space}} {image}, {type(image)}

{'id:': <{space}}{id: <{space}}, {type(id)}
{'label_name:': <{space}}{label_name: <{space}}, {type(label_name)}
"""
        
        
# fmt: on
