# ![](resources/anymacro/32x32.png) AnyMacro

AnyMacro is an Autodesk® Fusion 360™ add-in for chaining multiple commands in a row to form `Macros`. Macros are created from a set of commands run while the add-in is recording and will fire each of them consecutively. Additionally, the macros created are able to be mapped to keyboard shortcuts for ease of access.


## Built-in Macros

The built-in commands are always visible in the *AnyShortcut* menu. Assign shortcuts to them in the usual way.

Built-in commands include:

 * Align Camera

![Screenshot](builtin_screenshot.png)

## Recording

When enabled, the add-in records the resulting commands of actions that the user performs and collects them in the *AnyMacro* menu. The commands in the menu can then be assigned shortcut keys in the regular way.

If not stopped, the recording stops automatically after a number of commands, to avoid any performance degradation when the user is not setting up shortcuts.

\* Not all actions in Fusion 360™ result in "Commands" and some commands are not usable on their own. For example, *Pick Circle/Arc Tangent* does not generate a "Command" and *Roll History Marker Here* is triggered when clicking rewind in the history, but rewind actually first selects an item and then rolls.

![Screenshot](tracker_screenshot.png)

### Usage

To set up a macro:

* Click *Start recording* and then launch a series of commands in the order you desire for your macro.
* If the commands you chose are able to be recorded, they will be added underneath the record command in the *Command Recorder* dropdown at the top of the *AnyMacro* panel.
* Should you desire to remove a command, you need just click its name within the dropdown.
* Once you stop recording, two new options: *Save Macro* and *Reset Recording*; should appear just under the record command along with a test macro at the bottom of the list. The test macro allows you to make sure everything works before you save it and see the changes you make to the command list.
* Finally, once you are satisfied with the macro, hit the *Save Macro* button. This will display a prompt that will ask you to name your macro. There are few restrictions on the name, however, make sure there are *some* numbers or letters as its ID will be created using the `str.isidentifier()` method for each character.
* You should now find your command under the *Custom Macros* dropdown. You can assign it to keys, run, and delete it right from the command. Additionaly, the macro is persistant, meaning it will remain between sessions of fusion360 and only needs to be created once.

To remove a macro, navigate to its location under the *Custom Macros* dropdown and select the remove option under it. A prompt will appear asking if you are sure you wish to remove it.

## Fusion 360 Quirks

Be aware of the following quirks in Fusion 360™.

* Fusion 360™ cannot handle all key combinations. Forget Alt+Left to rollback history, because fusion cannot save this combination and it will be broken next time you start the application.

* Menu items in sub-menus are not always clickable ([bug](https://forums.autodesk.com/t5/fusion-360-api-and-scripts/api-bug-cannot-click-menu-items-in-nested-dropdown/td-p/9669144)).

## Supported Platforms

  * Windows
  * Mac OS

## Installation

Download the add-in from the [Releases](https://github.com/zxynine/AnyMacro/releases) page.

Unpack it into `API\AddIns` (see [How to install an add-in or script in Fusion 360](https://knowledge.autodesk.com/support/fusion-360/troubleshooting/caas/sfdcarticles/sfdcarticles/How-to-install-an-ADD-IN-and-Script-in-Fusion-360.html)).

Make sure the directory is named `AnyMacro`, with no suffix.

The new menu *`TOOLS`* -> *`ANYMACRO`* is now available.

The add-in can be temporarily disabled using the *Scripts and Add-ins* dialog. Press *`Shift+S`* in Fusion 360™ and go to the *Add-Ins* tab.

## Reporting Issues

If you get any problems, please check out the section on [Fusion 360 quirks](#fusion-360-quirks).

If that does not apply to you, please report any issues that you find in the add-in on the [Issues](https://github.com/zxynine/AnyMacro/issues) page.

For better support, please include the steps you performed and the result. Also include copies of any error messages.

## Author

This add-in is created by ZXYNINE and is based off of Thomas Axelsson's AnyShortcut.

## License

This project is licensed under the terms of the MIT license. See [LICENSE](LICENSE).

## More Fusion 360™ Add-ins

[My Fusion 360™ app store page](https://apps.autodesk.com/en/Publisher/PublisherHomepage?ID=JLH9M8296BET)

[All my add-ins on Github](https://github.com/topics/fusion-360?q=user%3Athomasa88)

## Changelog

* v 0.1.0
  * Original Implementation 

