import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
Kirigami.FormLayout {
 id:page
 property int cfg_displayMode: 0
 Kirigami.Separator {Kirigami.FormData.isSection:true;Kirigami.FormData.label:"Dashboard layout"}
 QQC2.Label {text:"Choose how much information the Gaming HUD shows.";wrapMode:Text.WordWrap;color:Kirigami.Theme.disabledTextColor}
 QQC2.RadioButton {Kirigami.FormData.label:"Display mode:";text:"Full — header, launch, controllers, recent games";checked:page.cfg_displayMode===0;onClicked:page.cfg_displayMode=0}
 QQC2.RadioButton {text:"Semi-Compact — header, launch and controllers";checked:page.cfg_displayMode===2;onClicked:page.cfg_displayMode=2}
 QQC2.RadioButton {text:"Compact — Steam launch and four controllers only";checked:page.cfg_displayMode===1;onClicked:page.cfg_displayMode=1}
 QQC2.Label {text:"Compact and Semi-Compact use shorter widget surfaces. The profile selector remains available in either mode.";wrapMode:Text.WordWrap;color:Kirigami.Theme.disabledTextColor}
}
