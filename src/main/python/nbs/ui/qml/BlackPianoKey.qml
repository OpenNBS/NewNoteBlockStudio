
import QtQuick 2.15

Rectangle {
    width: 400
    height: 200
    color: "#f0f0f0"

    property int octaveCount: 2
    property int whiteKeyCount: octaveCount * 7
    property int blackKeyCount: (octaveCount - 1) * 5 + 2

    property int keyWidth: width / whiteKeyCount
    property int keyHeight: height

    property var blackKeyIndices: [1, 2, 4, 5, 6]

    Rectangle {
        id: whiteKeys
        width: parent.width
        height: parent.height

        Repeater {
            model: whiteKeyCount
            Rectangle {
                id: whiteKey
                x: index * parent.width / whiteKeyCount
                width: parent.width / whiteKeyCount
                height: parent.height
                color: "white"
                border.width: 1
                border.color: "black"
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        console.log("White key clicked:", index)
                    }
                }
            }
        }
    }

    Rectangle {
        id: blackKeys
        width: whiteKeys.width - keyWidth / 2
        height: whiteKeys.height / 2
        anchors.top: whiteKeys.top
        anchors.right: whiteKeys.right

        Repeater {
            model: blackKeyCount
            Rectangle {
                id: blackKey
                x: blackKeyIndices[index] * keyWidth  // Use the indices to calculate the x position
                width: keyWidth / 2
                height: keyHeight / 2
                color: "black"
                border.width: 1
                border.color: "black"
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        console.log("Black key clicked:", index)
                    }
                }
            }
        }
    }
}
