
import QtQuick 2.15

Rectangle {
    property int key
    property string label

    width: 38
    height: 120
    color: "white"
    border.width: 1
    border.color: Qt.darker(color, 1.75)
    radius: 3

    Rectangle {
        width: parent.width
        height: 10
        color: Qt.darker(parent.color, 1.05)
        anchors.bottom: parent.bottom
        border.width: 1
        border.color: Qt.darker(color, 1.5)
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
}
