
import QtQuick 2.15

Rectangle {
    width: parent.width
    height: 140
    color: "transparent"

    anchors {
        horizontalCenter: parent.horizontalCenter
        bottom: parent.bottom
    }

    property int octaveCount: 3
    property int whiteKeyCount: octaveCount * 7 + 3
    property int blackKeyCount: octaveCount * 5 + 2

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

    Repeater {
        model: blackKeyCount

        BlackPianoKey {
            id: blackKey
            key: index
            label: whiteKeyLabels[blackKeyIndices[index % 5] - 1] + "#" + (Math.floor(index / whiteKeyLabels.length) + 1)
            x: Math.floor(index / 5) * (40 * 7) + (blackKeyIndices[index % 5] * 40 - 4) // TODO: hardcoded
        }
    }
}
