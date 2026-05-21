-- =====================================================================
-- MODULE IMPORTS
-- =====================================================================
-- These lines pull in Hammerspoon's built-in systems (APIs) so the script can use them.
local application = require "hs.application" -- Manages opening/switching apps
local fnutils = require "hs.fnutils"         -- Functional utility helpers (like loops)
local grid = require "hs.grid"               -- The grid-based window management engine
local hotkey = require "hs.hotkey"           -- Listens for your custom keyboard shortcuts
local mjomatic = require "hs.mjomatic"       -- Extension module (not explicitly used here)
local window = require "hs.window"           -- Manages window metadata (size, position, id)

-- =====================================================================
-- GLOBAL GRID CONFIGURATION
-- =====================================================================
-- Sets up an invisible 13-row by 13-column grid across your screen.
grid.MARGINX = 0     -- No horizontal gaps between windows when tiled
grid.MARGINY = 0     -- No vertical gaps between windows when tiled
grid.GRIDHEIGHT = 13 -- Screen is split into 13 vertical segments
grid.GRIDWIDTH = 13  -- Screen is split into 13 horizontal segments

-- =====================================================================
-- SHORTCUT MODIFIER MASKS
-- =====================================================================
local mash = { "cmd", "alt", "ctrl" }               -- Holds down Command + Option + Control
local mashshift = { "cmd", "alt", "ctrl", "shift" } -- Holds down Command + Option + Control + Shift


-- =====================================================================
-- FEATURE 1: CAFFEINE (Anti-Sleep Toggle)
-- =====================================================================
-- Creates a small icon in your Mac menu bar to prevent your screen from sleeping.
local caffeine = hs.menubar.new()

-- Updates the menu bar icon based on whether anti-sleep is ON or OFF
function setCaffeineDisplay(state)
    local result
    if state then
        result = caffeine:setIcon("caffeine-on.pdf")  -- Shows filled coffee cup icon
    else
        result = caffeine:setIcon("caffeine-off.pdf") -- Shows empty coffee cup icon
    end
end

-- Triggers when you click the menu bar item or use the hotkey
function caffeineClicked()
    -- Toggles the Mac's "displayIdle" sleep prevention flag and updates the icon
    setCaffeineDisplay(hs.caffeinate.toggle("displayIdle"))
end

-- Initialization: If the menu bar icon successfully loads, set its initial icon state
if caffeine then
    caffeine:setClickCallback(caffeineClicked)           -- Makes the icon clickable
    setCaffeineDisplay(hs.caffeinate.get("displayIdle")) -- Matches icon to current system state
end

-- Shortcut: Press Command + Option + Control + Forward Slash (/) to toggle sleep prevention
hs.hotkey.bind(mash, "/", function() caffeineClicked() end)


-- =====================================================================
-- FEATURE 2: EDGE PEEK / WINDOW HIDING
-- =====================================================================
-- A custom system to throw a window mostly off-screen to clear clutter,
-- and bring it right back to its original spot when triggered again.

-- A key-value dictionary to remember the original dimensions of hidden windows
local origWindowPos = {}

-- Cleanup helper: Erases a window's saved position when it is restored or closed
local function cleanupWindowPos(_, _, _, id)
    origWindowPos[id] = nil
end

-- The core engine that pushes windows off-screen or pulls them back
local function movewin(direction)
    local win = hs.window.focusedWindow()
    if not win then return end
    local res = hs.screen.mainScreen():frame() -- Gets your screen's width and height
    local id = win:id()                        -- Unique hardware ID of the active window

    if not origWindowPos[id] then
        -- STEP A: IF THE WINDOW IS NOT HIDDEN YET -> HIDE IT
        local f = win:frame()
        origWindowPos[id] = win:frame() -- Save its current location to memory

        -- Watch the window. If the user closes it while it's hidden, clear its memory footprint
        local watcher = win:newWatcher(cleanupWindowPos, id)
        watcher:start({ hs.uielement.watcher.elementDestroyed })

        -- Math to move the window entirely off-screen, leaving just a 10-pixel edge visible
        if direction == "left" then f.x = (res.w - (res.w * 2)) + 10 end -- Push past left boundary
        if direction == "right" then f.x = (res.w + res.w) - 10 end      -- Push past right boundary
        if direction == "down" then f.y = (res.h + res.h) - 10 end       -- Push past bottom boundary
        win:setFrame(f)
    else
        -- STEP B: IF THE WINDOW IS ALREADY HIDDEN -> RESTORE IT
        win:setFrame(origWindowPos[id]) -- Snap it back to its original shape/coordinates
        cleanupWindowPos(_, _, _, id)   -- Wipe its data from memory
    end
