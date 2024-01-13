from typing import List

import pytest

from nbs.controller.layer import LayerController
from nbs.core.data import Layer


@pytest.fixture
def layerController() -> LayerController:
    layers = [
        Layer(
            name="Layer 1",
            lock=False,
            solo=False,
            volume=100,
            panning=0,
        ),
        Layer(
            name="Layer 2",
            lock=True,
            solo=True,
            volume=50,
            panning=100,
        ),
    ]
    return LayerController(layers)


def testAddLayer() -> None:
    layers: List[Layer] = []
    layerController = LayerController(layers)
    layerController.addLayer()
    assert len(layers) == 1
    assert layers[0].name == ""
    assert layers[0].lock == False
    assert layers[0].solo == False
    assert layers[0].volume == 100
    assert layers[0].panning == 0


def testInsertLayer(layerController: LayerController) -> None:
    layerController.addLayer(1)
    layers = layerController.layers
    assert len(layers) == 3
    assert layers[0].name == "Layer 1"
    assert layers[1].name == ""
    assert layers[2].name == "Layer 2"


def testRemoveLayer(layerController: LayerController) -> None:
    layerController.removeLayer(0)
    layers = layerController.layers
    assert len(layers) == 1
    assert layers[0].name == "Layer 2"
    layerController.removeLayer(0)
    assert len(layers) == 0


def testRemoveNonExistingLayer(layerController: LayerController) -> None:
    with pytest.raises(IndexError):
        layerController.removeLayer(2)


def testSetLayerName(layerController: LayerController) -> None:
    layerController.setLayerName(0, "Layer 2")
    assert layerController.layers[0].name == "Layer 2"


def testSetLayerNameToEmptyString(layerController: LayerController) -> None:
    layerController.setLayerName(0, "")
    assert layerController.layers[0].name == ""


def testSetLayerLock(layerController: LayerController) -> None:
    layerController.setLayerLock(0, True)
    assert layerController.layers[0].lock == True


def testSetLayerSolo(layerController: LayerController) -> None:
    layerController.setLayerSolo(0, True)
    assert layerController.layers[0].solo == True


def testSetLayerVolume(layerController: LayerController) -> None:
    layerController.setLayerVolume(0, 50)
    assert layerController.layers[0].volume == 50


def testSwapLayer(layerController: LayerController) -> None:
    layerController.swapLayers(0, 1)
    assert layerController.layers[0].name == "Layer 2"
    assert layerController.layers[1].name == "Layer 1"


def testSwapLayerToSamePosition(layerController: LayerController) -> None:
    layerController.swapLayers(0, 0)
    assert layerController.layers[0].name == "Layer 1"
    assert layerController.layers[1].name == "Layer 2"
