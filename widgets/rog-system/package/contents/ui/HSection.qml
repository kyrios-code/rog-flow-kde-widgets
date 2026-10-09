import QtQuick
import org.kde.kirigami as Kirigami
Rectangle {
 id:section;radius:16;color:Qt.rgba(0.025,0.055,0.11,fillOpacity);border.width:1;border.color:edge
 property color accent: '#50cfff'
 property color edge: '#6650a6d1'
 property real fillOpacity: 0
 property string title:''
 property int themeIndex: 0
 Image {x:section.width-32;y:10;width:17;height:17;fillMode:Image.PreserveAspectFit;source:"../images/"+(section.title==="NETWORK ACTIVITY"?"network":section.title==="GRAPHICS MEMORY"?"graphics":section.title==="SYSTEM & STORAGE"?"storage":section.title==="TOP PROCESSES"?"processes":"profile")+"-"+section.themeIndex+".svg"}
 Text{x:17;y:10;text:section.title;font.family:'Bulky Pixels';font.pixelSize:15;color:section.accent}
}
