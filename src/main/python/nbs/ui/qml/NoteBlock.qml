import QtQuick 2.0
import QtGraphicalEffects 1.0
import QtQuick.Controls 1.4


Rectangle {

    property int key: 0
    property string label: "C4"
    property int instrument: 0
    property color overlayColor: "green"

    id: "rect"
    width: 32
    height: 32
    visible: true
    color: "red"

    Image {
        id: image
        anchors.fill: parent
        source: "../../../../resources/base/images/note_block_grayscale.png"
        fillMode: Image.PreserveAspectFit
        // set scaling to nearest neighbor
        smooth: false
        cache: true
    }

    ColorOverlay {
        anchors.fill: image
        source: image
        color: overlayColor
        opacity: 0.25
        cached: true
    }

    Text {
        anchors {
            top: parent.top
            topMargin: 2
            horizontalCenter: parent.horizontalCenter
        }
        id: keyLabel
        text: label
        font.pixelSize: 12
        color: "white"
    }

    Text {
        anchors {
            bottom: parent.bottom
            bottomMargin: 2
            horizontalCenter: parent.horizontalCenter
        }
        id: clicksLabel
        text: instrument
        font.pixelSize: 12
        color: "white"
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            console.log("clicked")
        }
    }
}
