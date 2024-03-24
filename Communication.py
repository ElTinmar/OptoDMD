from dataclasses import dataclass
from numpy.typing import NDArray
import numpy as np

@dataclass
class ImageStore:
    camera_image: NDArray = np.zeros((512,512))
    two_photon_image: NDArray = np.zeros((512,512))
    dmd_image = NDArray = np.zeros((512,512))
    camera_mask: NDArray = np.zeros((512,512))
    two_photon_mask: NDArray = np.zeros((512,512))
    dmd_mask = NDArray = np.zeros((512,512))    