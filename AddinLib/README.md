# ![](resources/AnyMacroIcon/AnyMacroIcon.png) AnyMacro

AnyMacro is an Autodesk® Fusion 360™ add-in for chaining multiple commands in a row to form `Macros`. Macros are created from a set of commands run while the add-in is recording. The macro, when finished, will fire each of the recorded commands consecutively. Additionally, the macros created are able to be mapped to keyboard shortcuts for ease of access.

\* This is not able to nor is it designed to replace the *[AnyShortcut](https://github.com/thomasa88/AnyShortcut)* add-in and thus, any functionality it has is not currently planned to be included in *`AnyMacro`*. This add-in is only based on the work by the creator of that add-in and is completly independant. With that said, using both is highly reccomended as they provide a large range of control over your Fusion 360™ application.

AnyMacro is free, but if you particually like it and wish to see more, consider [buying me a coffee (Ko-fi link)](ko-fi.com/zxynine)

## Features

### -Current:
* Ability to record a series of commands.
* Ability to remove commands from the Test Macro before saving.
* Ability to stop recording, then start again while keeping history.
* Ability to clear the current recorded commands to start again.
* Ability to save the recorded series of commands as a persistant macro.
* Ability to delete any recorded macro.
* Option to block a command from being recorded if it is fired twice in a row.
* Two Built-in Camera orienting commands.
* One Built-in Macro to demonstrate chaining.
* Custom Event which allows API scripts/add-ins to register macros.

### -Planned:
* Create icons for built-in commands
* A built-in command to halt any currently running macro.
* Ability to add custom icons to each macro.
* Possible collaboration with AnyShortcut
* Adding Built-in macros
* A favourites dropdown
* Ability to edit pre-made/saved macros




## Usage
When enabled, the add-in records the resulting commands of actions that the user performs and collects them in the *AnyMacro* menu. If not stopped, the recording stops automatically after a number of commands, to avoid any performance degradation when the user is not setting up macros.

\* *Not all actions in Fusion 360™ result in "Commands" and some commands are not usable on their own. For example, **Pick Circle/Arc Tangent** does not generate a "Command" and **Roll History Marker Here** is triggered when clicking rewind in the history, but rewind actually first selects an item and then rolls.*

![Screenshot](tracking_screenshot.png)

### -Creating Macros
* Click ***Start recording*** and then launch a series of commands in the order you desire for your macro.
* If the commands you chose are able to be recorded, they will be added underneath the record command in the ***Command Recorder*** dropdown at the top of the *AnyMacro* panel.
* Should you desire to remove a command, you need just click its name within the dropdown.
* Once you stop recording, two new options: ***Save Macro*** and ***Reset Recording***; should appear just under the record command along with a test macro at the bottom of the list. The test macro allows you to make sure everything works before you save it and see the changes you make to the command list.
* Finally, once you are satisfied with the macro, hit the *Save Macro* button. This will display a prompt that will ask you to name your macro. There are few restrictions on the name, however, make sure there are *some* numbers or letters as its ID will be created using the `str.isidentifier()` method for each character.
* You should now find your command under the *Custom Macros* dropdown. You can run, assign a key-combination, and delete it right from the menu. Additionaly, the macro is persistant, meaning it will remain between sessions of fusion360 and only needs to be created once.

### -Removing Macros
* Navigate to its location under the *Custom Macros* dropdown
* Select the remove option under the macro. 
* A prompt will appear asking if you are sure you wish to remove it.
* Hit `OK` and the macro is now gone.

### -Creating Macros From API   (***`EXPEREMENTAL`***)
* Create a dictionary representing your macro object.
* Set its key: *`name`* to the desired name for the macro.
* Set its key: *`id`* to the desired id. (Must be "`A-z|0-9|_`", no spaces!)
* Set its key: *`executeList`* to a list of command-id's to execute in the same order.
* Use `json.dumps` from the `Json` module to convert it into a string.
* Use `Application.fireCustomEvent()` with the id "`AnyMacro_Add_Macro`"
* Pass in your macro string for the `additionalInfo` argument.
* Check to make sure your macro is visible under the `Custom Macros` dropdown

#### Example of creating a Macro via the API:
	TestMacro = dict(
		name='Test Macro', 
		id='TestMacroId',
		executeList=['SketchCreate',]
	)
	Application.fireCustomEvent('AnyMacro_Add_Macro', json.dumps(TestMacro))

## Built-in Objects
The ***AnyMacro*** add-in includes two built-in commands that are used in the built-in macro *'`Align Camera`'*. These commands can be found under the menu item *`TOOLS`* -> *`INSPECT`*. The macro demonstrates how these two commands can be chained.

Built-in commands include:
 * Change Cameras Up
 * Change Cameras Forwards

Built-in macros include:
 * Align Camera

### Images:

![Screenshot](builtin_macro_screenshot.png) 

![Screenshot](builtin_commands_screenshot.png)

\* The icons for the built-in commands are just placeholders

## Supported Platforms
  * Windows
  * Mac OS

## Installation
1. Download the add-in from the [Releases](https://github.com/zxynine/AnyMacro/releases) page.
2. Unpack it into `API\AddIns` (see [How to install an add-in or script in Fusion 360](https://knowledge.autodesk.com/support/fusion-360/troubleshooting/caas/sfdcarticles/sfdcarticles/How-to-install-an-ADD-IN-and-Script-in-Fusion-360.html)).
3. Make sure the directory is named `AnyMacro`, with no suffix.
4. The new menu *`TOOLS`* -> *`ANYMACRO`* is now available.

The add-in can be temporarily disabled using the *Scripts and Add-ins* dialog. Press *`Shift+S`* in Fusion 360™ and go to the *Add-Ins* tab.

## Reporting Issues
If you get any problems, please check out the section on [Fusion 360 quirks](##fusion-360-quirks).

If that does not apply to you, please report any issues that you find in the add-in on the [Issues](https://github.com/zxynine/AnyMacro/issues) page.

For better support, please include the steps you performed and the result. Also include copies of any error messages.

## Fusion 360 Quirks
Be aware of the following quirks in Fusion 360™.

* Fusion 360™ cannot handle all key combinations. Forget Alt+Left to rollback history, because fusion cannot save this combination and it will be broken next time you start the application.

* Menu items in sub-menus are not always clickable ([bug](https://forums.autodesk.com/t5/fusion-360-api-and-scripts/api-bug-cannot-click-menu-items-in-nested-dropdown/td-p/9669144)).

* The commands that change the camera may demonstrate some odd visual bugs due to fusions interpolation.

## Changelog
* v 1.0.1
  * Fixed bug with built-in camera command where the camera would break if an orthagonal forwards was selected. 
  * Fixed bug causing command queue to throw a silent error
  * Reduced excess code and added additional util functions
  * Added in a geometry library to the code utilities
* v 1.0.0
  * Original Implementation 

## Author
This add-in is created by [ZXYNINE](https://github.com/Zxynine) and is based off of Thomas Axelsson's [AnyShortcut](https://github.com/thomasa88/AnyShortcut).

## License
This project is licensed under the terms of the MIT license. See [LICENSE](LICENSE).

## More Fusion 360™ Add-ins
[My Fusion 360™ app store page](https://apps.autodesk.com/en/Publisher/PublisherHomepage?ID=EFHWLR46R29G)

[All my add-ins on Github](https://github.com/Zxynine?tab=repositories)
