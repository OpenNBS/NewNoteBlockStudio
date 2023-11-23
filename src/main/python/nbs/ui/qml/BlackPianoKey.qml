
import QtQuick 2.15 

Rectangle {
    property int key
    property string label

    width: 25
    height: 70
    color: "#333333"
    border.width: 1
    border.color: Qt.darker(color, 2.0)
    radius: 3

    Rectangle {
        width: parent.width
        height: 10
        color: Qt.darker(parent.color, 1.15)
        anchors.bottom: parent.bottom
        border.width: 1
        border.color: Qt.darker(color, 2.0)
        radius: 2
    }

    Text {
        anchors {
            horizontalCenter: parent.horizontalCenter
            bottom: parent.bottom
            bottomMargin: 25
        }

        text: parent.label
        color: "white"
        font.pixelSize: 12
    }

    MouseArea {
        anchors.fill: parent
        onPressed: {
            blackKey.y = blackKey.y + 5
            console.log("Black key clicked:", index)
        }
        onReleased: {
            blackKey.y = blackKey.y - 5
            console.log("Black key released:", index)
        }
    }
}