end

-- Hotkeys to slide windows out of the way
hs.hotkey.bind(mash, "A", function() movewin("left") end)  -- Mash + A: Hide Left
hs.hotkey.bind(mash, "D", function() movewin("right") end) -- Mash + D: Hide Right
hs.hotkey.bind(mash, "S", function() movewin("down") end)  -- Mash + S: Hide Down


-- =====================================================================
-- FEATURE 3: INSTANT APP SWITCHERS
-- =====================================================================
-- Helper functions to open or pull focus to specific development applications.
local function openBrave()
    application.launchOrFocus("Brave Browser")
end

-- Bindings for instant access
hotkey.bind(mash, 'B', openBrave) -- Mash + B: Jump to Brave



-- =====================================================================
-- FEATURE 4: GRID WINDOW MANAGEMENT
-- =====================================================================

-- 1. ADJUSITING GRID REOSLUTION ON THE FLY
-- Lets you dynamically expand or contract the 13x13 grid sizes globally
hotkey.bind(mashshift, '=', function() grid.adjustHeight(1) end)  -- Mash + Shift + = : Add rows
hotkey.bind(mashshift, '-', function() grid.adjustHeight(-1) end) -- Mash + Shift + - : Remove rows
hotkey.bind(mash, '=', function() grid.adjustWidth(1) end)        -- Mash + = : Add columns
hotkey.bind(mash, '-', function() grid.adjustWidth(-1) end)       -- Mash + - : Remove columns

-- 2. SNAP CURRENT WINDOWS TO GRID
hotkey.bind(mash, ';', function() grid.snap(window.focusedWindow()) end)               -- Force current window to match nearest grid lines
hotkey.bind(mash, "'", function() fnutils.map(window.visibleWindows(), grid.snap) end) -- Loop through and snap ALL visible windows at once

-- 3. INTERACTIVE WINDOW MOVEMENT (Pushing windows around the grid layout)
hotkey.bind(mash, 'DOWN', grid.pushWindowDown)   -- Mash + Down Arrow: Shift window down 1 block
hotkey.bind(mash, 'UP', grid.pushWindowUp)       -- Mash + Up Arrow: Shift window up 1 block
hotkey.bind(mash, 'LEFT', grid.pushWindowLeft)   -- Mash + Left Arrow: Shift window left 1 block
hotkey.bind(mash, 'RIGHT', grid.pushWindowRight) -- Mash + Right Arrow: Shift window right 1 block

-- 4. INTERACTIVE WINDOW RESIZING (Stretching or shrinking window edges)
hotkey.bind(mashshift, 'UP', grid.resizeWindowShorter)   -- Mash + Shift + Up Arrow: Pull bottom edge up
hotkey.bind(mashshift, 'DOWN', grid.resizeWindowTaller)  -- Mash + Shift + Down Arrow: Push bottom edge down
hotkey.bind(mashshift, 'RIGHT', grid.resizeWindowWider)  -- Mash + Shift + Right Arrow: Push right edge out
hotkey.bind(mashshift, 'LEFT', grid.resizeWindowThinner) -- Mash + Shift + Left Arrow: Pull right edge in

-- 5. MULTI-MONITOR MANAGMENT
hotkey.bind(mash, 'N', grid.pushWindowNextScreen) -- Mash + N: Throw window to next screen
hotkey.bind(mash, 'P', grid.pushWindowPrevScreen) -- Mash + P: Throw window to previous screen


-- =====================================================================
-- FEATURE 5: LIVE CONFIG RELOADER
-- =====================================================================
-- Watches your configuration directory. The second you save changes to this file,
-- Hammerspoon resets itself, wipes out the old memory leaks, and loads your updates.

function reload_config(files)
    caffeine:delete() -- Destroys old menu bar icon instance to prevent duplicates in system tray
    hs.reload()       -- Resets Hammerspoon entirely
