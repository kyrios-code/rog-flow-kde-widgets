import QtQuick
import org.kde.plasma.configuration
ConfigModel {
    ConfigCategory {
        name: "Appearance"
        icon: "preferences-desktop-theme"
        source: "ConfigAppearance.qml"
    }
ConfigCategory {name:"Display";icon:"view-grid";source:"ConfigDisplay.qml"}
}
