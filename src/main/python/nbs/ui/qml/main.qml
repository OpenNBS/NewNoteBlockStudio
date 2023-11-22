import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 1280
    height: 720
    title: "Clock"

    property string currTime: "00:00:00"

    Rectangle {
        anchors.fill: parent

        Rectangle {
            anchors.fill: parent
            color: "red"

            Text {
                anchors {
                    bottom: parent.bottom
                    bottomMargin: 12
                    left: parent.left
                    leftMargin: 12
                }
                text: currTime
                font.pixelSize: 36
                color: "white"
            }

        }

    }

    Piano {
        anchors {
            top: parent.top
            topMargin: 12
            horizontalCenter: parent.horizontalCenter
        }
    }

    NoteBlock {
        anchors {
            bottom: parent.bottom
            bottomMargin: 12
            left: parent.left
            leftMargin: 12
        }
    }

}