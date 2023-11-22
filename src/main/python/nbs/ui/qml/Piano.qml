
import QtQuick 2.15

Rectangle {
    width: parent.width
    height: 200
    color: "#f0f0f0"

    anchors {
        horizontalCenter: parent.horizontalCenter
        bottom: parent.bottom
    }

    property int octaveCount: 3
    property int whiteKeyCount: 21 //octaveCount * 7
    property int blackKeyCount: (octaveCount - 1) * 5 + 2

    property int keyWidth: width / whiteKeyCount
    property int keyHeight: height

    property var blackKeyIndices: [1, 2, 4, 5, 6]

    property var whiteKeyLabels: ["C", "D", "E", "F", "G", "A", "B"]

    Row {
        anchors.fill: parent
        anchors.margins: 10
        // add a 1px gap between the white and black keys
        spacing: 2

        Repeater {
            model: whiteKeyCount

            WhitePianoKey {
                id: whiteKey
                key: index
                label: whiteKeyLabels[index % whiteKeyLabels.length] + (Math.floor(index / whiteKeyLabels.length) + 1)
                x: index * whiteKey.width
            }
        }
    }

    //Rectangle {
    //    id: blackKeys
    //    width: whiteKeys.width - keyWidth / 2
    //    height: whiteKeys.height / 2
    //    anchors.top: whiteKeys.top
    //    anchors.right: whiteKeys.right
    //
    //    Repeater {
    //        model: blackKeyCount
    //        Rectangle {
    //            id: blackKey
    //            x: blackKeyIndices[index] * keyWidth  // Use the indices to calculate the x position
    //            width: keyWidth / 2
    //            height: keyHeight / 2
    //            color: "black"
    //            border.width: 1
    //            border.color: "black"
    //            MouseArea {
    //                anchors.fill: parent
    //                onClicked: {
    //                    console.log("Black key clicked:", index)
    //                }
    //            }
    //        }
    //    }
    //}
}