end

-- Watches the exact directory paths for edits
hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reload_config):start()

-- Displays a native macOS banner notification indicating a successful build/load
hs.alert.show("Config loaded")



-- ==============================Another useful set of config
--
-- =====================================================================
-- 1. WINDOW TILING (Basic Halves and Fullscreen)
-- =====================================================================
-- Pushes the currently focused window to different halves of the screen
-- Left half:  Hyper + Left Arrow
-- Right half: Hyper + Right Arrow
-- Fullscreen: Hyper + Up Arrow

hs.hotkey.bind(hyper, "left", function()
    local win = hs.window.focusedWindow()
    local f = win:frame()
    local screen = win:screen()
    local max = screen:frame()

    f.x = max.x
    f.y = max.y
    f.w = max.w / 2
    f.h = max.h
    win:setFrame(f)
end)

hs.hotkey.bind(hyper, "right", function()
    local win = hs.window.focusedWindow()
    local f = win:frame()
    local screen = win:screen()
    local max = screen:frame()

    f.x = max.x + (max.w / 2)
    f.y = max.y
    f.w = max.w / 2
    f.h = max.h
    win:setFrame(f)
end)

hs.hotkey.bind(hyper, "up", function()
    hs.window.focusedWindow():maximize()
end)


-- =====================================================================
-- 2. INSTANT APP SWITCHERS (Hyper-Launchers)
-- =====================================================================
-- Instead of Cmd+Tabbing, press Hyper + a letter to instantly jump to an app.
-- If it's closed, it opens. If it's open, it comes to the front.

hs.hotkey.bind(hyper, "B", function() hs.application.launchOrFocus("Brave Browser") end)
hs.hotkey.bind(hyper, "T", function() hs.application.launchOrFocus("WezTerm") end)


-- =====================================================================
-- 3. SYSTEM AUTOMATIONS (Battery & WiFi)
-- =====================================================================

-- Notify when battery is low
-- This runs in the background and checks every time the battery state changes
batteryWatcher = hs.battery.watcher.new(function()
    if hs.battery.isCharging() == false and hs.battery.percentage() < 15 then
        hs.alert.show("⚠️ Battery is below 15%! Plug in your Mac.")
    end
end)
batteryWatcher:start()

-- Auto-mute volume when connecting to a specific WiFi (e.g., Office)
wifiWatcher = hs.wifi.watcher.new(function()
    local currentNetwork = hs.wifi.currentNetwork()
    -- Change "OfficeWiFi" to the actual name of your work network
    if currentNetwork == "OfficeWiFi" then
        hs.audiodevice.defaultOutputDevice():setVolume(0)
        hs.alert.show("🔇 Arrived at work. System muted.")
    end
end)
wifiWatcher:start()

-- =====================================================================
-- 7. SPOONS (Pre-built Plugins)
-- =====================================================================
-- To use these, download the .zip from the links provided below,
-- unzip them, and double-click the .spoon file to install.

-- CAFFEINE: Prevents your Mac from going to sleep. Adds a coffee cup to the menu bar.
-- Download: https://github.com/Hammerspoon/Spoons/raw/master/Spoons/Caffeine.spoon.zip
-- hs.loadSpoon("Caffeine")
-- spoon.Caffeine:start() -- Automatically starts the menubar icon

-- ACLOCK: Displays a giant clock on the screen (Great for presentations or breaks)
-- Download: https://github.com/Hammerspoon/Spoons/raw/master/Spoons/AClock.spoon.zip
-- hs.loadSpoon("AClock")
-- hs.hotkey.bind(hyper, "T", function()
--     spoon.AClock:toggleShow()
-- end)

-- ------------------------------------------------------------------

-- https://github.com/miromannino/miro-windows-manager
hs.loadSpoon("MiroWindowsManager")

hs.window.animationDuration = 0.3
spoon.MiroWindowsManager:bindHotkeys({
    up = { hyper, "up" },
    right = { hyper, "right" },
    down = { hyper, "down" },
    left = { hyper, "left" },
    fullscreen = { hyper, "f" },
    nextscreen = { hyper, "n" }
})
-- ------------------------------------------------------------------
