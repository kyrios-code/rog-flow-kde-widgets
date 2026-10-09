import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as Plasma5Support
PlasmoidItem {
 id: root
    function shellQuote(value) { return "'" + value.replace(/'/g, "'\\''") + "'" }
 Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
 readonly property bool semiCompact: Number(Plasmoid.configuration.displayMode||0)===1
 readonly property int visibleHeight: semiCompact?470:565
 implicitWidth: 410; implicitHeight: visibleHeight
 Layout.preferredWidth: 410; Layout.preferredHeight: visibleHeight
 Layout.minimumWidth: 290; Layout.minimumHeight: semiCompact?300:360
 preferredRepresentation: compactRepresentation
 property var readings: ({profiles:[]})
 property string feedback: ""
 property bool busy: false
 property string target: "keyboard"
 property string effect: "static"
 property string brightness: "high"
 property string rgb: "50CFFF"
 readonly property var themeColors: ["#50cfff","#b38cff","#48e5bc","#ffbb66"]
 readonly property int themeIndex: Math.max(0,Math.min(3,Number(Plasmoid.configuration.themeIndex||0)))
 readonly property color iconAccent: ["#ffbd69","#5ce4cf","#c7a0ff","#73baff"][themeIndex]
 readonly property color accent: themeColors[Math.max(0,Math.min(3,Number(Plasmoid.configuration.themeIndex||0)))]
 readonly property real opacityLevel: Math.max(0,Math.min(90,Number(Plasmoid.configuration.backgroundOpacity||0)))/100
 readonly property string helper: "python3 " + shellQuote(decodeURIComponent(Qt.resolvedUrl("../scripts/rog-control-helper.py").toString().replace(/^file:\/\//, "")))
 function profileIcon(name) {
  let n=String(name||"").toLowerCase()
  if (/(extreme|ultimate|max(imum)?)(-|_|$)/.test(n) || n.indexOf("extreme")>=0) return "extreme"
  if (n.indexOf("battery")>=0 || n.indexOf("eco")>=0) return "leaf"
  if (n.indexOf("gaming")>=0 || n.indexOf("game")>=0) return "gamepad"
  if (n.indexOf("performance")>=0 || n.indexOf("turbo")>=0 || n.indexOf("boost")>=0) return "bolt"
  if (n.indexOf("quiet")>=0 || n.indexOf("silent")>=0) return "moon"
  return "profile"
 }
 function send(args) {
  if (busy) return
  busy=true;feedback="Applying..."
  actions.connectSource(helper+" "+args)
 }
 compactRepresentation: Item {
  implicitWidth:410;implicitHeight:root.visibleHeight;clip:true
  Item {
   id: panel;width:410;height:565;transformOrigin:Item.TopLeft
   readonly property real factor:Math.max(.01,Math.min(parent.width/410,parent.height/root.visibleHeight))
   scale:factor;x:(parent.width-width*factor)/2;y:root.semiCompact?-95*factor:(parent.height-height*factor)/2
   Rectangle{anchors.fill:parent;color:Qt.rgba(.025,.055,.11,root.opacityLevel);radius:22}
   Text{visible:!root.semiCompact;x:20;y:18;text:"ROG FLOW Z13";font.family:"Bulky Pixels";font.pixelSize:16;color:root.accent}
   Image { visible:!root.semiCompact; x:346; y:15; width:46; height:38; fillMode:Image.PreserveAspectFit; smooth:true
     source: "../images/rog-eye-" + ["cyan","purple","emerald","amber"][Math.max(0,Math.min(3,Number(Plasmoid.configuration.themeIndex||0)))] + ".svg" }
   Text{visible:!root.semiCompact;x:20;y:46;text:"CONTROL HUD";font.family:"Bulky Pixels";font.pixelSize:26;color:"#eff7ff"}
   Rectangle{visible:!root.semiCompact;x:20;y:83;width:370;height:1;color:root.accent;opacity:.5}
   Rectangle{
    x:12;y:98;width:386;height:260;radius:17;color:Qt.rgba(.025,.055,.11,root.opacityLevel);border.width:1;border.color:root.accent
    Image {x:350;y:12;width:18;height:18;source:"../images/profile-"+root.themeIndex+".svg"}
    Text{x:15;y:12;text:"PERFORMANCE PROFILES";font.pixelSize:15;font.bold:true;color:root.accent}
    Text{x:15;y:38;width:350;elide:Text.ElideRight;text:root.readings.autoswitch?"AC: "+root.readings.ac+"  •  BAT: "+root.readings.battery:"Autoswitch disabled";font.pixelSize:11;color:"#dceeff"}
    Flickable{
     id:profileScroll
     x:12;y:60;width:362;height:184;clip:true
     contentWidth:width;contentHeight:cards.height
     boundsBehavior:Flickable.StopAtBounds
     flickableDirection:Flickable.VerticalFlick
     QQC2.ScrollBar.vertical: QQC2.ScrollBar {
      id:profileBar
      policy:QQC2.ScrollBar.AsNeeded
      width:8
      contentItem:Rectangle {radius:4;color:root.accent}
      background:Rectangle {radius:4;color:Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.13)}
     }
     WheelHandler {
      target:null
      onWheel:(event)=>{
       profileScroll.contentY=Math.max(0,Math.min(
        Math.max(0,profileScroll.contentHeight-profileScroll.height),
        profileScroll.contentY-event.angleDelta.y/2))
       event.accepted=true
      }
     }
     Grid{
      id:cards;columns:2;spacing:8;width:350
      Repeater{
       model:(root.readings.profiles||[]).filter(function(n){return Plasmoid.configuration.showFirmware||["quiet","balanced","performance"].indexOf(n)<0}).filter(function(n){return n!=="custom"})
       delegate:Rectangle{
        required property string modelData
        width:170;height:85;radius:12;color:root.readings.active===modelData?Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.70):Qt.rgba(.025,.055,.11,.12);border.width:root.readings.active===modelData?2:1;border.color:root.readings.active===modelData?root.accent:Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.50)
        Text{x:10;y:8;width:120;elide:Text.ElideRight;text:modelData.replace(/-/g," ").toUpperCase();font.pixelSize:12;font.bold:true;color:"#eff7ff"}
        Image {x:143;y:7;width:18;height:18;fillMode:Image.PreserveAspectFit
         source:"../images/"+root.profileIcon(modelData)+"-"+root.themeIndex+".svg"}
        Text{x:10;y:29;width:150;elide:Text.ElideRight;text:(root.readings.details||{})[modelData]||"Firmware profile";font.pixelSize:11;color:"#eff7ff"}
        Text{x:10;y:62;width:150;elide:Text.ElideRight;text:(root.readings.active===modelData?"✓ ACTIVE ":"")+(root.readings.ac===modelData?"⌁ AC ":"")+(root.readings.battery===modelData?"▣ BAT":"");font.pixelSize:10;color:root.readings.active===modelData?"#ffffff":root.accent}
        MouseArea{anchors.fill:parent;onClicked:root.send("profile "+modelData)}
       }
      }
     }
    }
    Text {
     anchors.right:profileScroll.right;anchors.rightMargin:12
     anchors.bottom:profileScroll.bottom;anchors.bottomMargin:1
     visible:profileScroll.contentY<profileScroll.contentHeight-profileScroll.height-2
     text:"⌄";font.pixelSize:19;color:root.iconAccent
    }
   }
   Rectangle{
    x:12;y:370;width:386;height:183;radius:17;color:Qt.rgba(.025,.055,.11,root.opacityLevel);border.width:1;border.color:root.accent
    Image {x:350;y:10;width:18;height:18;source:"../images/rgb-"+root.themeIndex+".svg"}
    Text{x:15;y:10;text:"RGB LIGHTING";font.pixelSize:15;font.bold:true;color:root.accent}
    Row{x:12;y:39;spacing:8
     Repeater{
      model:[{id:"keyboard",name:"Keyboard"},{id:"lightbar",name:"Lightbar"},{id:"all",name:"Both"}]
      delegate:Rectangle{
       required property var modelData
       width:112;height:29;radius:9;color:root.target===modelData.id?Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.70):"transparent";border.width:root.target===modelData.id?2:1;border.color:root.target===modelData.id?root.accent:Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.45)
       Text{anchors.centerIn:parent;text:modelData.name;font.pixelSize:12;font.bold:root.target===modelData.id;color:"#eff7ff"}
       MouseArea{anchors.fill:parent;onClicked:root.target=modelData.id}
      }
     }
    }
    QQC2.ComboBox{id:modeBox;x:12;y:78;width:174;model:["static","breathe","cycle","rainbow","strobe"];onActivated:root.effect=currentText}
    QQC2.ComboBox{id:levelBox;x:199;y:78;width:174;model:["off","low","medium","high"];currentIndex:3;onActivated:root.brightness=currentText}
    Row{x:12;y:128;spacing:8
     Repeater{
      model:["50CFFF","B38CFF","48E5BC","FFBB66","FF527A","FFFFFF"]
      delegate:Rectangle{
       required property string modelData
       width:27;height:27;radius:7;color:"#"+modelData;border.width:root.rgb===modelData?3:1;border.color:root.rgb===modelData?"#ffffff":"#789"
       MouseArea{anchors.fill:parent;onClicked:root.rgb=modelData}
      }
     }
     QQC2.Button{width:104;height:30;text:"Apply";onClicked:root.send("lighting "+root.target+" "+root.effect+" "+root.rgb+" "+root.brightness+" normal")}
    }
   }
   Text{x:18;y:552;width:374;elide:Text.ElideRight;text:root.feedback;font.pixelSize:11;color:root.accent}
  }
 }
 fullRepresentation: compactRepresentation
 Plasma5Support.DataSource{
  id:poll;engine:"executable";connectedSources:[root.helper];interval:4000
  onNewData:function(src,data){if(!data||!data.stdout)return;try{let o=JSON.parse(data.stdout);if(o.ok)root.readings=o;else root.feedback=o.error}catch(e){root.feedback=String(e)}}
 }
 Plasma5Support.DataSource{
  id:actions;engine:"executable";interval:0
  onNewData:function(src,data){
   try{let o=JSON.parse(data.stdout||"{}");root.feedback=o.ok?(o.message||"Profile applied"):(o.error||"Command failed");if(o.profiles)root.readings=o}
   catch(e){root.feedback="Invalid response"}
   root.busy=false;disconnectSource(src)
  }
 }
}
