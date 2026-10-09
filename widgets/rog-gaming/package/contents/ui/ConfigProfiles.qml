import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
Kirigami.FormLayout {
 property alias cfg_showFirmware: firmware.checked
 Kirigami.Separator {Kirigami.FormData.isSection:true;Kirigami.FormData.label:"Profile visibility"}
 QQC2.CheckBox {id:firmware;Kirigami.FormData.label:"Firmware modes:";text:"Show Quiet, Balanced and Performance"}
 QQC2.Label {text:"The running profile always remains visible above the choices, even if it is a hidden firmware mode.";wrapMode:Text.WordWrap;Layout.maximumWidth:460;color:Kirigami.Theme.disabledTextColor}
}
