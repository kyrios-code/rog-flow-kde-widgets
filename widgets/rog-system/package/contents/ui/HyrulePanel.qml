import QtQuick
import org.kde.kirigami as Kirigami
Item {
 id:p;implicitWidth:480;implicitHeight:1068
 property var telemetry:({});property var downHistory:[];property var upHistory:[]
 property bool showOuterBorder: false
 property bool showHeader: true
 property string themeName: 'Cyan Glass'
 readonly property int themeIndex: Math.max(0,["Cyan Glass","Purple Nebula","Emerald Circuit","Amber ROG"].indexOf(themeName))
 property real backgroundOpacity: 0
 readonly property color accent: themeName === 'Purple Nebula' ? p.purple : themeName === 'Emerald Circuit' ? '#48e5bc' : themeName === 'Amber ROG' ? '#ffbb66' : '#50cfff'
 readonly property color edge: themeName === 'Purple Nebula' ? '#9977cc' : themeName === 'Emerald Circuit' ? '#369c88' : themeName === 'Amber ROG' ? '#c18b56' : '#50a6d1'
 readonly property color panelFill: Qt.rgba(0.025,0.055,0.11,Math.max(0,Math.min(1,backgroundOpacity)))
 readonly property color cyan:accent;readonly property color purple:'#b38cff';readonly property color pale:'#dceeff'
 function v(k,def){return telemetry[k]===undefined ? (def===undefined?'—':def) : String(telemetry[k])}
 Rectangle{anchors.fill:parent;radius:23;color:p.panelFill;border.width:p.showOuterBorder ? 1 : 0;border.color:'#8c50b8dc'}
 Text{visible:p.showHeader;x:24;y:17;text:'ROG FLOW Z13';font.family:'Bulky Pixels';font.pixelSize:16;color:p.cyan}
 Image { visible:p.showHeader; x:402; y:14; width:48; height:38; fillMode:Image.PreserveAspectFit; smooth:true
   source: "../images/rog-eye-" + (p.themeName === "Purple Nebula" ? "purple" : p.themeName === "Emerald Circuit" ? "emerald" : p.themeName === "Amber ROG" ? "amber" : "cyan") + ".svg" }
 Text{visible:p.showHeader;x:24;y:48;text:'SYSTEM HUD';font.family:'Bulky Pixels';font.pixelSize:28;color:'#eff7ff'}
 Rectangle{visible:p.showHeader;x:24;y:98;width:432;height:1;color:p.edge;opacity:.5}
 HCard{themeIndex:p.themeIndex;accent:p.accent;edge:p.edge;fillOpacity:p.backgroundOpacity;x:16;y:115;title:'CPU';value:p.v('cpu','0');unit:'%';detail:p.v('temp')+'°C APU · '+p.v('fan');fraction:Number(p.telemetry.cpu||0)/100}
 HCard{themeIndex:p.themeIndex;accent:p.accent;edge:p.edge;fillOpacity:p.backgroundOpacity;x:248;y:115;title:'GPU';value:p.v('gpu');unit:'%';detail:'Radeon 8060S';fraction:Number(p.telemetry.gpu||0)/100}
 HCard{themeIndex:p.themeIndex;accent:p.accent;edge:p.edge;fillOpacity:p.backgroundOpacity;x:16;y:288;title:'MEMORY';value:p.v('mem');unit:'GiB';detail:p.v('memDetail');fraction:Number(p.telemetry.memPct||0)/100}
 HCard{themeIndex:p.themeIndex;accent:p.accent;edge:p.edge;fillOpacity:p.backgroundOpacity;x:248;y:288;title:'BATTERY';value:p.v('battery');unit:'%';detail:p.v('batteryDetail');fraction:Number(p.telemetry.battery||0)/100}

 // Compact, aligned three-card telemetry strip.
 Repeater {
  model: [
   {name:"APU TEMP", icon:"thermometer", value:p.v("temp"), unit:"°C", sub:"Processor"},
   {name:"FAN SPEED", icon:"fan", value:p.v("fan").replace(/[^0-9]/g,""), unit:"RPM", sub:"Cooling fan"},
   {name:"TDP LIMIT", icon:"bolt", value:p.v("pl1"), unit:"W", sub:"PL2 "+p.v("pl2")+"W · PL3 "+p.v("pl3")+"W"}
  ]
  delegate: Rectangle {
   required property var modelData
   required property int index
   x:16+index*154; y:461; width:140; height:105; radius:16
   color:p.panelFill; border.width:1; border.color:p.edge
   Text {x:11;y:11;text:modelData.name;font.family:"Bulky Pixels";font.pixelSize:11;color:p.accent}
   Image {x:111;y:9;width:17;height:17;source:"../images/"+modelData.icon+"-"+p.themeIndex+".svg";fillMode:Image.PreserveAspectFit}
   Row {
    x:11;y:38;spacing:4
    Text {text:modelData.value;font.family:"Bulky Pixels";font.pixelSize:15;color:"#eff7ff"}
    Text {text:modelData.unit;font.family:"Noto Sans";font.pixelSize:10;color:p.pale;anchors.baseline:parent.children[0].baseline}
   }
   Text {x:11;y:79;width:119;elide:Text.ElideRight;text:modelData.sub;font.family:"Noto Sans";font.pixelSize:9;color:p.pale}
  }
 }
 HSection{themeIndex:p.themeIndex;accent:p.accent;edge:p.edge;fillOpacity:p.backgroundOpacity;x:16;y:581;width:448;height:74;title:'GRAPHICS MEMORY'
  Text{x:17;y:42;text:p.v('gpuMemory');font.family:'Noto Sans';font.pixelSize:14;color:'#eff7ff'}
  Text{x:284;y:42;text:'BIOS: '+p.v('biosVram');font.family:'Noto Sans';font.pixelSize:12;color:p.pale}
 }
 HSection{themeIndex:p.themeIndex;accent:p.accent;edge:p.edge;fillOpacity:p.backgroundOpacity;x:16;y:669;width:448;height:95;title:'SYSTEM & STORAGE'
  Column{x:17;y:39;spacing:3
   Text{text:'Uptime '+p.v('uptime')+'  ·  CPU '+p.v('freq');font.family:'Noto Sans';font.pixelSize:12;color:p.pale}
   Text{text:'Disk '+p.v('disk')+'  ·  Swap '+p.v('swap');font.family:'Noto Sans';font.pixelSize:11;color:p.pale}
   Text{text:'Kernel '+p.v('kernel');font.family:'Noto Sans';font.pixelSize:11;color:p.pale}
  }
 }
 HSection{themeIndex:p.themeIndex;accent:p.accent;edge:p.edge;fillOpacity:p.backgroundOpacity;x:16;y:773;width:448;height:125;title:'NETWORK ACTIVITY'
  Row{x:17;y:39;spacing:10
   Text{text:'↓';font.family:'Noto Sans';font.pixelSize:17;color:p.cyan}
   Text{text:p.v('down','0')+' KiB/s';font.family:'Noto Sans';font.pixelSize:12;color:'#eff7ff';anchors.verticalCenter:parent.verticalCenter}
   Item{width:20;height:1}
   Text{text:'↑';font.family:'Noto Sans';font.pixelSize:17;color:p.purple}
   Text{text:p.v('up','0')+' KiB/s';font.family:'Noto Sans';font.pixelSize:12;color:'#eff7ff';anchors.verticalCenter:parent.verticalCenter}
  }
  Canvas{id:graph;x:17;y:65;width:414;height:48
   onPaint:{let c=getContext('2d');c.clearRect(0,0,width,height);let peak=8,all=p.downHistory.concat(p.upHistory)
    for(let i=0;i<all.length;i++)peak=Math.max(peak,all[i]);c.lineWidth=1;c.strokeStyle='rgba(150,200,235,.20)'
    for(let i=0;i<3;i++){let y=i*height/2;c.beginPath();c.moveTo(0,y);c.lineTo(width,y);c.stroke()}
    function trace(a,col){if(a.length<2)return;c.beginPath();c.lineWidth=1.8;c.strokeStyle=col
     for(let i=0;i<a.length;i++){let x=i*width/59,y=height-Math.min(1,a[i]/peak)*height;if(i===0)c.moveTo(x,y);else c.lineTo(x,y)}c.stroke()}
    trace(p.downHistory,p.accent);trace(p.upHistory,p.purple)}
   Connections{target:p;function onDownHistoryChanged(){graph.requestPaint()} function onUpHistoryChanged(){graph.requestPaint()}}
  }
 }
 HSection{themeIndex:p.themeIndex;accent:p.accent;edge:p.edge;fillOpacity:p.backgroundOpacity;x:16;y:907;width:448;height:65;title:'TOP PROCESSES'
  Text{x:17;y:42;width:414;elide:Text.ElideRight;text:p.v('processes');font.family:'Noto Sans';font.pixelSize:11;color:p.pale}
 }
 HSection{themeIndex:p.themeIndex;accent:p.accent;edge:p.edge;fillOpacity:p.backgroundOpacity;x:16;y:981;width:448;height:75;title:'ACTIVE PROFILE'
  Text{x:17;y:40;text:p.v('profile');font.family:'Bulky Pixels';font.pixelSize:18;color:'#eff7ff'}
  Text{x:349;y:37;text:p.v('pl1')+' W';font.family:'Bulky Pixels';font.pixelSize:21;color:p.cyan}
  Text{x:17;y:59;text:'PL1 '+p.v('pl1')+'W  ·  PL2 '+p.v('pl2')+'W  ·  PL3 '+p.v('pl3')+'W  ·  CO '+p.v('uv');font.family:'Noto Sans';font.pixelSize:10;color:p.pale}
 }
}
