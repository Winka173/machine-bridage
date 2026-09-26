#!/usr/bin/env bash
# Installs the development APK on a connected device or emulator, launches it and
# streams Unity's log. Usage: Tools/run-android.sh [device-serial]
set -euo pipefail

APK="Builds/Android/MachineBrigade-dev.apk"
PACKAGE="com.winka.machinebrigade"
ADB="${ANDROID_HOME:-$LOCALAPPDATA/Android/Sdk}/platform-tools/adb"

serial="${1:-$("$ADB" devices | awk 'NR > 1 && $2 == "device" { print $1; exit }')}"
if [[ -z "$serial" ]]; then
  echo "No device or emulator attached (check 'adb devices')." >&2
  exit 1
fi

"$ADB" -s "$serial" install -r "$APK"
"$ADB" -s "$serial" logcat -c
"$ADB" -s "$serial" shell monkey -p "$PACKAGE" -c android.intent.category.LAUNCHER 1 > /dev/null
echo "Launched $PACKAGE on $serial. Ctrl+C stops the log."
"$ADB" -s "$serial" logcat -s Unity:V AndroidRuntime:E
