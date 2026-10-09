import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
 id: page
 property int cfg_themeIndex: 0
 property alias cfg_backgroundOpacity: opacity.value
 readonly property var themeNames: ["Cyan Glass", "Purple Nebula", "Emerald Circuit", "Amber ROG"]
 readonly property var accents: ["#50cfff", "#b38cff", "#48e5bc", "#ffbb66"]
 readonly property var iconColors: ["#ffbd69", "#5ce4cf", "#c7a0ff", "#73baff"]
 readonly property var colorLabels: ["Warm amber icons", "Mint teal icons", "Soft violet icons", "Electric blue icons"]
 Kirigami.Separator { Kirigami.FormData.isSection: true; Kirigami.FormData.label: "Color theme" }
 QQC2.Label { text: "Choose a coordinated glass and icon palette."; color: Kirigami.Theme.disabledTextColor }
 ColumnLayout {
  spacing: 8
  Layout.preferredWidth: 480
  Repeater {
   model: 4
   delegate: Rectangle {
    required property int index
    Layout.fillWidth: true
    Layout.preferredHeight: 74
    radius: 11
    color: index===page.cfg_themeIndex ? Qt.rgba(.13,.18,.23,.75) : Qt.rgba(.08,.12,.17,.45)
    border.width: index===page.cfg_themeIndex ? 2 : 1
    border.color: index===page.cfg_themeIndex ? page.accents[index] : "#496071"
    Rectangle {
     x:12; y:10; width:65; height:54; radius:9
     color:"#102032"; border.width:1; border.color:page.accents[index]
     Image { anchors.centerIn:parent; width:31; height:31; fillMode:Image.PreserveAspectFit
      source:"../images/fan-"+index+".svg" }
    }
    Column {
     x:91; y:15; spacing:5
     Text { text:page.themeNames[index]; color:Kirigami.Theme.textColor; font.pixelSize:15; font.bold:true }
     Text { text:page.colorLabels[index]; color:Kirigami.Theme.disabledTextColor; font.pixelSize:12 }
    }
    Row {
     anchors.right:parent.right; anchors.rightMargin:16; anchors.verticalCenter:parent.verticalCenter; spacing:6
     Rectangle {width:17;height:17;radius:9;color:page.accents[index]}
     Rectangle {width:17;height:17;radius:9;color:page.iconColors[index]}
    }
    MouseArea { anchors.fill:parent; onClicked:page.cfg_themeIndex=index }
   }
  }
 }
 Kirigami.Separator { Kirigami.FormData.isSection: true; Kirigami.FormData.label: "Glass transparency" }
 RowLayout {
  Kirigami.FormData.label: "Background opacity:"
  Layout.preferredWidth: 440
  QQC2.Slider {id:opacity;Layout.fillWidth:true;from:0;to:90;stepSize:5;snapMode:QQC2.Slider.SnapAlways}
  QQC2.Label {text:Math.round(opacity.value)+"%";Layout.minimumWidth:42;horizontalAlignment:Text.AlignRight}
 }
 QQC2.Label { text:"0% is fully transparent. Opacity applies independently to this widget.";wrapMode:Text.WordWrap;color:Kirigami.Theme.disabledTextColor }
}
