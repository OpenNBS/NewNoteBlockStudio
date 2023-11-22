
import QtQuick 2.15

Rectangle {
    property int key: 0
    property string label: "C4"

    width: 38
    height: 120
    color: "white"
    border.width: 1
    border.color: "black"
    radius: 3

    Rectangle {
        width: parent.width
        height: 10
        //color: darker(parent.color, 1.2)
        anchors.bottom: parent.bottom
        border.width: 1
        border.color: "black"
        radius: 2
    }

    Text {
        anchors {
            horizontalCenter: parent.horizontalCenter
            bottom: parent.bottom
            bottomMargin: 25
        }

        text: parent.label
        font.pixelSize: 12
    }

    MouseArea {
        anchors.fill: parent
        onPressed: {
            whiteKey.y = whiteKey.y + 5
            console.log("White key clicked:", index)
        }
        onReleased: {
            whiteKey.y = whiteKey.y - 5
            console.log("White key released:", index)
        }
    }

    Connections {
        target: whiteKey
        function onYChanged() {
            if (whiteKey.y > 0) {
                whiteKey.y = 0
            }
        }
    }
}
