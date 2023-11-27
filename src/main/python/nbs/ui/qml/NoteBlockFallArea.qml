import QtQuick 2.0
import QtQuick.Controls 2.15

ScrollView {
    id: fallArea
    anchors.fill: parent
    //anchors.bottomMargin: 100
    //contentWidth: label.width //availableWidth
    //contentHeight: label.height
    contentHeight: 10000
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOn
    ScrollBar.vertical.policy: ScrollBar.AlwaysOn
    clip: true

    //Label {
    //    id: label
    //    //implicitWidth: width
    //    //implicitHeight: height
    //    text: qsTr("Hello World")
    //    anchors.centerIn: parent
    //    font.pixelSize: 500
    //}

    ListView {
        id: listView
        width: parent.width
        height: parent.height
        model: noteManager.notes

        delegate: Loader {
            sourceComponent: NoteBlock {
                color: "red"
                x: modelData.key * 8
                y: fallArea.contentHeight - modelData.tick * 8
                //label: noteManager.notes[index].instrument
            }
        }
}
