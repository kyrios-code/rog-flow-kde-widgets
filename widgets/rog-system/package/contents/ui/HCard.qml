import QtQuick
import org.kde.kirigami as Kirigami
Rectangle {
 id: card;width:216;height:157;radius:17;color:Qt.rgba(0.025,0.055,0.11,fillOpacity);border.width:1;border.color:edge
 property color accent: '#50cfff'
 property color edge: '#6650a6d1'
 property real fillOpacity: 0
 property string title:'';property string value:'—';property string unit:'';property string detail:'';property real fraction:0
 property int themeIndex: 0
 Image {x:card.width-32;y:13;width:17;height:17;fillMode:Image.PreserveAspectFit;source:"../images/"+(card.title==="CPU"?"cpu":card.title==="GPU"?"gpu":card.title==="MEMORY"?"memory":"battery")+"-"+card.themeIndex+".svg"}
 Text{x:17;y:13;text:card.title;font.family:'Bulky Pixels';font.pixelSize:15;color:card.accent}
 Text{id:num;x:17;y:47;text:card.value;font.family:'Bulky Pixels';font.pixelSize:27;color:'#eff7ff'}
 Text{x:Math.min(160,num.x+num.paintedWidth+6);y:60;text:card.unit;font.family:'Noto Sans';font.pixelSize:14;color:'#dceeff'}
 Text{x:17;y:93;width:190;elide:Text.ElideRight;text:card.detail;font.family:'Noto Sans';font.pixelSize:12;color:'#dceeff'}
 Rectangle{x:17;y:139;width:182;height:6;radius:3;color:'#80334e65'
  Rectangle{width:Math.max(0,Math.min(parent.width,parent.width*card.fraction));height:6;radius:3;color:card.accent}
 }
}
