import QtQuick
import QtQuick.Effects
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls as QQC2
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as Plasma5Support
PlasmoidItem {
 id: root
    function shellQuote(value) { return "'" + value.replace(/'/g, "'\\''") + "'" }
 Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
 preferredRepresentation: compactRepresentation
 readonly property int displayMode: Number(Plasmoid.configuration.displayMode||0)
 readonly property bool compactMode: displayMode===1
 readonly property bool semiCompactMode: displayMode===2
 readonly property bool showHeader: !compactMode
 readonly property bool showRecent: displayMode===0
 readonly property int surfaceHeight: compactMode ? 182 : (semiCompactMode ? 292 : 419)
 implicitWidth: 390; implicitHeight: surfaceHeight
 Layout.preferredWidth:390;Layout.preferredHeight:root.surfaceHeight
 Layout.minimumWidth:280;Layout.minimumHeight:root.compactMode?140:270
 property var library: ({recent:[],installed:0,profiles:[],controllers:[],details:{},active:""})
 property string feedback: ""
 property string selectedProfile: ""
 property bool chooserOpen: false
 property bool busy: false
 readonly property string helper: "python3 " + shellQuote(decodeURIComponent(Qt.resolvedUrl("../scripts/rog-gaming-helper.py").toString().replace(/^file:\/\//, "")))
 readonly property int themeIndex: Math.max(0,Math.min(3,Number(Plasmoid.configuration.themeIndex||0)))
 readonly property var accents: ["#50cfff","#b38cff","#48e5bc","#ffbb66"]
 readonly property var complements: ["#ffbd69","#5ce4cf","#c7a0ff","#73baff"]
 readonly property color accent: accents[themeIndex]
 readonly property color iconAccent: complements[themeIndex]
 readonly property real opacityLevel: Math.max(0,Math.min(90,Number(Plasmoid.configuration.backgroundOpacity||0)))/100
 function profileIcon(name) {
  let n=String(name||"").toLowerCase()
  if (/(extreme|ultimate|max(imum)?)(-|_|$)/.test(n) || n.indexOf("extreme")>=0) return "extreme"
  if (n.indexOf("battery")>=0 || n.indexOf("eco")>=0) return "leaf"
  if (n.indexOf("gaming")>=0 || n.indexOf("game")>=0) return "gamepad"
  if (n.indexOf("performance")>=0 || n.indexOf("turbo")>=0 || n.indexOf("boost")>=0) return "bolt"
  if (n.indexOf("quiet")>=0 || n.indexOf("silent")>=0) return "moon"
  return "profile"
 }
 readonly property var otherProfiles: (library.profiles||[]).filter(function(n){
  return n!==library.active && n!=="custom" &&
    (Plasmoid.configuration.showFirmware || ["quiet","balanced","performance"].indexOf(n)<0)
 })
 function launch() {
  if(busy || !selectedProfile)return
  busy=true;feedback="Preparing Gaming Mode..."
  commands.connectSource(helper+" launch "+selectedProfile)
 }
 compactRepresentation: Item {
  implicitWidth:390;implicitHeight:root.surfaceHeight;clip:true
  Item {
   id: panel;width:390;height:root.surfaceHeight;transformOrigin:Item.TopLeft
   readonly property real factor:Math.max(.01,Math.min(parent.width/390,parent.height/root.surfaceHeight))
   scale:factor;x:(parent.width-width*factor)/2;y:(parent.height-height*factor)/2
   Rectangle{anchors.fill:parent;color:Qt.rgba(.025,.055,.11,root.opacityLevel);radius:20}
   Text{visible:root.showHeader;x:24;y:17;text:"ROG FLOW Z13";font.family:"Bulky Pixels";font.pixelSize:16;color:root.accent}
   Image{visible:root.showHeader;x:320;y:12;width:50;height:38;fillMode:Image.PreserveAspectFit;source:"../images/rog-eye-"+["cyan","purple","emerald","amber"][root.themeIndex]+".svg"}
   Text{visible:root.showHeader;x:24;y:48;text:"GAMING HUD";font.family:"Bulky Pixels";font.pixelSize:28;color:"#eff7ff"}
   Rectangle{visible:root.showHeader;x:24;y:98;width:342;height:1;color:root.accent;opacity:.5}
   Rectangle {
    x:16;y:root.compactMode?6:112;width:170;height:170;radius:16
    color:Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.23)
    border.width:2;border.color:root.accent
    Image {anchors.horizontalCenter:parent.horizontalCenter;y:28;width:91;height:91;source:"../images/steam-symbol.svg";fillMode:Image.PreserveAspectFit}
    Text{anchors.horizontalCenter:parent.horizontalCenter;y:125;text:"GAME MODE";font.family:"Bulky Pixels";font.pixelSize:14;color:root.accent}
    MouseArea{anchors.fill:parent;onClicked:root.chooserOpen=true}
   }
   Grid {
    x:196;y:root.compactMode?6:112;columns:2;spacing:8
    Repeater {
     model:4
     delegate:Rectangle {
      required property int index
      readonly property var pad:index<(root.library.controllers||[]).length?root.library.controllers[index]:null
      width:85;height:81;radius:12
      color:pad?Qt.rgba(root.iconAccent.r,root.iconAccent.g,root.iconAccent.b,.17):Qt.rgba(.07,.14,.22,.16)
      border.width:1;border.color:pad?root.iconAccent:"#51637c"
      Image{anchors.horizontalCenter:parent.horizontalCenter;y:7;width:23;height:23
       source:"../images/gamepad-"+root.themeIndex+".svg";fillMode:Image.PreserveAspectFit
       opacity:pad?1:.38}
      Text{anchors.horizontalCenter:parent.horizontalCenter;y:35;text:pad?"P"+(index+1)+" · "+(pad.battery===null?"—":pad.battery+"%"):"P"+(index+1);font.pixelSize:11;color:pad?"#eff7ff":"#8995a8"}
      Text{anchors.horizontalCenter:parent.horizontalCenter;y:55;text:pad?"CONNECTED":"OFFLINE";font.pixelSize:9;color:pad?root.iconAccent:"#68758c"}
      QQC2.ToolTip.visible: hover.containsMouse
      QQC2.ToolTip.text: pad?pad.name+(pad.battery===null?" · Battery unavailable":" · "+pad.battery+"%"):"Controller slot "+(index+1)
      MouseArea{id:hover;anchors.fill:parent;hoverEnabled:true}
     }
    }
   }
   Text{visible:root.showRecent;x:18;y:294;text:"RECENTLY PLAYED";font.family:"Bulky Pixels";font.pixelSize:13;color:root.accent}
   Text{visible:root.showRecent;x:320;y:295;text:"LAST 5";font.pixelSize:11;color:root.iconAccent}
   Row {
    visible:root.showRecent;x:17;y:316;spacing:7
    Repeater {
     model:5
     delegate:Rectangle {
      required property int index
      readonly property var game:index<(root.library.recent||[]).length?root.library.recent[index]:null
      width:65;height:78;radius:8
      color:Qt.rgba(.07,.14,.22,.38)
      border.width:coverHover.containsMouse?2:1
      border.color:coverHover.containsMouse?root.iconAccent:root.accent
      Rectangle {
       id:coverMask;anchors.fill:parent;anchors.margins:1;radius:7
       color:"white";visible:false
       layer.enabled:true
      }
      Image {
       id:coverImage;anchors.fill:parent;anchors.margins:1
       source:parent.game&&parent.game.art?parent.game.art:""
       fillMode:Image.PreserveAspectCrop;asynchronous:true
       visible:status===Image.Ready
       layer.enabled:true
       layer.effect:MultiEffect {maskEnabled:true;maskSource:coverMask}
      }
      Text{anchors.centerIn:parent;width:parent.width-6;horizontalAlignment:Text.AlignHCenter;wrapMode:Text.Wrap;maximumLineCount:3;elide:Text.ElideRight;visible:coverImage.status!==Image.Ready;text:parent.game?parent.game.name:"▣";font.pixelSize:parent.game?10:20;color:root.iconAccent}
      MouseArea{id:coverHover;anchors.fill:parent;hoverEnabled:true}
      QQC2.ToolTip.visible:coverHover.containsMouse && !!game
      QQC2.ToolTip.delay:400
      QQC2.ToolTip.text:game?game.name:""
     }
    }
   }
   Text{visible:root.showRecent;x:19;y:405;width:350;elide:Text.ElideRight;text:root.feedback||("STEAM LIBRARY  ·  "+root.library.installed+" INSTALLED");font.pixelSize:11;color:root.iconAccent}

  }
 }
 Window {
  id:profileDialog
  width:390;height:405
  visible:root.chooserOpen
  flags:Qt.Dialog | Qt.FramelessWindowHint
  modality:Qt.NonModal
  title:"ROG Gaming Mode — Select Profile"
  color:"transparent"
  transientParent:root.Window.window
  x:root.Window.window ? root.Window.window.x + Math.max(0,(root.Window.window.width-width)/2) : 150
  y:root.Window.window ? root.Window.window.y + Math.max(0,(root.Window.window.height-height)/2) : 150
  onVisibleChanged: { if (visible) requestActivate() }
  onClosing:(event)=>{root.chooserOpen=false}
  Shortcut {sequence:"Escape";onActivated:root.chooserOpen=false}
   Rectangle {
    anchors.fill:parent
    color:"#ee091725";radius:18;border.width:2;border.color:root.accent
    Text{x:18;y:17;text:"SELECT POWER PROFILE";font.family:"Bulky Pixels";font.pixelSize:17;color:root.accent}
    QQC2.Button{x:337;y:9;width:40;height:34;text:"×";onClicked:root.chooserOpen=false}
    Text{x:18;y:48;text:"CURRENTLY RUNNING";font.pixelSize:11;font.bold:true;color:root.iconAccent}
    Rectangle {
     x:16;y:66;width:358;height:61;radius:11
     color:Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.30)
     border.width:1;border.color:root.accent
     Image{x:15;y:17;width:26;height:26;source:"../images/"+root.profileIcon(root.library.active)+"-"+root.themeIndex+".svg"}
     Text{x:51;y:10;text:String(root.library.active||"unknown").replace(/-/g," ").toUpperCase();font.pixelSize:14;font.bold:true;color:"#eff7ff"}
     Text{x:51;y:33;text:(root.library.details||{})[root.library.active]||"Active power profile";font.pixelSize:11;color:"#dceeff"}
     Text{x:321;y:15;text:root.selectedProfile===root.library.active?"✔":"●";font.pixelSize:23;color:root.iconAccent}
     MouseArea{anchors.fill:parent;onClicked:root.selectedProfile=root.library.active}
    }
    Rectangle{x:16;y:138;width:358;height:1;color:root.accent;opacity:.6}
    Text{x:18;y:145;text:"CHOOSE ANOTHER PROFILE";font.pixelSize:11;font.bold:true;color:root.accent}
    Flickable {
     id:launchProfileScroll
     x:16;y:166;width:358;height:163;clip:true
     contentWidth:width;contentHeight:choices.height
     boundsBehavior:Flickable.StopAtBounds
     flickableDirection:Flickable.VerticalFlick
     QQC2.ScrollBar.vertical: QQC2.ScrollBar {
      id:launchProfileBar
      policy:QQC2.ScrollBar.AsNeeded
      width:8
      contentItem:Rectangle {radius:4;color:root.accent}
      background:Rectangle {radius:4;color:Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.13)}
     }
     WheelHandler {
      target:null
      onWheel:(event)=>{
       launchProfileScroll.contentY=Math.max(0,Math.min(
        Math.max(0,launchProfileScroll.contentHeight-launchProfileScroll.height),
        launchProfileScroll.contentY-event.angleDelta.y/2))
       event.accepted=true
      }
     }
     Column {
      id:choices;spacing:9;width:344
      Repeater {
       model:root.otherProfiles
       delegate:Rectangle {
        required property string modelData
        width:344;height:69;radius:11
        color:root.selectedProfile===modelData?Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.52):Qt.rgba(.10,.22,.32,.6)
        border.width:root.selectedProfile===modelData?2:1
        border.color:root.selectedProfile===modelData?root.accent:"#52728a"
        Image{x:16;y:17;width:25;height:25;source:"../images/"+root.profileIcon(modelData)+"-"+root.themeIndex+".svg";fillMode:Image.PreserveAspectFit}
        Text{x:52;y:10;width:250;elide:Text.ElideRight;text:modelData.replace(/-/g," ").toUpperCase();font.bold:true;font.pixelSize:13;color:"#eff7ff"}
        Text{x:52;y:32;width:265;elide:Text.ElideRight;text:(root.library.details||{})[modelData]||"Firmware profile";font.pixelSize:11;color:"#dceeff"}
        Text{x:52;y:51;text:root.selectedProfile===modelData?"SELECTED FOR LAUNCH":"";font.pixelSize:10;color:root.iconAccent}
        Text{x:306;y:14;text:root.selectedProfile===modelData?"✔":"";color:root.iconAccent;font.pixelSize:28;font.bold:true}
        MouseArea{anchors.fill:parent;onClicked:root.selectedProfile=modelData}
       }
      }
     }
    }
    Text {
     anchors.right:launchProfileScroll.right;anchors.rightMargin:13
     anchors.bottom:launchProfileScroll.bottom
     visible:launchProfileScroll.contentY<launchProfileScroll.contentHeight-launchProfileScroll.height-2
     text:"⌄";font.pixelSize:19;color:root.iconAccent
    }
    QQC2.Button {
     x:16;y:349;width:358;height:45
     text:root.busy?"Switching...":"LAUNCH WITH "+root.selectedProfile.toUpperCase()
     enabled:!!root.selectedProfile && !root.busy
     onClicked:root.launch()
    }
   }
 }
 fullRepresentation:compactRepresentation
 Plasma5Support.DataSource{
  id:poll;engine:"executable";connectedSources:[root.helper];interval:30000
  onNewData:function(source,data){
   if(!data||!data.stdout)return
   try{
    let obj=JSON.parse(data.stdout)
    if(obj.ok){
     root.library=obj
     if(!root.selectedProfile){
      root.selectedProfile=(obj.profiles||[]).indexOf(obj.active)>=0?obj.active:(obj.profiles[0]||"")
     }
    }else root.feedback=obj.error
   }catch(e){root.feedback=String(e)}
  }
 }
 Plasma5Support.DataSource{
  id:commands;engine:"executable";interval:0
  onNewData:function(source,data){
   try{let obj=JSON.parse(data.stdout||"{}");root.feedback=obj.ok?obj.message:obj.error}
   catch(e){root.feedback=String(e)}
   root.busy=false;disconnectSource(source)
  }
 }
}
