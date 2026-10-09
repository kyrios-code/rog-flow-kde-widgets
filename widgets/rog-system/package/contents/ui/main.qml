import QtQuick
import QtQuick.Layouts
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as Plasma5Support

PlasmoidItem {
    id: root
    function shellQuote(value) { return "'" + value.replace(/'/g, "'\\''") + "'" }
    readonly property string helper: "python3 " + shellQuote(decodeURIComponent(Qt.resolvedUrl("../scripts/telemetry.py").toString().replace(/^file:\/\//, "")))
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    readonly property var themes: ["Cyan Glass", "Purple Nebula", "Emerald Circuit", "Amber ROG"]
    readonly property int themeIndex: Math.max(0, Math.min(3, Number(Plasmoid.configuration.themeIndex || 0)))
    readonly property string selectedTheme: themes[themeIndex]
    readonly property real selectedOpacity: Math.max(0, Math.min(90, Number(Plasmoid.configuration.backgroundOpacity || 0))) / 100
    implicitWidth: 480
    readonly property bool semiCompact: Number(Plasmoid.configuration.displayMode||0)===1
    readonly property int visibleHeight: semiCompact ? 960 : 1068
    implicitHeight: visibleHeight
    Layout.minimumWidth: 240
    Layout.minimumHeight: semiCompact ? 480 : 534
    Layout.preferredWidth: 480
    Layout.preferredHeight: visibleHeight

    // Use the compact surface directly to avoid Plasma's full-representation
    // popup/background wrapper; both surfaces still report 480 x 948.
    preferredRepresentation: compactRepresentation
    property var metrics: ({})
    property var downs: []
    property var ups: []

    // Both representations report the ENTIRE dashboard's implicit geometry.
    // New plugin ID also avoids stale geometry from the old widget instance.
    compactRepresentation: ROGViewport {
        semiCompact: root.semiCompact
        themeName: root.selectedTheme
        backgroundOpacity: root.selectedOpacity
        telemetry: root.metrics
        downHistory: root.downs
        upHistory: root.ups
    }
    fullRepresentation: ROGViewport {
        semiCompact: root.semiCompact
        themeName: root.selectedTheme
        backgroundOpacity: root.selectedOpacity
        telemetry: root.metrics
        downHistory: root.downs
        upHistory: root.ups
    }

    Plasma5Support.DataSource {
        engine: "executable"
        connectedSources: [root.helper]
        interval: 2000
        onNewData: function(sourceName, data) {
            if (!data || !data.stdout) return
            try {
                const obj = JSON.parse(data.stdout)
                root.metrics = obj
                let d = root.downs.slice()
                d.push(Number(obj.down) || 0)
                if (d.length > 60) d.shift()
                root.downs = d
                let u = root.ups.slice()
                u.push(Number(obj.up) || 0)
                if (u.length > 60) u.shift()
                root.ups = u
            } catch (e) { console.warn("ROG telemetry:", e) }
        }
    }
}
