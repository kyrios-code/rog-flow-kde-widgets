import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
Kirigami.FormLayout {
 id: page
 property int cfg_displayMode: 0
 Kirigami.Separator {Kirigami.FormData.isSection:true;Kirigami.FormData.label:"Display layout"}
 QQC2.RadioButton {Kirigami.FormData.label:"Display mode:";text:"Full — show ROG header and title";checked:page.cfg_displayMode===0;onClicked:page.cfg_displayMode=0}
 QQC2.RadioButton {text:"Semi-Compact — cards only, hide ROG header and title";checked:page.cfg_displayMode===1;onClicked:page.cfg_displayMode=1}
}
