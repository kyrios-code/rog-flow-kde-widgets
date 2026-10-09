import QtQuick
import QtQuick.Layouts

Item {
    id: viewport
    implicitWidth: 480
    property bool semiCompact: false
    implicitHeight: semiCompact ? 960 : 1068
    Layout.minimumWidth: 240
    Layout.minimumHeight: semiCompact ? 480 : 534
    Layout.preferredWidth: 480
    Layout.preferredHeight: semiCompact ? 960 : 1068
    clip: true

    property string themeName: "Cyan Glass"
    property real backgroundOpacity: 0
    property var telemetry: ({})
    property var downHistory: []
    property var upHistory: []

    readonly property real factor: Math.max(0.001, Math.min(width / 480, height / (semiCompact ? 960 : 1068)))

    HyrulePanel {
        width: 480
        height: 1068
        transformOrigin: Item.TopLeft
        scale: viewport.factor
        x: (viewport.width - width * viewport.factor) / 2
        y: viewport.semiCompact ? -108 * viewport.factor : (viewport.height - height * viewport.factor) / 2
        showHeader: !viewport.semiCompact
        themeName: viewport.themeName
        backgroundOpacity: viewport.backgroundOpacity
        telemetry: viewport.telemetry
        downHistory: viewport.downHistory
        upHistory: viewport.upHistory
    }
}
