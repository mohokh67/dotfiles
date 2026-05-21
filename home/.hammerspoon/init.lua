-- Define our default modifier keys
local hyper = { "cmd", "alt", "ctrl" }
local hyperShift = { "cmd", "alt", "ctrl", "shift" }


-- Format: {"App Name", window title, screen, unit rect (x, y, width, height)}
local devWorkspace = {
    { "WezTerm",       nil, nil, { x = 0, y = 0, w = 0.45, h = 0.9 } },        -- Left half
    { "Brave Browser", nil, nil, { x = 0.55, y = 0, w = 0.45, h = 0.9 } },     -- Right half
    { "Signal",        nil, nil, { x = 0.35, y = 0.65, w = 0.35, h = 0.35 } }, -- Bottom Centre
    { "Zed",           nil, nil, { x = 0.35, y = 0, w = 0.5, h = 0.7 } }       -- Top Centre
}

-- 2. Bind it to a hotkey (e.g., Command + Option + Control + W)
hs.hotkey.bind(hyper, "1", function()
    -- Launch the apps (or focus them if they are already running)
    hs.application.launchOrFocus("WezTerm")
    hs.application.launchOrFocus("Brave Browser")
    hs.application.launchOrFocus("Signal")
    hs.application.launchOrFocus("Zed")

    -- Wait 1 second for the apps to open/load, then apply the layout
    hs.timer.doAfter(0.5, function()
        hs.layout.apply(devWorkspace)
    end)
end)

-- =====================================================================
-- FEATURE 5: LIVE CONFIG RELOADER
-- =====================================================================
-- Watches your configuration directory. The second you save changes to this file,
-- Hammerspoon resets itself, wipes out the old memory leaks, and loads your updates.

function reload_config(files)
    hs.reload() -- Resets Hammerspoon entirely
end

-- Watches the exact directory paths for edits
hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reload_config):start()

-- Displays a native macOS banner notification indicating a successful build/load
hs.alert.show("Config loaded")


-- =====================================================================
-- 4. MONITOR DETECTION (Desk Docking)
-- =====================================================================
-- Automatically re-arranges your apps when you plug in an external monitor

monitorWatcher = hs.screen.watcher.new(function()
    local screens = #hs.screen.allScreens()
    if screens > 1 then
        hs.alert.show("🖥️ External Monitor Connected!")
        -- You could trigger a specific layout here, e.g.:
        -- hs.layout.apply(dockedWorkspace)
    else
        hs.alert.show("💻 Laptop Only Mode")
        -- Trigger laptop-only layout here
    end
end)
monitorWatcher:start()


-- Instantly move the focused window to the next screen, keeping its relative size
hs.hotkey.bind(hyper, "N", function()
    local win = hs.window.focusedWindow()
    if not win then return end

    local currentScreen = win:screen()
    local nextScreen = currentScreen:next()

    -- Throw the window to the new screen
    win:moveToScreen(nextScreen)
end)

-- 5. MULTI-MONITOR MANAGMENT
hs.hotkey.bind(hyper, 'N', hs.grid.pushWindowNextScreen) -- Mash + N: Throw window to next screen
hs.hotkey.bind(hyper, 'P', hs.grid.pushWindowPrevScreen) -- Mash + P: Throw window to previous screen
