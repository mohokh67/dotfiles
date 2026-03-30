-- Pull in the wezterm API
local wezterm = require 'wezterm'

-- This will hold the configuration.
local config = wezterm.config_builder()

-- This is where you actually apply your config choices.

-- For example, changing the initial geometry for new windows:
config.initial_cols = 120
config.initial_rows = 28

-- or, changing the font size and color scheme.
config.font_size = 17
config.line_height = 1.2

-- config.color_scheme = 'catppuccin-latte'
-- config.color_scheme = 'catppuccin-Mocha'
config.color_scheme = 'catppuccin-frappe'
-- config.color_scheme = 'catppuccin-macchiato'

config.font = wezterm.font 'JetBrainsMono Nerd Font'


config.colors = {
    cursor_bg = '#7aa2f7',
    cursor_border = '#7aa2f7',
    -- This sets the color of the divider lines between split panes
    split = '#7aa2f7', -- Change this to any hex color you like (e.g., Magenta)
}


-- Optional: Make the inactive panes slightly dimmer to help the active one stand out
config.inactive_pane_hsb = {
    saturation = 1,
    brightness = 0.7,
}

config.window_padding = {
    left = 13,
    right = 2,
    top = 2,
    bottom = 13,
}
config.window_background_opacity = 0.96
config.macos_window_background_blur = 23

-- config.window_decorations = 'RESIZE'

config.keys = {
    { key = 'w',          mods = 'CMD',       action = wezterm.action.CloseCurrentPane { confirm = false }, },
    { key = 'd',          mods = 'CMD',       action = wezterm.action.SplitHorizontal { domain = 'CurrentPaneDomain' }, },
    { key = 'd',          mods = 'CMD|SHIFT', action = wezterm.action.SplitVertical { domain = 'CurrentPaneDomain' }, },
    { key = 'k',          mods = 'CMD',       action = wezterm.action.SendString 'clear\n', },
    -- Move between panes using CMD + Arrow Keys
    { key = 'LeftArrow',  mods = 'CMD',       action = wezterm.action.ActivatePaneDirection 'Left' },
    { key = 'RightArrow', mods = 'CMD',       action = wezterm.action.ActivatePaneDirection 'Right' },
    { key = 'UpArrow',    mods = 'CMD',       action = wezterm.action.ActivatePaneDirection 'Up' },
    { key = 'DownArrow',  mods = 'CMD',       action = wezterm.action.ActivatePaneDirection 'Down' },

    -- Move between panes using CMD + hjkl (Vim style)
    { key = 'h',          mods = 'CMD',       action = wezterm.action.ActivatePaneDirection 'Left' },
    { key = 'l',          mods = 'CMD',       action = wezterm.action.ActivatePaneDirection 'Right' },
    { key = 'k',          mods = 'CMD',       action = wezterm.action.ActivatePaneDirection 'Up' },
    { key = 'j',          mods = 'CMD',       action = wezterm.action.ActivatePaneDirection 'Down' },

    -- QUICK NAVIGATION (Leader, then number)
    { key = '1',          mods = 'CMD',       action = wezterm.action.ActivateTab(0) },
    { key = '2',          mods = 'CMD',       action = wezterm.action.ActivateTab(1) },
    { key = '3',          mods = 'CMD',       action = wezterm.action.ActivateTab(2) },
}




-- Finally, return the configuration to wezterm:
return config
