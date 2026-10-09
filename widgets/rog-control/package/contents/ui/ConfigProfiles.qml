import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
    property alias cfg_showFirmware: firmware.checked

    Kirigami.Separator {
        Kirigami.FormData.isSection: true
        Kirigami.FormData.label: "Profile visibility"
    }
    QQC2.CheckBox {
        id: firmware
        Kirigami.FormData.label: "Firmware modes:"
        text: "Show Quiet, Balanced and Performance"
    }
    QQC2.Label {
        text: "Custom z13ctl profiles are shown automatically. AC and battery targets remain visible on the HUD even when firmware profiles are hidden."
        wrapMode: Text.WordWrap
        Layout.fillWidth: true
        Layout.maximumWidth: 470
        color: Kirigami.Theme.disabledTextColor
    }
}
