# Release checklist

Things that are deliberately different in test builds. Go through this list before building a release.

1. **Unlocks.** `Progression.TestUnlockAll` (`Assets/MachineBrigade/Scripts/Game/Match/Progression.cs`) is `true` in test builds.
   - It unlocks every card (vehicles, strikes, premium units) and every doctrine.
   - It also lets Normal-difficulty enemies field the whole roster, because their deck follows the player's unlocks.
   - Set it to `false` for a release. The campaign rewards and shop unlocks then work as designed.
2. **Camera shake.** `RtsCamera.ShakeEnabled` is `false`: shake was switched off at the user's request because it read as stutter.
   - Turning it back on restores every shake source.
3. **Ads.** `Ads.cs` is still the placeholder. It needs the real AdMob SDK and ad unit IDs.
4. **Build.** Build a signed release AAB, not the development APK (`BuildScripts.BuildAndroidDevApk`). Swappy frame pacing is only enabled in release builds.
